from ctypes import *

MAX_AXIS = 48


class IODBPSD_U(Union):
    _fields_ = [
        ('cdata', c_char),
        ('idata', c_short),
        ('ldata', c_long),
        ('cdatas', c_char * MAX_AXIS),
        ('idatas', c_short * MAX_AXIS),
        ('ldatas', c_long * MAX_AXIS)
    ]


class IODBPSD(Structure):
    _fields_ = [
        ('datano', c_short),
        ('type', c_short),
        ('u', IODBPSD_U)
    ]


facos = cdll.LoadLibrary('./Fwlib32.dll')


class Facos(object):
    def __init__(self, ip, port, timeout=10):
        if isinstance(ip, str):
            ip = ip.encode()
        self.ip = ip
        self.port = port
        self.timeout = timeout
        self.handler = c_ushort()

    def connect(self):
        print(type(self.handler))
        res = facos.cnc_allclibhndl3(c_char_p(self.ip), c_ushort(self.port), c_int(self.timeout),
                                     addressof(self.handler))
        return res == 0

    def disconnect(self):
        res = facos.cnc_freelibhndl(self.handler)
        return res == 0

    @property
    def products(self):
        """
        生产件数
        :return: 生产件数
        """
        iodbpsd = IODBPSD()
        facos.cnc_rdparam(self.handler, 6711, 0, 4 + MAX_AXIS, addressof(iodbpsd))
        return iodbpsd.u.ldata

    def __enter__(self):
        if self.connect():
            return self
        raise Exception("Connection failed")

    def __exit__(self, type, value, traceback):
        self.disconnect()


if __name__ == "__main__":
    a = Facos("192.168.1.1", 8193)
    a.connect()
    # with Facos("192.168.1.1", 8193) as f:
    # print("生产件数:", f.products)

