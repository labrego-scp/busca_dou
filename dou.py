import urllib.parse
import getpass
import time
import sys
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from tqdm import tqdm
from extrair_dou_comaer import edc
from gemini import gemini
from helpers import normalizar_string, calcular_ratio
from get_data_pw import get_data_pw

# Inicializa o contador de tempo
start_time = time.time()

# Inicialzia o conteúdo da saída HTML
conteudo_html = ""

######### COLETA DOS DADOS DO PROXY E DO .ENV #########

# Carregar variáveis do .env
load_dotenv()
api_gemini = os.getenv('GEMINI_KEY')
cred_google = os.getenv('GSHEET_CRED')
url_sheet = os.getenv('GSHEET_KEY_SHEET')

# Proxy
usuario = input("Usuário: ")
senha_bruta = getpass.getpass("Senha: ")
senha = urllib.parse.quote(senha_bruta, safe='')
adress = os.getenv('ENDERECO_PROXY')
proxy = [usuario, senha, adress]

######### COLETA DOS DADOS DAS PUBLICAÇÕES DO DIA #########

# Define a data
#date = "5/8/2024"
#date = "19/3/2024"
#date = "15/7/2024"
date = datetime.now().strftime('%d/%m/%Y')

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

######### BUSCA DOS LIAS E PRCS DO PLANINFRAWEB #########
try:
    lista_pw = get_data_pw(proxy, cred_google, url_sheet)
    #print (lista_pw.info())
except Exception as e:
    print(f"Erro: {e}")
    sys.exit(1)

######### DEFINIÇÃO DA DESCRIÇÕES DO PLANINFRAWEB #########

#descricao = "Adequação da sala segura de servidores do CCA-RJ"
#descricao = "Conectividade entre o CINDACTA IV e seus Destacamentos"
#descricoes = lista_pw["DESCRIÇÃO"].tolist()[14:]
descricoes = lista_pw["DESCRIÇÃO"].tolist()
#descricoes = []
#print(descricoes)
#descricao = input("Escreva a descrição do objeto: ")

for descricao in tqdm(descricoes):
    ######### ACIONAMENTO DA IA #########

    # Configurar o temporizador (segundos)
    intervalo_entre_solicitacoes = 10

    saida_ai = pd.DataFrame(columns=["Veredicto_AI", "Justificativa", "Objeto", "Órgão", "Tipo", "Link"])

    print("Inicializando a análise da IA")
    for pub in tqdm(pub_cont):
        content = pub[0]
        orgao = pub[1]
        tipo = pub[2]
        link = pub[3]
        try:
            analise = gemini(proxy, api_gemini, content, descricao)
            nova_linha = {"Veredicto_AI": analise[0], "Justificativa": analise[1], "Objeto": analise[2], "Órgão": orgao, "Tipo": tipo, "Link": link}
            saida_ai = pd.concat([saida_ai, pd.DataFrame([nova_linha])], ignore_index=True)
        except Exception as e:
            print(f"Erro ao processar conteúdo: {e}")
        # Aguardar antes de fazer a próxima solicitação
        time.sleep(intervalo_entre_solicitacoes)

    print("Finalizada a análise da IA")

    ######### APLICAÇÃO DA LÓGICA FUZZY #########

    score_corte = 45

    descricao_norm = normalizar_string(descricao)

    saida_ai["Score_fuzzy"] = [fuzz.ratio(descricao_norm, normalizar_string(x)) for x in saida_ai["Objeto"]]
    saida_ai["Veredicto_fuzzy"] = ["SIM" if fuzz.ratio(descricao_norm, normalizar_string(x)) > score_corte else "NÃO" for x in saida_ai["Objeto"]]

    print(saida_ai)

    ######### SAÍDA #########

    # Aplicar a função calcular_ratio à coluna 'Veredicto_AI' e criar uma nova coluna com os resultados
    saida_ai["similaridade_ai"] = saida_ai["Veredicto_AI"].apply(calcular_ratio)

    # Aplicar a função calcular_ratio à coluna 'Veredicto_fuzzy' e criar uma nova coluna com os resultados
    saida_ai["similaridade_fuzzy"] = saida_ai["Veredicto_fuzzy"].apply(calcular_ratio)

    # Filtrar as linhas onde a similaridade do veredicto com "sim" é maior que 70
    condicao_positiva_ai = saida_ai["similaridade_ai"] > 70
    condicao_positiva_fuzzy = saida_ai["similaridade_fuzzy"] > 70  

    #Saída para atendimento das duas condições (IA e fuzzy)
    saida = saida_ai.loc[condicao_positiva_ai | condicao_positiva_fuzzy]
    saida = saida[['Objeto','Tipo','Órgão','Veredicto_AI','Justificativa','Veredicto_fuzzy','Score_fuzzy','Link']]
    saida['Objeto'] = saida['Objeto'].str.replace("Objeto: ", "", regex=False)
    saida['Objeto'] = saida['Objeto'].str.replace("\n", "", regex=False)
    
    #if saida.empty:
    #    print("Não foram encontrados dados compatíveis com a descrição fornecida, de acordo com a IA e com a lógica de Levenshtein")
    #else:
    #    print(saida)

    # Gerar o HTML da tabela ou, para o caso de não ter respostas, criar um parágrafo dizendo que nada foi encontrado
    if saida.empty:
        tabela_html = "<p style='text-align: center;'>Não foram encontrados dados compatíveis com a descrição fornecida, de acordo com a IA e com a lógica de Levenshtein</p>"
    else:
        tabela_html = saida.to_html(index=False, justify='center', border=1, classes='table table-striped', escape=False)

    # Ler o template HTML
    with open('template_saida.html', 'r', encoding='utf-8') as file:
        html_template = file.read()

    conteudo_html += f"<h2>{descricao}</h2>\n{tabela_html}\n<br><br>\n"

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


elapsed_time = time.time() - start_time
print(f"Tempo de execução: {elapsed_time} segundos")