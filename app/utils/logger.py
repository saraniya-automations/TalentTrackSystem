import logging

logger = logging.getLogger("EmployeeAPI")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("api.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

if not logger.hasHandlers():
    logger.addHandler(handler)
