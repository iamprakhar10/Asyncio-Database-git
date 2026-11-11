import logging

logging.basicConfig(level=logging.INFO,
                    filename='log.log', 
                    filemode='w',
                    #format='%(asctime)s - %(levelname)s - %(message)s'
                    )

logging.debug("debugyggjygfjy")
logging.info("info")
logging.warning("warning")
logging.error("error")
logging.critical("critical")

x = 2
logging.info(f"x = {x}")

try:
    1/0
except ZeroDivisionError as e:
    logging.exception("Exception occurred of zero division", exc_info=True)

print(__name__)
"""
The root logger is simply the default logger. You can also create named loggers to identify which part of a larger program produced each message:
logger = logging.getLogger("payments")
logger.warning("Payment is taking longer than expected")

Custom logs
"""