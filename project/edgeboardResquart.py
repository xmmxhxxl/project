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

class RequestEdgeboard():
    def __init__(self):
        super(RequestEdgeboard, self).__init__()

        self.kind = []
        self.label_test = []
        self.bottlePrice = {}

        self.bottleName = None
        self.price = None
        self.result = None
        self.similarity = 0
        self.threshold = 0

        self.mysql = MysqlClass()
        self.kindList = self.mysql.select_all("select * from kindTable")
        self.findKind()

    def findKind(self):
        for i in self.kindList:
            self.kind.append(i[1])
            self.label_test.append(i[2])
            self.bottlePrice.update({i[1]: i[3]})
        # print(self.kind, self.label_test, self.bottlePrice)

    # 访问edgeboard，得到识别数据
    def getRecognitionResult(self, imagePath):
        try:
            with open(r'{}'.format(imagePath), 'rb') as f:
                image = f.read()
                result = re.post('http://192.168.137.254:24401/', params={'threshold': 0.1}, data=image).json()
        except Exception as ex:
            print("链接edgebodrd失败:", ex)
        try:
            label = tuple(result["results"])[0]
            self.result = label["label"]
            similarity = label["score"]
            self.similarity = similarity * 100
            self.similarity = round(self.similarity, 2)
        except Exception as ex:
            print(ex)

    def resultAnalysis(self):
        try:
            # voice = win.Dispatch("SAPI.SpVoice")
            for self.item in self.kind:
                if self.result == self.item and self.similarity > self.threshold:
                    self.bottleName = self.label_test[self.kind.index(self.item)]
                    self.price = self.bottlePrice[self.result]
                    # voice.Speak(self.pingzong[self.label1])
                    print(self.result,self.similarity, self.price, self.bottleName)
                    # self.insertIdentiRequestEdgeboardData()

                if self.similarity < 70:
                    # voice = win.Dispatch("SAPI.SpVoice")
                    # voice.Speak("相似度较低，请重新尝试")
                    break
        except Exception as ex:
            print("resultAnalysis:", ex)

    def ConnectRaspberryPie(self):
        try:
            ip = "192.168.137.254"
            port = 22
            user = "root"
            password = "root"
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port, user, password, timeout=10)
            cmd = "python startupFile.py"
            ssh.exec_command(cmd)
            print("成功执行命令")
            # 关闭连接
            ssh.close()
        except Exception as ex:
            print("链接edgeboard超时！", ex)


if __name__ == '__main__':
    RequestEdgeboard = RequestEdgeboard()
    RequestEdgeboard.ConnectRaspberryPie()
    RequestEdgeboard.getRecognitionResult("../picture/image2.png")
    RequestEdgeboard.resultAnalysis()
