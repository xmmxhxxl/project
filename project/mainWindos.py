# coding = gbk
# @Time : 2021/10/25 8:47
# @Author : liman
# @File : mainWindos.py
# @Software : PyCharm
import json
import random
import sys

import cv2 as cv
import numpy as np
import requests
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QApplication, QLabel, QTableWidget, QTextEdit, QAbstractItemView
from paho.mqtt import client as mqtt_client

from demoProject import Ui_Form
from edgeboardResquart import fication
from mqtt_send import MQTTReceive
from mysqlProject import MysqlClass


class MyMainWindow(QWidget, Ui_Form):
    j = 0

    def __init__(self):
        super().__init__()
        self.fi = fication()
        self.setupUi(self)

        self.labeltxt = self.label
        self.thread = MyThread()
        self.thread.playLabel = self.label
        self.thread.classifiedArea = self.classifiedArea
        self.thread.priceArea = self.priceArea
        self.thread.videoSin.connect(self.sin)

        self.mqtt = MQTTThread()
        self.mqtt.user_sin.connect(self.setUserInformation)
        self.mqtt.switch_sin.connect(self.setSwitchCondition)
        self.mqtt.start()

        self.setOpenId = None
        self.setNickName = None
        self.setAvatarUrl = None
        self.avatar = None
        self.line = None

    def sin(self):
        self.fi.detect()
        self.fi.resultAnalysis()
        self.line = 0
        if self.fi.xiangsidu >= 60:

            self.classifiedArea.setColumnCount(2)
            self.classifiedArea.verticalHeader().setVisible(False)
            self.classifiedArea.horizontalHeader().setVisible(False)
            self.classifiedArea.setEditTriggers(QAbstractItemView.NoEditTriggers)
            self.classifiedArea.setShowGrid(False)

            self.totalPrice = 0
            self.classifiedArea.insertRow(self.line)
            self.classifiedArea.setItem(self.line, 0, QTableWidgetItem(str(self.fi.label2)))
            self.classifiedArea.setItem(self.line, 1, QTableWidgetItem(str(self.fi.price)))
            self.line += 1
            # ser.open_ser()
            # ser.send_msg()
            # self.insertData()  # 插入数据
            QApplication.processEvents()  # 刷新界面
            # 求总价
            try:
                for it in range(0, self.j + 1):
                    price = self.classifiedArea.item(it, 1).text()
                    print(self.fi.price)
                    self.totalPrice = self.totalPrice + eval(price)
                self.totalPrice = round(self.totalPrice, 2)
                print(self.totalPrice)
                self.priceArea.setPlainText(str(self.totalPrice))
                self.j += 1
                if self.j > 9:
                    self.j = 1
                QApplication.processEvents()
            except Exception as ex:
                print("识别错误" + ex)

    #   插入数据
    def insertData(self):
        try:
            my = MysqlClass(host='localhost', database='demomysql', user='root', password='root')
            my.insert('insert into tablehxl(label,similarity,price,total) values(%s,%s,%s,%s)',
                      [self.fi.label2, self.fi.jieguo, self.fi.price, self.totalPrice])
        except Exception as ex:
            print(ex)

    # 设置用户信息
    def setUserInformation(self, openId, nickName, avatarUrl):
        print(openId, nickName, avatarUrl)
        req = requests.get(avatarUrl)

        self.avatar = QPixmap()
        self.avatar.loadFromData(req.content)

        self.avatarUrl.setPixmap(self.avatar)
        self.label_3.setText(nickName)

        self.setOpenId = openId
        self.setNickName = nickName
        self.setAvatarUrl = avatarUrl

    # 按键状态检测
    def setSwitchCondition(self, switchCondition):
        if switchCondition == 'open':
            self.thread.sinVideo = True
            self.thread.start()

            self.avatarUrl.setPixmap(self.avatar)
            self.label_3.setText(self.setNickName)

            self.identify_but.clicked.connect(self.sin)

        if switchCondition == 'close':
            self.classifiedArea.clear()
            self.avatarUrl.clear()
            self.thread.playLabel.clear()
            self.label_3.clear()
            self.priceArea.clear()

            self.thread.sinVideo = False
            self.line = 0


# 使用多线程来读取视频流
class MyThread(QThread):
    videoSin = pyqtSignal()

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)
        self.cap = cv.VideoCapture(1)
        self.playLabel = QLabel()
        self.classifiedArea = QTableWidget()
        self.priceArea = QTextEdit()
        self.sinVideo = True

    def run(self):
        # 获取图形尺寸
        size = (int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
        print('size:' + repr(size))
        self.es = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 4))
        self.kernel = np.ones((5, 5), np.uint8)
        self.background = None
        self.frame = 24  # 帧数
        n = 0  # 总共进行的帧数
        self.times = 2  # 每隔2秒判断一次
        items = [0] * 3  # 定义一个长度为3的数组，用来存放相邻三秒内的mse指标
        global i  # 定义全局变量，用来控制数组的长度
        global j  # 定义全局变量，用来控制识别的次数
        i = 0
        j = 0

        try:
            while self.sinVideo:
                # print('开始运行')
                n += 1
                # 读取视频流
                grabbed, self.image = self.cap.read()
                # cv.imshow("self.image", self.image)
                if n == self.frame:
                    midimg = self.image
                elif n % self.frame == 0:
                    self.oldimg = midimg
                    self.nowimg = self.image
                    midimg = self.image

                # 对帧进行预处理，先转成灰度图，在进行高斯模糊
                # 用高斯滤波进行弧度处理，进行处理的原因是因为每个输入的视频帧都会因为自然振动、光照变化或者摄像头本身的原因产生噪声，对噪声进行平滑是为了避免在运动和跟踪的时候将其检测出来
                gray_frame = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)  # 灰度处理
                gray_frame = cv.GaussianBlur(gray_frame, (21, 21), 0)  # 高斯处理

                # 将第一帧作为整个输入的背景
                if self.background is None:
                    self.background = gray_frame
                    continue

                # 对于每个从背景之后读取的帧都会计算和背景之间的差，并得到一个差分图(different map)
                # 需要应用阈值出来来得到一幅黑白图像，并通过下面的代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
                diff = cv.absdiff(self.background, gray_frame)
                diff = cv.threshold(diff, 25, 255, cv.THRESH_BINARY)[1]  # 二值化阈值处理
                diff = cv.dilate(diff, self.es, iterations=2)  # 形态学膨胀

                # 显示矩形框
                contours, hierarchy = cv.findContours(diff.copy(), cv.RETR_EXTERNAL,
                                                      cv.CHAIN_APPROX_SIMPLE)  # 该函数用来计算一幅图像中目标的轮廓
                for c in contours:
                    if cv.contourArea(c) < 1500:  # 用于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示
                        continue
                    (x, y, w, h) = cv.boundingRect(c)  # 用于计算矩形边框的边界
                    cv.rectangle(self.image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # 加载视频流到ui界面
                showfram = self.image
                self.showImage = QImage(showfram, showfram.shape[1], showfram.shape[0], QImage.Format_BGR888)
                self.playLabel.setPixmap(QPixmap.fromImage(self.showImage))
                # 判断页面是否静止
                if n % (self.frame * self.times) == 0:
                    err = np.sum((self.oldimg.astype('float') - self.nowimg.astype('float')) ** 2)
                    err /= float(self.oldimg.shape[0] * self.oldimg.shape[1])
                    # print(len(items))
                    print(items)
                    items[i] = round(err, 3)
                    i += 1
                    print(i)
                    if i >= 3:
                        i = 0
                    print(items)
                    variance = np.var(items)
                    average = np.mean(items)
                    print("方差是：", variance)
                    print("平均数是：", average)
                    if variance > 10000 and average > 500:
                        j += 1  #
                        cv.imwrite("../picture/image{}.png".format(i), self.image)
                        print("成功保存截图！！", j)
                    elif variance < 10000 and average < 500 and j >= 3:
                        # 使用多线程执行识别模块，节约代码执行时间
                        print("开始识别")
                        self.videoSin.emit()
                        j = 0
        except Exception as ex:
            print("错误！！！\n" + str(ex))


class MQTTThread(QThread):
    user_sin = pyqtSignal(object, object, object)
    switch_sin = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MQTTThread, self).__init__(parent)
        self.MQTTReceive = MQTTReceive()

        self.broker = 'www.xmxhxl.top'
        self.port = 1883
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'

    def connect_mqtt(self) -> mqtt_client:
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        client = mqtt_client.Client(self.client_id)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def subscribe(self, client: mqtt_client, topic):
        def on_message(client, userdata, msg):
            # print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            data = json.loads(msg.payload.decode())
            if msg.topic == 'user/openId':
                print(data['openId'])
                self.user_sin.emit(data['openId'], data['nickName'], data['avatarUrl'])
            else:
                print(data['msg'])
                self.switch_sin.emit(data['msg'])

        client.subscribe(topic)
        client.on_message = on_message

    def run(self):
        client = self.connect_mqtt()
        self.subscribe(client, "user/#")
        client.loop_forever()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    im = MyMainWindow()
    im.show()
    sys.exit(app.exec_())
