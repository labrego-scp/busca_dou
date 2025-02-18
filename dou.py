import urllib.parse
import time
import sys
import os
import warnings
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from dotenv import load_dotenv
from tqdm import tqdm
from extrair_dou_comaer import edc
from gemini import gemini2
from helpers import calcular_ratio, enviar_email, gerar_pdf


# Oculta os warnings
warnings.filterwarnings("ignore")

# Inicializa o contador de tempo
start_time = time.time()

# Inicialzia o conteúdo da saída HTML
conteudo_html = "<meta charset='UTF-8'>"

######### COLETA DOS DADOS DO PROXY E DO .ENV #########

# Carregar variáveis do .env
load_dotenv()
api_gemini = os.getenv('GEMINI_KEY')
cred_google = os.getenv('GSHEET_CRED')
url_sheet = os.getenv('GSHEET_KEY_SHEET')

# Proxy
usuario = os.getenv('USUARIO_PROXY')
senha_bruta = os.getenv('PASS_PROXY')
senha = urllib.parse.quote(senha_bruta, safe='')
adress = os.getenv('ENDERECO_PROXY')
proxy = [usuario, senha, adress]

######### COLETA DOS DADOS DAS PUBLICAÇÕES DO DIA #########

# Define a data
date = datetime.now().strftime('%d/%m/%Y')
#date = "31/01/2025"

print("Inicializando a coleta dos dados no DOU")
try:
    pub_cont = edc(proxy, date) # São criados n itens na lista pub_cont, onde n é o número de publicações naquela data. Cada lista é composta por uma lista com duas posições. A posição 0 corresponde ao conteúdo da publicação, o índice 1 corresponde ao órgão, o índice 2 corresponde ao tipo e o 3 ao link.
except Exception as e:
    if "proxy" in str(e):
        print("Erro: reveja as credenciais do proxy!")
    else:
        print(f"Erro: {e}")
    sys.exit(1)
print("Finalizada a coleta dos dados no DOU")

publicacoes = dict()
content = []
orgao = []
tipo = []
link = []

for pub in tqdm(pub_cont):
    content.append(pub[0])
    orgao.append(pub[1])
    tipo.append(pub[2])
    link.append(pub[3])

publicacoes['content'] = content
publicacoes['orgao'] = orgao
publicacoes['tipo'] = tipo
publicacoes['link'] = link
  

######### LISTAGEM DAS OBRAS E SERV. ENG. NO DOU #########
while True:
    while True:
        try:
            analise_obra = gemini2(proxy, api_gemini, content)
            analise_obra_list = analise_obra.split("###")
            if analise_obra_list[-1] == "\n":
                analise_obra_list = analise_obra_list[:-1]
            print(analise_obra_list)
            
            #analise_obra_list = [item for item in analise_obra_list if item != "" and item != "\n"]
        except Exception as e:
            print(f"Erro ao processar conteúdo: {e}")

        parecer_obra = []

        for analise in analise_obra_list:
            # Usa splitlines() para dividir as linhas e filtra as linhas vazias
            temp = [linha for linha in analise.splitlines() if linha.strip()]
            parecer_obra.append(temp)

        # Filtra os valores vazios
        parecer_obra = [sublista for sublista in parecer_obra if sublista]

        print(f"Analise da IA: {len(parecer_obra)}")
        print(f"DOU: {len(orgao)}")

        # Verifica se o tamanho do resultado da IA bate com o
        if len(parecer_obra) == len(orgao):
            break
        # Aguardar antes de fazer a próxima solicitação
        print("Fazendo novamente...")
        time.sleep(10)

    try:
        #saida_obra = pd.DataFrame(parecer_obra, columns=["Veredicto_AI", "Justificativa", "Objeto"])
        saida_obra = pd.DataFrame(parecer_obra, columns=["Veredicto_AI", "Justificativa", "Objeto"])
        saida_obra['Órgão'] = orgao
        saida_obra['Tipo'] = tipo
        saida_obra['Link'] = link
        break
    except Exception as e:
        print(f"Erro ao processar conteúdo: {e}")

# Filtrar as linhas onde a similaridade do veredicto com "sim" é maior que 70
saida_obra["similaridade"] = saida_obra["Veredicto_AI"].apply(calcular_ratio)
condicao_obra = saida_obra["similaridade"] > 70
saida_obra = saida_obra.loc[condicao_obra]

saida_obra = saida_obra[['Objeto','Tipo','Órgão','Veredicto_AI','Justificativa','Link']]
saida_obra['Objeto'] = saida_obra['Objeto'].str.replace("Objeto: ", "", regex=False)
saida_obra['Objeto'] = saida_obra['Objeto'].str.replace("\n", "", regex=False)

conteudo_html += f"<br><br><h1>Obras e Serviços de Engenharia tratados no DOU</h1>\n"

# Gerar o HTML da tabela ou, para o caso de não ter respostas, criar um parágrafo dizendo que nada foi encontrado
if saida_obra.empty:
    tabela_html = "<p style='text-align: center;'>Não foram encontrados obras e serviços de engenharia</p>"
else:
    tabela_html = saida_obra.to_html(index=False, justify='center', border=1, classes='table table-striped', escape=False)

conteudo_html += f"<br>\n{tabela_html}\n<br><br>\n"


######### CRIAÇÃO DO PDF E ENVIO DO E-MAIL #########
# Ler o template HTML
with open('template_saida.html', 'r', encoding='utf-8') as file:
    html_template = file.read()
# Verifique se o conteúdo do template foi lido corretamente
if not html_template:
    print("O template HTML está vazio ou não foi lido corretamente.")
else:
    # Substituir os espaços reservados pelo título e pela tabela
    html_content = html_template.replace("{{conteudo}}", conteudo_html)
# Salvar o HTML em um arquivo no diretório com codificação utf-8
# Nome do arquivo PDF com a data atual
data_atual = datetime.now().strftime('%Y%m%d')
nome_arquivo = f"{data_atual}_busca_dou.html"
with open(nome_arquivo, 'w', encoding='utf-8') as file:
    file.write(html_content)

# Gerar o pdf
caminho_pdf = "saida.pdf"
gerar_pdf(conteudo_html, caminho_pdf)

# Enviar e-mail
conteudo = f"Prezados, \n\nO relatório de análise de inclusão de obras e serviços de engenharia no DOU ({date}) se encontra em anexo. \n\nRespeitosamente, ECCP"
assunto = f"Relatório diário - DOU - {date}"
enviar_email(proxy, conteudo, assunto, caminho_pdf)

# Remover arquivos temporários após o envio do e-mail
try:
    os.remove(nome_arquivo)  # Remove o arquivo HTML
    os.remove(caminho_pdf)  # Remove o arquivo PDF
    print("Arquivos temporários removidos com sucesso.")
except Exception as e:
    print(f"Erro ao remover arquivos temporários: {e}")

elapsed_time = time.time() - start_time
print(f"Tempo de execução: {elapsed_time} segundos")


