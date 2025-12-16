## infrastructure/logger.py

import logging
import json
import sys

# Configuração básica do logger para direcionar a saída para stdout,
# permitindo que o Docker capture os logs corretamente.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("VigilAPI")

def log_event(message: str, data: dict = None, level: str = "INFO"):
    """
    Registra um evento da aplicação de forma estruturada em JSON.

    Args:
        message (str): A descrição principal do evento.
        data (dict, optional): Dados contextuais adicionais sobre o evento.
        level (str): Nível de severidade do log (INFO, WARNING, ERROR, DEBUG).
    """
    log_entry = {"event": message}

    # Adiciona dados contextuais se fornecidos
    if data:
        # Garantir que os dados sejam serializáveis em JSON
        try:
            json.dumps(data)
            log_entry["data"] = data
        except TypeError:
            # Se os dados contiverem objetos não serializáveis, converte para string
            log_entry["data"] = str(data)

    # Formata a mensagem final como JSON
    log_message = json.dumps(log_entry)

    # Seleciona o nível de logging apropriado
    log_level = level.upper()

    if log_level == "ERROR":
        logger.error(log_message)
    elif log_level == "WARNING":
        logger.warning(log_message)
    elif log_level == "DEBUG":
        logger.debug(log_message)
    else:
        # Padrão para INFO
        logger.info(log_message)