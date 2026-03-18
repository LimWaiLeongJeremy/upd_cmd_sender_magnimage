import logging

def setup_logger(log_file):
    """Set up a logger to write logs to a file."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file, filemode='a')
    logger = logging.getLogger(__name__)
    return logger