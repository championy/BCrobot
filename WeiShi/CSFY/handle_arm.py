import modbus_tk.modbus_tcp as mt
import modbus_tk.defines as md
import time

# line_id-----对应那一条线
# amr_id----那个机械臂
# num ------启动机械臂参数参数

#
master = mt.TcpMaster("192.168.1.181", 502)
master.set_timeout(5.0)


# # 启动机械臂
def start_arm(line_id, amr_id, num):
    ip = "192.168.1." + str(180 + amr_id)
    master = mt.TcpMaster(ip, 502)

    i = 0
    while i < 3:
        try:
            master.execute(1, md.WRITE_MULTIPLE_REGISTERS, int("1", 16),
                           output_value=[line_id, num])  # [启动信号]
            master.close()
            return True
        except:
            time.sleep(2)
            i += 1
            continue
    return False


# 判断机械臂是否运行完成
def arm_is_ok(amr_id):
    ip = "192.168.1." + str(180 + amr_id)
    master = mt.TcpMaster(ip, 502)

    i = 0
    error_count = 0
    while i < 3:
        if error_count <= 600:
            try:
                a = master.execute(1, md.READ_HOLDING_REGISTERS, 3, 1, output_value=[0])
            except:
                print('机械臂连接错误')
                i += 1
                time.sleep(3)
                continue
            print(a[0])

            if a[0] == 0:
                error_count += 1
                time.sleep(0.5)
                continue
            elif a[0] == 1:
                master.execute(1, md.WRITE_MULTIPLE_REGISTERS, 2,
                               output_value=[0])  # [启动信号]
                master.close()
                return 1
            elif a[0] == 2:
                print("机械臂相机报警!")
                return 2
            elif a[0] == 3:
                print("AGV无有物料")
                return 3
            time.sleep(0.5)
        elif error_count > 600:
            return 4
    print('机械臂连接超时！')
    return 5
