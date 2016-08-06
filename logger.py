# coding=utf8

import logging
import logging.handlers
import config


# 로거 인스턴스를 만든다
logger = logging.getLogger('my_logger')

# 포매터를 만든다
fomatter = logging.Formatter(
    '[%(asctime)s][%(levelname)s|%(filename)s:%(lineno)s] > %(message)s')

# 스트림과 파일로 로그를 출력하는 핸들러를 각각 만든다.
fileHandler = logging.FileHandler('./myLoggerTest.log')
streamHandler = logging.StreamHandler()

# 각 핸들러에 포매터를 지정한다.
fileHandler.setFormatter(fomatter)
streamHandler.setFormatter(fomatter)

# 로거 인스턴스에 스트림 핸들러와 파일핸들러를 붙인다.
logger.addHandler(fileHandler)
logger.addHandler(streamHandler)

# 로거 인스턴스로 로그를 찍는다.
logger.setLevel(config.log_level)


if __name__ == '__main__':
    logger.debug("===========================")
    logger.info("TEST START")
    logger.warning("스트림으로 로그가 남아요~")
    logger.error("파일로도 남으니 안심이죠~!")
    logger.critical("치명적인 버그는 꼭 파일로 남기기도 하고 메일로 발송하세요!")
    logger.debug("===========================")
    logger.info("TEST END!")
