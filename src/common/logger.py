import logging

LOG_LEVEL = logging.INFO

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)

# Create a formatter for log messages
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def init_file_logger(file_name, log_level=LOG_LEVEL):
    # Create a file handler
    file_handler = logging.FileHandler(f"{file_name}.log", mode="w")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


# Create a console handler
console_handler = logging.StreamHandler()
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
