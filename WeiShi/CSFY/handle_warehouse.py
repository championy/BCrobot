### 成品仓和原料仓的处理


import modbus_tk.modbus_tcp as mt
import modbus_tk.defines as md
import time

# 原料仓modbus
master_start = mt.TcpMaster("192.168.1.140", 502)
master_start.set_timeout(5.0)

# 成品仓modbus
master_finish = mt.TcpMaster("192.168.1.150", 502)
master_finish.set_timeout(5.0)


def handle_start_warehouse():
    i = 0
    while i < 3:
        try:
            tuple_start = master_start.execute(2, md.READ_COILS, 1000, 12, output_value=[0])
            master_start.close()
            break
        except:
            i += 1
            continue




