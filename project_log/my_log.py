# from logzero import setup_logger,LogFormatter
import logging


# DEFAULT_FORMAT = '%(color)s[%(name)s: %(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
# DATE_FORMATTER="%y-%m-%d %H:%M:%S"
#
# def setup_mylogger(name=None,logfile=None,formatter=LogFormatter(datefmt=DATE_FORMATTER,fmt=DEFAULT_FORMAT)):
#    return setup_logger(name=name,logfile=logfile,formatter=formatter,maxBytes=3e7)


def setup_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    return logging