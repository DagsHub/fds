import logging
import logging.config

logging.basicConfig(format='%(asctime)s at %(name)s.%(funcName)s'
                           ' (File "%(pathname)s", line %(lineno)d) %(levelname)s - %(message)s')


class Logger(object):

    logging_level = logging.INFO
    _logger = None

    @classmethod
    def set_logging_level(cls, level):
        cls.logging_level = level
        cls._logger = None

    @classmethod
    def get_logger(cls, logger_name: str):
        if cls._logger is None:
            # Ignoring the logger of dvc, by setting it to highest level
            logging.getLogger('dvc').setLevel(logging.CRITICAL)

            # Logger for fds
            cls._logger = logging.getLogger(logger_name)
            cls._logger.setLevel(cls.logging_level)

        return cls._logger
