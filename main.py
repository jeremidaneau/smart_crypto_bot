from connectors import Crypto_Bot
import config
import schedule
import time
import logging
from connectors.Crypto_Bot import Crypto_Bot



logger = logging.getLogger()

logger.setLevel(logging.INFO)


stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)s :: %(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('info.log')
#file_handler.setFormatter(formatter)
#file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
#logger.addHandler(file_handler)


if __name__ == "__main__":

    crypto_bot = Crypto_Bot(config.API_KEY, config.API_SECRET, False)

    schedule.every(1).seconds.do(crypto_bot.run_bot)
    schedule

    while True:
        schedule.run_pending()
        time.sleep(2)
