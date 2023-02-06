import ast


def parse_input_str_to_dict(in_str:str):
    """
    TCP传输，字符串解析成字典
    :param in_str: 字符串
    :return: 解析后的字符串
    """
    if ":" not in in_str:
        return None
    c1 = in_str.strip()
    c1 = c1.split(";")

    c2 = [[i.split(":")[0],':'.join(i.split(":")[1:])] for i in c1]
    return dict(c2)

def parse_str_2_dict(str_data:str):
    """
    解析指令，字符串转换成字典
    :param str_data: "{'key': value, 'key': value}"
    :return: {'key': value, 'key': value}
    """
    try:
        return ast.literal_eval(str_data) ## 如果解析成功
    except:
        return None ## 如果解析失败