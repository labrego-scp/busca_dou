import os
import google.generativeai as genai

# Gemma 2: https://www.kaggle.com/models/google/gemma-2/pyTorch/gemma-2-2b-pt
# Tutorial: https://ai.google.dev/gemini-api/docs/get-started/tutorial?lang=python&hl=pt-br



def gemini2(proxy, api_gemini, content):

    usuario = proxy[0]    
    senha = proxy[1]
    adress = proxy[2]

    os.environ['HTTP_PROXY'] = f'http://{usuario}:{senha}@{adress}'
    os.environ['HTTPS_PROXY'] = f'http://{usuario}:{senha}@{adress}'

    genai.configure(api_key=api_gemini) #DADO SENSÍVEL

    clause = []
    clause.append(f"{content}\nCada item da lista acima será doravante denominado 'conteúdo'.")
    clause.append("Responda, para cada conteúdo, em APENAS três linhas.")
    clause.append("A primeira linha deve responder a pergunta: o conteúdo se refere a uma obra ou a um serviço de engenharia, conforme Lei 14.133/2021 (obra, reforma, manutenção, construção, substituição, adaptação, reparo, adequação, etc.)? A resposta deve ser apenas 'SIM' ou 'NÃO', sem rodeios.")
    clause.append("A segunda linha deve ser uma contextualização que justifique a primeira linha.")
    clause.append("A terceira linha deve ser o assunto resumido do conteúdo, no padrão: 'Objeto: [assunto]'. ")
    clause.append("Desconsiderar palavras como 'aquisição de', contratação de empresa para' e afins, ou seja, foque no objeto de fato.")
    clause.append("As respostas de cada conteúdo devem ser separadas por '###'")
    clause.append("Logo, a tua resposta final deve seguir o padrão:")
    clause.append("'SIM (ou NÃO)'\n'[Justificativa 1]'\n'Objeto: [assunto 1]###")
    clause.append("'SIM (ou NÃO)'\n'[Justificativa 2]'\n'Objeto: [assunto 2]###")
    clause.append("... E assim por diante")

    prompt = "\n".join(clause)
    #print(prompt)
    
    #prompt = f"{content} /n Cada item da lista acima será doravante denominado 'conteúdo'. Avalie se cada conteúdo se trata de obra ou serviço de engenharia./n Responda, para cada conteúdo, em APENAS três linhas. Ou seja, sua resposta deverá ter apenas 3 linhas por conteúdo, ou 3*(número de conteúdo) linhas ao todo./n A primeira linha deve ser 'SIM' ou 'NÃO'./n  A segunda linha deve ser uma contextualização./n A terceira linha deve ser o assunto resumido do conteúdo. no padrão: 'Objeto: [assunto]'. Desconsiderar palavras como 'aquisição de', contratação de empresa para' e afins, ou seja, foque no objeto de fato./n/n. As respostas de cada conteúdo devem ser separadas por '###'"
    
    """for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)"""

    #model = genai.GenerativeModel('gemini-1.5-pro')
    model = genai.GenerativeModel('gemini-1.5-flash')
    #model = genai.GenerativeModel('gemini-1.0-pro')

    response = model.generate_content(prompt)

    resposta = response.text
    # veredicto = resposta[0]
    # justificativa = resposta[len(resposta)-1]

    #prompt = f"{content} /n Cada item da lista acima será doravante denominado 'conteúdo'. Qual o objeto de que trata cada conteúdo? Por favor, responda no padrão: 'Objeto: [objeto]'. Desconsiderar palavras como 'aquisição de', contratação de empresa para' e afins, ou seja, foque no objeto de fato. Responda uma linha para cada conteúdo."

    #response = model.generate_content(prompt)
    
    #objeto = response.text
    
    # return (veredicto, justificativa, objeto)

    return (resposta)