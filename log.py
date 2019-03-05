import datetime
import logging
def makelog(log_saved_name):
    logger = logging.getLogger("mylogger")
    logger.setLevel(level=logging.INFO)
    time_now = datetime.datetime.now().strftime('%Y-%m-%d')
    handler = logging.FileHandler(log_saved_name)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)