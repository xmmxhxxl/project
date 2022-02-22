# -*- codeing = utf-8 -*-
# @Time : 2021/8/11 14:54
# @Author : 黎满
# @File : edgeboardResquart.py
# @Software : PyCharm
import paramiko
import requests as re

from mysqlProject import MysqlClass


# import win32com.client as win

# 分类

class fication():
    def __init__(self):
        super(fication, self).__init__()

        self.kind = []
        self.label_test = []
        self.labelPrice = {}

        self.label2 = None
        self.price = None

        self.mysql = MysqlClass()
        self.kindList = self.mysql.select_all("select * from kindTable")
        self.findKind()

    def findKind(self):
        for i in self.kindList:
            self.kind.append(i[1])
            self.label_test.append(i[2])
            self.labelPrice.update({i[1]: i[3]})

    # 访问edgeboard，得到识别数据
    def detect(self, imagePath):
        try:
            with open(r'{}'.format(imagePath), 'rb') as f:
                image = f.read()
                result = re.post('http://192.168.137.254:24401/', params={'threshold': 0.1}, data=image).json()
        except Exception as ex:
            print("链接edgebodrd失败:", ex)
        try:
            print(result)
            label = result["results"]
            out = tuple(label)
            out1 = out[0]
            self.jieguo = out1["label"]
            print(self.jieguo)
            self.n = 0
            xiangsidu = out1["score"]
            self.xiangsidu = xiangsidu * 100
            self.xiangsidu = round(self.xiangsidu, 2)
        except Exception as ex:
            print(ex)

    def resultAnalysis(self):
        try:
            # voice = win.Dispatch("SAPI.SpVoice")
            for self.item in self.kind:
                if self.jieguo == self.item and self.xiangsidu > self.n:
                    print(self.kind.index(self.item))
                    self.label2 = self.label_test[self.kind.index(self.item)]
                    self.price = self.labelPrice[self.jieguo]
                    # voice.Speak(self.pingzong[self.label1])
                    print(self.xiangsidu, self.price, self.label2)
                    # self.insertIdentificationData()

                if self.xiangsidu < 70:
                    # voice = win.Dispatch("SAPI.SpVoice")
                    # voice.Speak("相似度较低，请重新尝试")
                    break
        except Exception as ex:
            print("resultAnalysis:", ex)

    def remotConnect(self):
        try:
            # 服务器相关信息,个人的用户名、密码、ip等信息
            ip = "192.168.137.254"
            port = 22
            user = "root"
            password = "root"
            # 创建SSHClient 实例对象
            ssh = paramiko.SSHClient()
            # 调用方法，表示没有存储远程机器的公钥，允许访问
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # 连接远程机器，地址，端口，用户名密码
            ssh.connect(ip, port, user, password, timeout=10)
            # 输入linux命令
            cmd = "python startupFile.py"
            ssh.exec_command(cmd)
            # 输出命令执行结果
            # result = stdout.read()
            print("成功执行命令")
            # 关闭连接
            ssh.close()
        except Exception as ex:
            print("链接edgeboard超时！", ex)


# if __name__ == '__main__':
#     ification = fication()
#     ification.remotConnect()
#     ification.detect("../picture/image2.png")
#     ification.resultAnalysis()
