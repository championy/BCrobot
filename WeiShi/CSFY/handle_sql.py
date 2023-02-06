# 数据库操作
from decimal import Decimal

import MySQLdb


class CUDRDataBase(object):
    def __init__(self, tables_name):
        """
        :param tables_name: 数据库表名称
        """
        self.tables_name = tables_name

        self.db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="123456", db="weishi", port=3306,
                                  charset="utf8")

        self.cursor = self.db.cursor()

    def insert_data_to_mysql(self, sql):
        """
        插入一条数据到数据库
        :param sql: sql 语句
        :return: True or False
        """
        ## insert into Order_info(key_id, order_id, machine_id) values('cbg-0005','cbg-0005','900010001');
        i = 0
        while i < 3:  ## 尝试插入 3 次数据库都是失败，则放弃查询
            try:
                self.cursor.execute(sql)
                self.db.commit()
                self.cursor.close()
                self.db.close()
                return True
            except:
                self.db.rollback()  ## 如果插入失败，回滚
                i += 1
                continue

        self.cursor.close()
        self.db.close()
        return False

    def delete_data_from_mysql(self, sql):
        """
        从表中删除一条数据
        :param sql: sql 语句
        :return: True or False
        """
        i = 0
        while i < 3:  ## 尝试 3 次删除数据失败，则放弃数据库操作
            try:
                self.cursor.execute(sql)
                self.db.commit()
                self.cursor.close()
                self.db.close()
                return True
            except:
                self.db.rollback()  ## 如果删除错误，回滚
                i += 1
                continue

        self.cursor.close()
        self.db.close()
        return False

    def update_alldata_to_mysql(self, sql):
        """
        更新数据库
        :param sql: sql 语句
        :return: True or False
        """
        i = 0
        while i < 3:  ## 尝试 3 次更新数据库失败，则放弃数据库操作
            try:
                self.cursor.execute(sql)
                self.db.commit()
                self.cursor.close()
                self.db.close()
                return True
            except:
                self.db.rollback()  ## 如果更新数据库失败，回滚
                i += 1
                continue

        self.cursor.close()
        self.db.close()
        return False

    def select_onedata_from_mysql(self, key_id, field_name):
        """
        查询一个字段值
        :param key_id: 主键值
        :param field_name: 字段名称
        :return: 查询的结果，字符串类型
        """
        ## select order_id from Order_info where key_id='cbg-0001';
        ## 'select {} from self.tables_name where key_id={}'.formate(field_name, key_id)
        sql = """select {} from {} where id='{}'""".format(field_name, self.tables_name, key_id)
        # print('sql: ', sql)
        i = 0
        while i < 3:
            try:
                self.cursor.execute(sql)
                str_data = self.cursor.fetchone()[0]
                # print(type(str_data), str_data)
                self.cursor.close()
                self.db.close()
                return str_data
            except:
                i += 1
                continue

        self.cursor.close()
        self.db.close()
        return None

    def select_alldata_from_mysql(self, key_id):
        """
        查询一行记录
        :param key_id: 主键值
        :return: 查询的结果，字典类型
        """
        ## select * from Order_info where key_id='cbg-0001';
        sql = """ select * from {} where id='{}' """.format(self.tables_name, key_id)
        # print('sql: ', sql)
        i = 0
        while i < 3:
            try:
                self.cursor.execute(sql)
                tuple_data = self.cursor.fetchone()
                print(type(tuple_data), 'tuple_data: ', tuple_data)
                descript = self.cursor.description
                print(type(descript), descript)
                dict_data = {}
                for i in range(len((tuple_data))):
                    dict_data[descript[i][0]] = tuple_data[i]

                print(type(dict_data), dict_data)
                self.cursor.close()
                self.db.close()
                return dict_data
            except:
                i += 1
                continue

        self.cursor.close()
        self.db.close()
        return None

    def select_one_machine_id(self, sql):
        i = 0
        while i < 3:  ## 尝试zhao 3 次数据库都是失败，则放弃查询
            try:
                self.cursor.execute(sql)
                order_info = self.cursor.fetchall()
                self.db.commit()
                self.cursor.close()
                self.db.close()
                return order_info
            except:
                self.db.rollback()  ## 如果插入失败，回滚
                i += 1
                continue

        self.cursor.close()
        self.db.close()
        return False







