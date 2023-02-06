import time
import sys

sys.path.append('../')
from CSFY.config import cfg
from CSFY.handle_logs import handle_logging

logger = handle_logging('./logs/handle_time.log')  ## 生成一个 logger 对象


def get_time_current_server():
    """
    获取当前系统的时间戳
    :return:
    """
    return int(time.time() * 1000)


def verify_time_3heartbeat(time_client):
    """
        时间校验函数
        :param time_client: 客户端发送过来的时间
        :return: 时间校验是否成功，检验成功返回 True
        """
    str_time_client = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_client) // 1000))
    str_time_server = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(get_time_current_server() // 1000))
    if get_time_current_server() - int(time_client) >= 3 * cfg.FUYONG.heartbeat_time:  ## 时间间隔为 6s
        deltal_time = get_time_current_server() - int(time_client)
        logger.info('时间验证失败 client_time:{}, server_time:{}'.format(str_time_client, str_time_server))
        logger.info('时间验证失败 client_time:{}, server_time:{}, deltal:{}'.format(time_client, get_time_current_server(),
                                                                              deltal_time))
        return False
    else:
        deltal_time = get_time_current_server() - int(time_client)
        logger.info('时间验证成功 client_time:{}, server_time:{}'.format(str_time_client, str_time_server))
        logger.info('时间验证成功 client_time:{}, server_time:{}, deltal:{}'.format(time_client, get_time_current_server(),
                                                                              deltal_time))
        return True


def verify_time_10000(time_client):
    """
    时间校验函数
    :param time_client: 客户端发送过来的时间
    :return: 时间校验是否成功，检验成功返回 True
    """
    str_time_client = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_client)))
    str_time_server = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(get_time_current_server()))
    deltal_time = get_time_current_server() - int(time_client)
    if deltal_time > 5000:  ## 时间间隔为 5s
        logger.info('时间验证失败 client_time:{}, server_time:{}'.format(str_time_client, str_time_server))
        logger.info('时间验证失败 client_time:{}, server_time:{}, deltal:{}'.format(time_client, get_time_current_server(),
                                                                              deltal_time))
        return False
    else:
        logger.info('时间验证成功 client_time:{}, server_time:{}'.format(str_time_client, str_time_server))
        logger.info('时间验证成功 client_time:{}, server_time:{}, deltal:{}'.format(time_client, get_time_current_server(),
                                                                              deltal_time))
        return True
