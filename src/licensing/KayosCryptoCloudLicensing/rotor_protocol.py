import random
import string

def rodar_rotor():
    # Gera uma sequência pseudoaleatória de 9 caracteres alfanuméricos
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=9))
