# -*- codeing = utf-8 -*-
# @Time : 2021/10/3 16:04
# @Author : liman
# @File : mysqlProject.py
# @Software : PyCharm
import pymysql
import hashlib
import time


class MysqlClass():
    def __init__(self, host, database, user, password, port=3306, charset='utf8'):
        self.host = host
        self.database = database
        self.user = user
        self.port = port
        self.password = password
        self.charset = charset

    # 链接对象
    def connect(self):
        self.conn = pymysql.connect(host=self.host, database=self.database, user=self.user,
                                    passwd=self.password, port=self.port, charset=self.charset)
        self.cursor = self.conn.cursor()

    # 关闭链接
    def close(self):
        self.cursor.close()
        self.conn.close()

    # 创建数据表
    # def newDatabse(self, usertable):
    #     sql = '''
    #         create table use{}(
    #             frequency int(32) primary key auto_increment,
    #             label varchar(255),
    #             price float(16),
    #             date timestamp(6),
    #             total float(16)
    #         );
    #     '''.format(usertable)
    #
    #     try:
    #         self.connect()
    #         self.cursor.execute(sql)
    #         self.conn.commit()
    #         self.close()
    #     except Exception as ex:
    #         print("创建数据表失败{},错误原因{}".format(usertable, ex))

    # 查询一条数据
    def newDatabse(self):
        sql = '''
            create table usedemo(
                frequency int(32) primary key auto_increment,
                label varchar(255),
                price float(16),
                date timestamp(6),
                total float(16)
            );
        '''

        try:
            self.connect()
            self.cursor.execute(sql)
            self.conn.commit()
            self.close()
        except Exception as ex:
            print("创建数据表失败,错误原因{}".format(ex))

    def select_ont(self, sql, params=[]):
        result = None
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchone()
            self.close()
        except Exception as ex:
            print("查询数据失败", ex)
        return result

    # 查询所有数据
    def select_all(self, sql, params):
        result = ()
        try:
            self.connect()
            self.cursor.execute(sql, params)
            result = self.cursor.fetchall()
        except Exception as ex:
            print(ex)
        return result

    def _edit(self, sql, params):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql, params)
            self.close()
        except Exception as ex:
            print(ex)
        return count

    def _editdata(self, sql):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql)
            self.conn.commit()
            self.close()
        except Exception as ex:
            print(ex)
        return count

    # 增
    def insert(self, sql, params=[]):
        return self._edit(sql, params)

    # 插入数据
    def insertdata(self, sql):
        return self._editdata(sql)

    # 删
    def delete(self, sql, params=[]):
        return self._edit(sql, params)
