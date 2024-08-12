import re
from fuzzywuzzy import fuzz
from datetime import datetime


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

