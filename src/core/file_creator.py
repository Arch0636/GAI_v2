import os
import random
import string
import json
import base64
import time

# Original: X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
EICAR_B64 = "WDVPIVAlQEFQWzRcUFpYNTQoUF4pN0NDKTd9JEVJQ0FSLVNUQU5EQVJELUFOVElWSVJVUy1URVNULUZJTEUhJEgrSCo="

def get_eicar_content():
    return base64.b64decode(EICAR_B64)

def generate_random_content(ext, size):
    if ext in [".txt", ".log", ".ini", ".bat"]:
        return "".join(random.choices(string.ascii_letters + string.digits + " \n", k=size)).encode("utf-8")
    elif ext == ".json":
        dados = {"id": random.randint(1, 1000), "status": "ok", "data": "".join(random.choices(string.ascii_letters, k=20))}
        return json.dumps(dados).encode("utf-8")
    elif ext == ".csv":
        linhas = ["id,nome,valor"]
        for _ in range(5):
            linhas.append(f"{random.randint(1,100)},Item_{random.randint(1,10)},{random.random():.2f}")
        return "\n".join(linhas).encode("utf-8")
    return os.urandom(size)

def randomize_file_dates(path):
    try:
        dias_atras = random.randint(0, 365)
        segundos_aleat = random.randint(0, 86400)
        data_aleat = time.time() - (dias_atras * 86400 + segundos_aleat)
        os.utime(path, (data_aleat, data_aleat))
    except:
        pass

def create_file_on_disk(path, content, random_dates_flag):
    """Cria um único arquivo no disco com o conteúdo e opcionalmente randomiza suas datas."""
    with open(path, "wb") as f:
        f.write(content)
    if random_dates_flag:
        randomize_file_dates(path)
    return len(content)
