import logging

logging.basicConfig()
main_logger = logging.getLogger('uvicorn')
main_logger.setLevel(logging.INFO)
