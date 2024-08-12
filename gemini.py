import os
import google.generativeai as genai

# Gemma 2: https://www.kaggle.com/models/google/gemma-2/pyTorch/gemma-2-2b-pt
# Tutorial: https://ai.google.dev/gemini-api/docs/get-started/tutorial?lang=python&hl=pt-br


def gemini(proxy, api_gemini, content, descricao):

    usuario = proxy[0]    
    senha = proxy[1]
    adress = proxy[2]

    os.environ['HTTP_PROXY'] = f'http://{usuario}:{senha}@{adress}'
    os.environ['HTTPS_PROXY'] = f'http://{usuario}:{senha}@{adress}'

    genai.configure(api_key=api_gemini) #DADO SENSÍVEL

    prompt = f"{content} /n O texto acima, doravante denominado 'conteúdo' trata do seguinte 'objeto': {descricao} ? Responda em duas linhas. A primeira linha deve ser 'SIM' ou 'NÃO'. A segunda linha deve ser uma contextualização. O órgão que realizou a publicação do 'conteúdo' foi diferente daquele que nomeou o 'objeto', portanto, pode haver pequenas divergências entre eles. Caso o o tópico tratado 'conteúdo' seja minimamente parecido com o 'objeto', responda que sim. Note que eventualmente pode haver siglas em um e no outro não. Rescisões de contrato, aplicação de penalidades e termos aditivos não me interessam, logo, nesses casos a resposta deverá ser 'NÃO'."
    
    """for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)"""

    model = genai.GenerativeModel('gemini-1.5-flash')

    response = model.generate_content(prompt)

    resposta = response.text.splitlines()
    veredicto = resposta[0]
    justificativa = resposta[len(resposta)-1]

    prompt = f"{content} /n Qual o objeto de que trata o excerto acima? Por favor, responda no padrão: 'Objeto: [objeto]'. Desconsiderar palavras como 'aquisição de', contratação de empresa para' e afins, ou seja, foque no objeto de fato."

    response = model.generate_content(prompt)
    
    objeto = response.text
    
    return (veredicto, justificativa, objeto)