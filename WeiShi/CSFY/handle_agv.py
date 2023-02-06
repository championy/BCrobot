# agv操作

import requests, json, time

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5',
    'content-type': "application/json",
    # 'token': 'YWRtaW4sMTk1NjI3NjY4OTE3MiwyYTJiMGNhYjJmNmZiZGZmYTcxZjk0MGJjMWY1OWNjNA=='
}


# 获取订单状态
def order_info(order_id):
    url = 'http://192.168.2.200:8088/api/v2/orders/{}'.format(order_id)
    i = 0
    while 1:
        if i <= 3:
            try:
                recv = requests.get(url, headers=headers)
                dir_recv = json.loads(recv.text)
                order_state = dir_recv['order_state']  # 订单状态
                print(order_state)
                return order_state
            except:
                i += 1
        else:
            return False


# 移动小车到指定站点
def car_to_pin(pin):
    upper_id = str(int(time.time()))
    url = 'http://192.168.2.200:8088/api/v2/orders'
    payload = {"upper_id": upper_id, "mission": [{"type": "move", "destination": pin, "map_id": 1}]}
    print(payload)
    i = 0
    while 1:
        if i <= 3:
            try:
                recv = requests.post(url, data=json.dumps(payload), headers=headers)
                dir_recv = json.loads(recv.text)
                order_id = dir_recv['id']
                return order_id
            except:
                i += 1
        else:
            return False


# 获取小车状态
def car_status(id):
    """

    :param id: 小车在调度系统里的id
    :return: 小车所在的站点
    """
    url = "http://192.168.2.200:8088/api/v2/vehicles/{}".format(id)
    recv = requests.get(url, headers=headers)
    dir_recv = json.loads(recv.text)
    car_sta = dir_recv['cur_station_no']
    return car_sta


# 判断小车是否到达点位
def car_to_pin_ok(order_id, reel_pin):
    while 1:
        counting = 1
        if counting >= 120:
            return 4
            # await websocket.send('status:小车前往站点超时，请检查小车！}')

        time.sleep(0.5)
        order_status = order_info(order_id)
        if order_status == "SUCCESS":
            now_dian = car_status(1)  # 现在小车所在的点位
            print('小车已到达{}点位'.format(now_dian))
            if now_dian == reel_pin:
                return 1
            else:
                return 3
                # await websocket.send('status:小车所到点位有误!'.format(i))
                # break
        elif order_status == 'EXECUTING':
            continue
        counting += 1











