import requests
import os
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
from datetime import datetime


def get_urls(date):
    
    data_inicial = date
    data_inicial_obj = datetime.strptime(data_inicial, "%d/%m/%Y")
    ano_inicial = data_inicial_obj.year
    mes_inicial = data_inicial_obj.month
    dia_inicial = data_inicial_obj.day
    dia_inicial_str = str(dia_inicial).zfill(2)
    mes_inicial_str = str(mes_inicial).zfill(2)
    ano_inicial_str = str(ano_inicial)

    url = f"https://www.in.gov.br/leiturajornal?data={dia_inicial_str}-{mes_inicial_str}-{ano_inicial_str}&secao=do3&org=Ministério%20da%20Defesa&org_sub=Comando%20da%20Aeronáutica"

    #print(url)

    # Fazer a solicitação HTTP com o proxy configurado através das variáveis de ambiente
    response = requests.post(url, verify=False)

    # Verificar se há resultados ou não
    soup = BeautifulSoup(response.text, 'html.parser')

    # Formatar o HTML
    formatted_html = soup.prettify()

    # Escrever o HTML formatado em um arquivo
    with open('output.html', 'w', encoding='utf-8') as file:
        file.write(formatted_html)


    # Extrai os dados do JSON
    script_tag = soup.find('script', id='params')
    json_data = json.loads(script_tag.string)

    # Define the filter value for the second position in hierarchyList
    filter_value = 'Comando da Aeronáutica'

    # Filtra e organiza os dados do JASON
    organized_data = []

    for item in json_data['jsonArray']:
        hierarchy_list = item.get('hierarchyList', [])
        if len(hierarchy_list) >= 2 and hierarchy_list[1] == filter_value:
            filtered_item = {
                'pubName': item.get('pubName'),
                'urlTitle': item.get('urlTitle'),
                'numberPage': item.get('numberPage'),
                'subTitulo': item.get('subTitulo'),
                'titulo': item.get('titulo'),
                'title': item.get('title'),
                'pubDate': item.get('pubDate'),
                'content': item.get('content'),
                'editionNumber': item.get('editionNumber'),
                'artType': item.get('artType'),
                'hierarchyList': hierarchy_list[:2]  # Keep only the first two positions
            }
            organized_data.append(filtered_item)

    # Salva os dados organizados em um arquivo JSON
    with open('organized_data.json', 'w', encoding='utf-8') as f:
        json.dump(organized_data, f, ensure_ascii=False, indent=4)

    # Preparando a saída com apenas os títulos das urls
    url_titles = []

    for item in json_data['jsonArray']:
        hierarchy_list = item.get('hierarchyList', [])
        if len(hierarchy_list) >= 2 and hierarchy_list[1] == filter_value:
            url_titles.append(item.get('urlTitle'))

    #print(url_titles)
    #print(len(url_titles))

    # Remover arquivos temporários
    try:
        os.remove("output.html")
        os.remove("organized_data.json")
        print("Arquivos temporários removidos com sucesso.")
    except Exception as e:
        print(f"Erro ao remover arquivos temporários: {e}")

    return (url_titles)

def get_pub_content(url):

    url = f"https://www.in.gov.br/web/dou/-/{url}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }

   
    # Fazer a solicitação HTTP com o proxy configurado através das variáveis de ambiente
    response = requests.post(url, headers=headers, verify=False)

    print(response.status_code)
    print(response.text[:500])  # Exibe os primeiros 500 caracteres da resposta

    # Verificar se há resultados ou não
    soup = BeautifulSoup(response.text, 'html.parser')

    # Formatar o HTML
    formatted_html = soup.prettify()

    # Escrever o HTML formatado em um arquivo
    with open('output_pub.html', 'w', encoding='utf-8') as file:
        file.write(formatted_html)

    # Encontra as divs com class "texto-dou"
    texto_dou_div = soup.find('div', class_='texto-dou')

    # Extrai o conteúdo de todas as tags <p> dentro da div "texto-dou"
    p_tags = texto_dou_div.find_all('p')

    # Concatena o conteúdo de todas as tags <p> em uma string simples
    texto_dou_content = '\n'.join([p.get_text(strip=True) for p in p_tags])

    # Encontra as spans com class "orgao-dou-data"
    texto_dou_div = soup.find('span', class_='orgao-dou-data')

    # Extrai o conteúdo do último órgão
    orgao = texto_dou_div.get_text(strip=True)
    orgao = orgao.split('/')[-1].strip()
    
    # Encontra a tag "title"
    texto_dou_title = soup.find('title')
    titulo = texto_dou_title.get_text(strip=True)

    # Remover o arquivo temporário
    try:
        os.remove("output_pub.html")
        print("Arquivo output_pub.html removido com sucesso.")
    except Exception as e:
        print(f"Erro ao remover output_pub.html: {e}")
    
    return texto_dou_content, orgao, titulo


def edc(date):  

    # Aciona a função que vai listas as urls das publicações do dia
    urls = get_urls(date)

    # Aciona a função que extrai o conteúdo da publicação
    pub_cont = []
    
    for url in tqdm(urls):
        conteudo = get_pub_content(url) # O conteúdo da publicação é salvo no índice 0, o órgão é salvo no índice 1 e o título (tipo) no 2
        #link = f"https://www.in.gov.br/web/dou/-/{url}"
        link = f'<a href="https://www.in.gov.br/web/dou/-/{url}">Publicação</a>'
        conteudo = conteudo + (link,) # A url é incluída na posição 3 da lista
        pub_cont.append(conteudo)
        
    return pub_cont

#edc()
