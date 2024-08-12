import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def get_data_pw(proxy, cred_google, url_sheet):

    # Configurações de proxy
    usuario = proxy[0]    
    senha = proxy[1]
    adress = proxy[2]

    os.environ['HTTP_PROXY'] = f'http://{usuario}:{senha}@{adress}'
    os.environ['HTTPS_PROXY'] = f'http://{usuario}:{senha}@{adress}'

    # Definir o escopo
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # Autenticar usando as credenciais da conta de serviço - DADO SENSÍVEL
    creds = ServiceAccountCredentials.from_json_keyfile_name(cred_google, scope)
    client = gspread.authorize(creds)

    # Abrir a planilha pelo nome
    # DADO SENSÍVEL
    spreadsheet = client.open_by_key(url_sheet)

    # Selecionar a folha de trabalho
    worksheet = spreadsheet.worksheet("ACD")  # ou use worksheet = spreadsheet.get_worksheet(0) para a primeira folha

    # Puxar os dados do intervalo específico
    data = worksheet.get('A2:AC')

    # Converter para DataFrame do pandas
    lista_pw = pd.DataFrame(data[1:], columns=data[0])  # Primeira linha como cabeçalho

    # Remover linhas onde todos os valores são NaN
    lista_pw = lista_pw.dropna(how='all')

    lista_pw = lista_pw[lista_pw['AUTORIZAÇÃO'] != 'Encerrado'] # Filtra os vigentes

    filtro_prc = lista_pw[lista_pw['Status'] == 'PRC'] # Filtra somente PRC

    filtro_lia = lista_pw[(lista_pw['Status'] == 'LIA') & (lista_pw['Origem do Crédito'] != 'CONVÊNIO - SEDOP')] # Filtra somente LIA e exclui licitação pelo GOverno do PA 

    

    lista_pw_filtr = filtro_lia

    #lista_pw_filtr = pd.concat([lista_pw_filtr, filtro_prc], ignore_index=True)

    lista_pw_filtr = lista_pw_filtr[['ID Planinfra','DESCRIÇÃO','Status']]

    return lista_pw_filtr



