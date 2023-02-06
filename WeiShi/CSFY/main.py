#! /usr/bin/env python
# -*- coding: utf-8 -*-
# ================================================================
#   Copyright (C) 2019 * Ltd. All rights reserved.
#
#   File name   : send_Sms.py
#   Author      : Y
#   Contact     :
#   Created date: 2019-12-1 12:18:04
#   Editor      : yoyo
#   Modify Time : 2020-04-13 12:18:04
#   Description :
#   Version     : 1.0
#   IDE         : PyCharm
#   License     : Copyright (C) 2017-2020, http://www.xinruibao.cn
#
# ================================================================
import json
import logging
import socket
import sys

sys.path.append('../')
import requests
import threading
import time
import queue
import random

from CSFY.config import cfg
from CSFY.handle_logs import send_logging, recv_logging, other_logging, machine_logging, VipInfo_logging
from CSFY.handle_time import get_time_current_server, verify_time_10000, verify_time_3heartbeat
from CSFY.parse_data import parse_str_2_dict
from CSFY.handle_threading import stop_thread

cfg.LOG.dict_recvAndSend['recv'] = recv_logging()
cfg.LOG.dict_recvAndSend['send'] = send_logging()
cfg.LOG.dict_recvAndSend['other'] = other_logging()
cfg.LOG.dict_recvAndSend['VipInfo'] = VipInfo_logging()


class ChatServer:
    def __init__(self, ip='0.0.0.0', port=9998):
        """
        服务器初始化操作,启动服务
        :param ip: 服务器绑定的ip
        :param port: 服务器监听的端口号
        """
        ## 生成套接字对象
        self.sock = socket.socket()
        ## 服务器绑定的套接字 ip 和 port
        self.addr = (ip, port)
        # 客户端 {socket_fd:'imei_id'}
        self.clients = {}
        ## imei_id 与 machine_id 的映射, {imei_id: machine_id}
        self.imei_to_machine = {}
        # 心跳包 {socket_fd:'time'}
        self.heartbeat = {}
        # 单个客户端线程id {socket_fd: thread_object}
        self.threading_object_client = {}
        ## 一个客户端对应一个线程 {thread_object: thread_name线程对象}
        self.threading_name_client = {}
        ## 一个imei号对应一个线程 supervisor_open_door_900010002, {imei_id: threading_object}
        self.threading_supervisor_open_door = {}
        ## 一个imei号对应一个订阅者 pubsub, {imei_id: pubsub_object}
        self.subscribe_supervisor_open_door = {}
        ## 每个客户端对应的 master redis,{socket_fd:6379}
        self.clients_2_master_redis = {}
        ##储存退出的机器号
        self.machine_id = []

        self.ip_post = {}

    ### 开启服务器
    def start(self):
        """
        启动服务器
        :return:
        """
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 地址重用
        self.sock.bind(self.addr)  # 绑定
        self.sock.listen()  # 监听
        threading.Thread(target=self.supervisor_VIP_info, name='supervisor_VIP_info').start()  ## 打印信息
        # accept会阻塞主线程,所以开一个新线程
        threading.Thread(target=self.accept, name='accept').start()

    ### 接收多个客户端
    def accept(self):
        """
        接收客户端请求
        :return:
        """
        while True:  # 多人连接
            sock, client = self.sock.accept()  # 阻塞
            if client[0] in self.ip_post:
                del self.ip_post[client[0]]
            if client[0] not in self.ip_post:
                self.ip_post[client[0]] = client[1]
                # sock.settimeout(2 * cfg.FUYONG.heartbeat_time // 1000)  ## 设置三个心跳时间即为超时
                f = sock  # 支持读写
                logger = cfg.LOG.dict_recvAndSend.get('other')
                print('连接的客户端socket_client:{}'.format(client))
                logger.warning('连接的客户端socket_client:{}'.format(client))
                queue_dictdata = queue.Queue(maxsize=10)  ## 存储解析之后的数据，字典类型
                # 准备接收数据,recv是阻塞的,开启新的线程
                obj_recv_thread = threading.Thread(target=self.recv, args=(f, queue_dictdata),
                                                   name='recv_{}_{}'.format(client[0], client[1]))
                obj_handlemsg_thread = threading.Thread(target=self.handle_msg_instructions, args=(f, queue_dictdata),
                                                        name='handlemsg_{}_{}'.format(client[0], client[1]))

                self.threading_object_client[f] = obj_recv_thread  # {套接字fd: 线程}
                obj_recv_thread.start()
                obj_handlemsg_thread.start()

    ### 生产者，循环接收客户端消息，存入队列中
    def recv(self, f, queue_dictdata):
        """
        服务器循环接收一个客户端的数据
        :param f: socket 套接字
        :param client: 客户端地址 ('ip', port)
        :return:
        """
        logger = cfg.LOG.dict_recvAndSend.get('recv')
        while True:  # 循环接收一个客户端数据

            # dict_info = self.recv_and_parse_msg(socket_fd=f)  ## 读取并解析数据，阻塞
            print('--------')
            dict_info = f.recv(1024)
            dict_info = dict_info.decode()
            print('取出的数据dict_info: {}'.format(dict_info))
            print('--------')


            # time_begin = get_time_current_server()
            if not dict_info and type(dict_info) == type(None):  ## 如果成功接收到信息，但是解析错误
                self.send(f, str({'SC': '[error msg], please send right data'}))
                logger.info('数据解析错误')
                continue
            elif dict_info == '' and type(dict_info) == type(''):  ## 如果客户端退出，跳出循环，消灭该线程
                logger.warning('data为空字符串没有 recv 数据 客户端断开')
                if f in self.threading_object_client:
                    object_threading = self.threading_object_client.get(f)
                    stop_thread(object_threading)
                    del self.threading_object_client[f]  ## 清除客户端记录

                f.close()  ## 关闭客户端
                break

            queue_dictdata.put(dict_info)  ## 将消息指令存放到队列中
            logger.warning('队列中存入的recv数据: {}'.format(dict_info))
            logger.warning('time_server: {}*********************************'.format(get_time_current_server()))
            if f in self.clients:
                imei_id = self.clients.get(f)
                machine_id = self.imei_to_machine.get(imei_id)
                logger1 = cfg.LOG.dict_machineId.get(machine_id)
                logger1.warning('recv: {}'.format(dict_info))  ## 单独写入机器号对应的日志文件中
                logger = cfg.LOG.dict_recvAndSend.get('recv')
                logger.warning('机器号: {}'.format(machine_id))
                logger.warning('\n')

    ### 消费者，循环处理一个客户端的消息指令，从队列中取指令
    def handle_msg_instructions(self, f, queue_dictdata):
        """
        服务器循环接收一个客户端的数据
        :param f: socket 套接字
        :param client: 客户端地址 ('ip', port)
        :return:
        """
        logger = cfg.LOG.dict_recvAndSend.get('other')
        while True:  # 循环接收一个客户端数据
            try:

                time.sleep(0.05)  ## 接收消息的时间稍微慢点，延时操作
                ## 如果在3个心跳时间内队列中依旧没有消息，说明客户端已经断开连接，此时退出循环，接下来对资源进行回收操作
                dict_info = queue_dictdata.get(block=True, timeout=2 * cfg.FUYONG.heartbeat_time // 1000)
            except:
                logger.info('队列中没有消息，客户端套接字已经断开')
                break

            logger.warning('队列中取出的数据dict_info: {}'.format(dict_info))
            logger.warning('time_server: {}*********************************'.format(get_time_current_server()))
            ## 如果时间戳超时
            if dict_info == 'start':
                pass




    ### 发送一条消息给客户端
    def send(self, socket_fd, msg: str):
        """
        给客户端发送消息
        :param socket_fd: 客户端套接字
        :param msg: 要发送的消息
        :return:
        """
        logger = cfg.LOG.dict_recvAndSend.get('send')
        data = "{}\r\n".format(msg.strip())  # 服务端需要一个换行符
        socket_fd.writelines(data)
        socket_fd.flush()
        logger.warning('send: {}'.format(msg))
        if socket_fd in self.clients:
            imei_id = self.clients.get(socket_fd)
            machine_id = self.imei_to_machine.get(imei_id)
            logger1 = cfg.LOG.dict_machineId.get(machine_id)
            logger1.warning('send: {}'.format(msg))  ## 单独写入机器号对应的日志文件中
            logger1.warning('\n')
            logger.warning('机器号: {}'.format(machine_id))
            logger.warning('\n')

    ### 停止服务器
    def stop(self):
        """
        停止服务器
        :return:
        """
        for s in self.clients:
            s.close()
        self.sock.close()
        # self.event.set()

    # 循环打印重要信息
    def supervisor_VIP_info(self):
        """
        循环打印重要信息
        :return:
        """
        logger = cfg.LOG.dict_recvAndSend.get('VipInfo')
        # logger=VipInfo_logging()
        while True:
            time.sleep(10)
            logger.warning('######-------------------------#####')
            logger.warning('#-----#####---------------#####-----')
            logger.warning('#----------#####-----#####----------')
            logger.warning('#---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            self.print_VIP_info(logger)
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.info('   #---------------#####---------------')
            logger.warning('#---------------#####---------------')
            logger.warning('#----------#####-----#####----------')
            logger.warning('#-----#####---------------#####-----')
            logger.warning('######-------------------------#####')

    ### 打印重要信息
    def print_VIP_info(self, logger):
        """
        打印重要信息
        self.clients:{socket_fd: imei_id}
        self.heartbeat:{socket_fd: 1586507626980}
        self.threading_supervisor_open_door:{imei_id:threading_object}
        self.subscribe_supervisor_open_door:{imei_id:pubsub_object}
        self.threading_object_client:{socket_fd:thread_object}
        self.clients_2_master_redis{socket_fd: 6379}
        :return:
        """
        logger1 = logger
        logger1.warning('self.imei_to_machine -{}- {}\n'.format(len(self.imei_to_machine), self.imei_to_machine))
        logger1.warning('self.client -{}- {}\n'.format(len(self.clients), self.clients))
        logger1.warning('self.heartbeat: -{}- {}\n'.format(len(self.heartbeat), self.heartbeat))
        logger1.warning('self.clients_2_master_redis -{}- {}\n'.format(len(self.clients_2_master_redis),
                                                                       self.clients_2_master_redis))
        logger1.warning('self.threading_object_client -{}- {}\n'.format(len(self.threading_object_client),
                                                                        self.threading_object_client))
        logger1.warning('self.threading_supervisor_open_door -{}- {}\n'.format(len(self.threading_supervisor_open_door),
                                                                               self.threading_supervisor_open_door))
        logger1.warning('self.subscribe_supervisor_open_door -{}- {}\n'.format(len(self.subscribe_supervisor_open_door),
                                                                               self.subscribe_supervisor_open_door))
        logger1.warning('threading.enumerate -{}- {}\n'.format(len(threading.enumerate()), threading.enumerate()))

    ### 接收信息，解析信息
    def recv_and_parse_msg(self, socket_fd):
        """
        接收消息，解析消息
        :param socket_fd: 客户端套接字
        :return: 解析出的指令
        """
        logger = cfg.LOG.dict_recvAndSend.get('other')
        try:
            data = socket_fd.readline()  # 阻塞到换行符
            logger.warning("\n\n")
            logger.warning('time_end ################################# {}'.format(
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time.time())))))
            logger.warning('number_threading: {} {}'.format(len(threading.enumerate()), threading.enumerate()))
            if data == '' or not data:  ## 接收到空消息，说明客户端断开连接，则退出循环
                logger.info('data{}'.format(data))
                logger.info('管道破裂 Broken pipe...')
                logger.info('客户端主动断开 Broken pipe...')
                return ''
            logger.info('数据解析后data_after:{}'.format(data))
        except Exception as e:
            logging.error(e)  # 有任何异常,退出
            return ''

        msg = data.strip()
        try:
            dict_info = parse_str_2_dict(msg)  # 解析得到的字典
        except Exception as e:
            print()
            logging.error(e)  # 消息解析有错误
            logger.info('recv from client msg: {}'.format(msg))
            dict_info = None

        return dict_info

    ## 循环跑线！！！
    def runing(self, f):
        pass


if __name__ == '__main__':
    cs = ChatServer()
    cs.start()
