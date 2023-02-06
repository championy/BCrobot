from easydict import EasyDict as edict

__C = edict()

cfg = __C

__C.FUYONG = edict()
__C.FUYONG.heartbeat_time = 30000 ## 约定，客户端与服务端心跳时间间隔是 30000ms,即 30s

# 日志配置文件
__C.LOG = edict()
__C.LOG.dict_machineId = {}
__C.LOG.dict_recvAndSend = {}
