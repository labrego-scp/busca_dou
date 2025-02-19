import re
from fuzzywuzzy import fuzz
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import pdfkit

def limpar_strings(s):
    return re.sub(r'\W+', '',s).lower()

def normalizar_string(s):
    s = s.lower()
    s = re.sub(r'\W+', ' ', s)
    s = re.sub(r'\b(do|da|de|e|dos|das|a|o|as|os|em|no|na|nos|nas|ao|aos|à|às|até|com|como|entre|já|mais|menos|mas|não|nem|ou|para|pelo|pela|pelos|pelas|por|que|porque|quem|se|sem|só|objeto:)\b', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

# Função para calcular o ratio de similaridade
def calcular_ratio(veredicto):
    return fuzz.ratio(normalizar_string(veredicto), "sim")

# Função para enviar o e-mail
def enviar_email(conteudo, assunto, caminho_pdf):
    # Carrega variáveis de ambiente do arquivo .env
    load_dotenv()

    # Definições
    sender_email = os.getenv('SENDER_EMAIL')
    receiver_email = os.getenv('RECEIVER_EMAIL')
    receiver_email2 = os.getenv('RECEIVER_EMAIL2')
    receiver_email3 = os.getenv('RECEIVER_EMAIL3')
    password = os.getenv('EMAIL_PASSWORD')

    # Criando a mensagem de e-mail
    mensagem = MIMEMultipart("alternative")
    mensagem["Subject"] = assunto
    mensagem["From"] = sender_email
    mensagem["To"] = receiver_email + ',' + receiver_email2 + ',' + receiver_email3
    
    # Adicionando o conteúdo do e-mail
    parte_texto = MIMEText(conteudo, "plain")
    mensagem.attach(parte_texto)

    # Anexando o PDF
    try:
        with open(caminho_pdf, "rb") as anexo:
            # Cria um objeto MIMEBase
            parte_anexo = MIMEBase("application", "octet-stream")
            parte_anexo.set_payload(anexo.read())
        
        # Codifica o anexo em Base64
        encoders.encode_base64(parte_anexo)

        # Adiciona cabeçalhos ao anexo
        parte_anexo.add_header(
            "Content-Disposition",
            f"attachment; filename= {os.path.basename(caminho_pdf)}",
        )

        # Anexa o arquivo PDF à mensagem de e-mail
        mensagem.attach(parte_anexo)

    except Exception as e:
        print(f"Erro ao anexar o PDF: {e}")
        return

    try:
        # Enviando o e-mail
        #with smtplib.SMTP("smtp.mail.intraer", 587) as server:
        with smtplib.SMTP("smtp.fab.mil.br", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, mensagem.as_string())
            #server.sendmail(sender_email, receiver_email2, mensagem.as_string())
            #server.sendmail(sender_email, receiver_email3, mensagem.as_string())
        print("E-mail enviado com sucesso!")
    except smtplib.SMTPException as e:
        print(f"Falha ao enviar e-mail: {e}")
    except Exception as e:
        print(f"Erro inesperado ao enviar e-mail: {e}")


def gerar_pdf(conteudo_html, caminho_pdf):
    # Converte o HTML para PDF
    try:
        pdfkit.from_string(conteudo_html, caminho_pdf)
        print("PDF gerado com sucesso!")
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
