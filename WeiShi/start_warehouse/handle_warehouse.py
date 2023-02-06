### 成品仓和原料仓的处理


import modbus_tk.modbus_tcp as mt
import modbus_tk.defines as md
from handle_sql import *
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
            tuple_start = master_start.execute(2, md.READ_INPUT_REGISTERS, 1000, 12, output_value=[0])
            master_start.close()

            # 更新数据库
            for i in len(tuple_start):
                db_cudr = CUDRDataBase('started_warehouse')
                sql = """
                        UPDATE started_warehouse SET have = {} WHERE id={};
                    """.format(tuple_start[i], i)
                db_cudr.update_alldata_to_mysql(sql)
                if tuple_start[i] == 1:
                    try:
                        master_start.execute(2, md.WRITE_SINGLE_COIL, i + 1, output_value=[1])
                        master_start.close()
                        break
                    except:
                        i += 1
                        if i == 3:
                            return False
                        continue
                elif tuple_start[i] == 0:
                    try:
                        master_start.execute(2, md.WRITE_SINGLE_COIL, i + 1, output_value=[0])
                        master_start.close()
                        break
                    except:
                        i += 1
                        if i == 3:
                            return False
                        continue

            time.sleep(1)
        except:
            i += 1
            time.sleep(5)
            continue
    return False


def handle_finish_warehouse():
    i = 0
    while i < 3:
        try:
            tuple_finish = master_finish.execute(2, md.READ_INPUT_REGISTERS, 1000, 12, output_value=[0])
            master_finish.close()

            # 更新数据库
            for i in len(tuple_finish):
                db_cudr = CUDRDataBase('started_warehouse')
                sql = """
                        UPDATE started_warehouse SET have = {} WHERE id={};
                    """.format(tuple_finish[i], i)
                db_cudr.update_alldata_to_mysql(sql)
                if tuple_finish[i] == 1:
                    try:
                        master_finish.execute(2, md.WRITE_SINGLE_COIL, i + 1, output_value=[1])
                        master_finish.close()
                        break
                    except:
                        i += 1
                        if i == 3:
                            return False
                        continue

            time.sleep(1)
        except:
            i += 1
            time.sleep(5)
            continue

    return False

