# -*- codeing = utf-8 -*-
# @Time : 2021/8/11 14:54
# @Author : 黎满
# @File : edgeboardResquart.py
# @Software : PyCharm
import paramiko
import requests as re
import os
from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication

import win32com.client as win
import serial.tools.list_ports


# 语音播报


# 分类
class fication():
    def __init__(self):
        super(fication, self).__init__()
        # self.setupUi(self)
        self.pingzong = ["硬质塑料瓶", "软质塑料瓶", "大个塑料瓶", "易拉罐"
                         ]

        self.label_test = ["hardBottle", "softBottle", "bigBottle", "popCan"
                           ]

        self.labelPrice = {"hardBottle": "0.07", "popCan": "0.15", "softBottle": "0.07", "bigBottle": "0.07"}
        # self.label1=0

    # 访问edgeboard，得到识别数据
    def detect(self):
        try:
            with open(r'../picture/image2.png', 'rb') as f:
                image = f.read()
                result = re.post('http://192.168.137.254:24401/', params={'threshold': 0.1}, data=image).json()
        except Exception as ex:
            print("链接edgebodrd失败:", ex)
        try:
            print(result)
            label = result["results"]
            # print(str)
            out = tuple(label)
            # print(out)
            out1 = out[0]
            self.jieguo = out1["label"]
            print(self.jieguo)
            self.n = 0
            xiangsidu = out1["score"]
            self.xiangsidu = xiangsidu * 100
            self.xiangsidu = round(self.xiangsidu, 2)
            # self.label1 = 0
        except Exception as ex:
            print(ex)

    def resultAnalysis(self):
        try:
            self.label1 = 0
            voice = win.Dispatch("SAPI.SpVoice")
            for self.item in self.label_test:
                if self.jieguo == self.item and self.xiangsidu > self.n:
                    print(self.label_test.index(self.item))
                    self.label1 = self.label_test.index(self.item)
                    self.label2 = self.pingzong[self.label1]
                    self.price = self.labelPrice[self.jieguo]
                    voice.Speak(self.pingzong[self.label1])
                    print(self.xiangsidu, self.price)
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
            # ls = "ls"
            ssh.exec_command(cmd)
            # 输出命令执行结果
            # result = stdout.read()
            print("成功执行命令")
            # 关闭连接
            ssh.close()
        except Exception as ex:
            print("链接edgeboard超时！",ex)


if __name__ == '__main__':
    ification = fication()
    ification.remotConnect()
    ification.detect()
    ification.resultAnalysis()
