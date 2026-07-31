import os
import platform
import logging

if platform.platform().startswith('Windows'):
    _ = os.path.join(os.getenv('HOMEDRIVE'),
                                os.getenv('HOMEPATH'),
                                '.log')
else:
    _ = os.path.join(os.getenv('HOME'),
                                '.log')

print("  ", _)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s : %(levelname)s : %(message)s',
    filename=_,
    filemode='w',
)

logging.debug(" ")
logging.info("  ")
logging.warning(" ")
