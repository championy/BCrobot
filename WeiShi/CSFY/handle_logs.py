import logging
import os
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import time


def mkdir_path(path_logs):
    """
    创建日志文件夹
    :param path_logs: 日志保存的路径
    :return:
    """
    tuple_path = os.path.split(path_logs)
    fold_name = tuple_path[0]
    if not os.path.exists(fold_name):
        os.makedirs(fold_name)


def recv_logging():
    """
    接收消息，写入日志
    :return:
    """
    logger = handle_logging('../../logs/recv_msg/tcp_server_recv.log')
    # cfg.LOG.dict_recvAndSend['recv'] = logger
    return logger


def send_logging():
    """
    发送消息，写入日志
    :return:
    """
    logger = handle_logging('../logs/send_msg/tcp_server_send.log')
    # cfg.LOG.dict_recvAndSend['send'] = logger
    return logger


def other_logging():
    """
    其他消息，写入日志文件
    :return:
    """
    logger = handle_logging('../logs/other/tcp_server_other.log')
    # cfg.LOG.dict_recvAndSend['other'] = logger
    return logger


def VipInfo_logging():
    """
    重要消息，写入日志文件
    :return:
    """
    logger = handle_logging('../logs/vip_info/tcp_server_vip.log')
    # cfg.LOG.dict_recvAndSend['VipInfo'] = logger
    return logger


## type_log:total_logger
## type_log:machine_id,machine_id:900010001
## type_log:recv
## type_log:send
def machine_logging(machine_id):
    """
    每一台机器，记录一个日志文件
    :return:
    """
    log_path = '../logs/{}/log_for_{}.log'.format(machine_id, machine_id)
    logger = handle_logging(log_path)
    # cfg.LOG.dict_machineId[machine_id] = logger
    return logger


def handle_logging(path_logs):
    """
    日志处理函数
    :param url_logs: 保存日志的目录地址
    :return:
    """
    # 创建一个logger
    mkdir_path(path_logs)  ## 创建日志保存的文件夹
    logger_name = path_logs.split('/')[-1].split('.')[0]
    logger = logging.getLogger(logger_name)  ## 不同的路径，生成不同的logger对象

    # 写入日志的等级
    logger.setLevel(logging.DEBUG)
    # logger.setLevel(logging.WARNING)

    logger.propagate = False
    # file_name = '.'.join(path_logs.split('.')[0:-1])
    # print(file_name)
    # log_file_handler = TimedRotatingFileHandler(filename=path_logs,when='S',interval=5,backupCount=5)
    # log_file_handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
    # log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}.log$")
    log_file_handler = RotatingFileHandler(filename=path_logs, maxBytes=3 * 1024 * 1024, backupCount=100,
                                           encoding='utf-8', delay=False)
    log_file_handler.setLevel(logging.DEBUG)  ## 写入日志文件的日志等级是 WARNING

    # 创建一个handler，用于写入日志文件
    # fh = logging.FileHandler(path_logs)
    # fh.setLevel(logging.DEBUG)

    # 再创建一个handler，用于输出到控制台
    ch = logging.StreamHandler()
    # 显示在控制台的等级
    ch.setLevel(logging.ERROR)
    # ch.setLevel(logging.DEBUG)

    # 定义handler的输出格式
    formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')
    # fh.setFormatter(formatter)
    log_file_handler.setFormatter(formatter)
    ch.setFormatter(formatter)

    if (logger.hasHandlers()):
        logger.handlers.clear()
    # 给logger添加handler
    # logger.addHandler(fh)
    logger.addHandler(log_file_handler)
    logger.addHandler(ch)
    return logger


def handle_logs(url_logs):
    """
    日志处理函数
    :return:
    """
    logger = logging.getLogger('tcp_server_logs')
    logger.setLevel(level=logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s:%(message)s")

    file_handler = logging.FileHandler(url_logs)
    file_handler.setLevel(level=logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(level=logging.DEBUG)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


def print_log(log):
    file_obj = open('logs/tcp_server.log', 'a+')
    log_time = time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))  # 转化时间格式
    file_obj.write("%s %s\n" % (log_time, str(log)))
    file_obj.close()  # 记得close()

