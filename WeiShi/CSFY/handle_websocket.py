import struct, hashlib, base64, socket, threading, json
import time



# 获取请求头部数据,并将请求头转换为字典
def get_headers(data):
    headers = {}
    data = str(data, encoding="utf-8")
    header, body = data.split("\r\n\r\n", 1)
    header_list = header.split("\r\n")
    for i in header_list:
        i_list = i.split(":", 1)
        if len(i_list) >= 2:
            headers[i_list[0]] = "".join(i_list[1::]).strip()
        else:
            i_list = i.split(" ", 1)
            if i_list and len(i_list) == 2:
                headers["method"] = i_list[0]
                headers["protocol"] = i_list[1]
                print("请求类型: {} 请求协议: {}".format(i_list[0], i_list[1]))
    return headers


# 接收数据时的解码过程
def parse_payload(payload):
    payload_len = payload[1] & 127
    if payload_len == 126:
        mask = payload[4:8]
        decoded = payload[8:]
    elif payload_len == 127:
        mask = payload[10:14]
        decoded = payload[14:]
    else:
        mask = payload[2:6]
        decoded = payload[6:]

    # 将所有数据全部收集起来，对所有字符串编码
    bytes_list = bytearray()
    for i in range(len(decoded)):
        chunk = decoded[i] ^ mask[i % 4]
        bytes_list.append(chunk)
    body = str(bytes_list, encoding='utf-8')
    return body


# 封装并发送数据到浏览器
def send_msg(conn, msg_bytes):
    # 接收的第一个字节都是x81不变
    first_byte = b"\x81"
    length = len(msg_bytes)
    if length < 126:
        first_byte += struct.pack("B", length)
    elif length <= 0xFFFF:
        first_byte += struct.pack("!BH", 126, length)
    else:
        first_byte += struct.pack("!BQ", 127, length)
    msg = first_byte + msg_bytes
    conn.sendall(msg)
    return True


# 从浏览器中接收数据
def recv_msg(conn):
    data_recv = conn.recv(8096)
    if data_recv[0:1] == b"\x81":
        data_parse = parse_payload(data_recv)
        return data_parse
    return False


# 建立握手流程并创建 handler_msg 完成数据收发
def handler_accept_5000(sock):
    while True:
        conn, addr = sock.accept()
        data = conn.recv(8096)
        headers = get_headers(data)

        # 对请求头中的sec-websocket-key进行加密
        response_tpl = "HTTP/1.1 101 Switching Protocols\r\n" \
                       "Upgrade:websocket\r\n" \
                       "Connection: Upgrade\r\n" \
                       "Sec-WebSocket-Accept: %s\r\n" \
                       "WebSocket-Location: ws://%s\r\n\r\n"
        # 加盐操作,此处是H5规范定义好的
        magic_string = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        if headers.get('Sec-WebSocket-Key'):
            value = headers['Sec-WebSocket-Key'] + magic_string
        # 对数据进行加解密
        ac = base64.b64encode(hashlib.sha1(value.encode('utf-8')).digest())
        response_str = response_tpl % (ac.decode('utf-8'), headers.get("Host"))
        # 相应握手包数据
        conn.sendall(bytes(response_str, encoding="utf-8"))
        handler_msg_5000(conn)
        # t = threading.Thread(target=handler_msg, args=(conn,))
        # t.start()
        # t1 = threading.Thread(target=handler_msg1, args=(conn,))
        # t1.start()


# 5000主函数,用于实现数据交互
def handler_msg_5000(conn):
    with conn as connect_ptr:
        while True:
            try:
                dict_recv = recv_msg(connect_ptr)
                if dict_recv == False:
                    print('5000 断开')
                    break
                # cleient_connect[0] = connect_ptr

                print("接收数据5000: {}".format(dict_recv))
                # dicts_recv = json.loads(dict_recv)
                # WS = dicts_recv['WS']
                #
                # # 获取AMR 状态
                # if WS == 'amr_status':
                #     amr_status = get_agv_status()
                #     amr_status['SW'] = 'amr_status'
                #     send_5000 = json.dumps(amr_status)
                #     send_msg(connect_ptr, bytes(send_5000, encoding="utf-8"))



            except:
                time.sleep(5)
                print('断开')




# sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock1.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 5)
# sock1.bind(("127.0.0.1", 5000))
# sock1.listen(5)
# t_5000 = threading.Thread(target=handler_accept_5000, args=(sock1,))
# t_5000.start()
# print('5000服务器开启')