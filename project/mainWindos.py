# coding = gbk
# @Time : 2021/10/25 8:47
# @Author : liman
# @File : mainWindos.py
# @Software : PyCharm
import json
import random
import sys
import time

import cv2 as cv
import numpy as np
import requests
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, QApplication, QLabel, QTableWidget, QTextEdit, QAbstractItemView
from paho.mqtt import client as mqtt_client

from demoProject import Ui_Form
from edgeboardResquart import RequestEdgeboard
from mqtt_send import MQTTReceive
from mysqlProject import MysqlClass


from Servo import Servo


class MyMainWindow(QWidget, Ui_Form):

    def __init__(self):
        super().__init__()
        self.requestEdgeboard = RequestEdgeboard()
        self.setupUi(self)
        self.classifiedArea.setColumnCount(2)
        self.classifiedArea.verticalHeader().setVisible(False)
        self.classifiedArea.horizontalHeader().setVisible(False)
        self.classifiedArea.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.classifiedArea.setShowGrid(False)

        self.videoThread = VideoThread()
        self.videoThread.playLabel = self.label
        self.videoThread.classifiedArea = self.classifiedArea
        self.videoThread.priceArea = self.priceArea
        self.videoThread.videoSin.connect(self.setIdentifySpecies)

        self.mqtt = MQTTThread()
        self.mqtt.user_sin.connect(self.setUserInformation)
        self.mqtt.switch_sin.connect(self.setSwitchCondition)
        self.mqtt.start()

        self.identify_but.clicked.connect(self.setIdentifySpecies)
        self.identify_but.setEnabled(False)

        self.automatic_but.toggled.connect(lambda: self.butChecked(self.automatic_but))
        self.manual_but.toggled.connect(lambda: self.butChecked(self.manual_but))
        self.automatic_but.setEnabled(False)
        self.manual_but.setEnabled(False)

        self.insertDataThread = InsertDataThread()
        self.insertDataThread.start()

        self.showVideoSin = False
        self.setOpenId = None
        self.setNickName = None
        self.setAvatarUrl = None
        self.avatar = None
        self.line = None

    def setIdentifySpecies(self):
        if self.videoThread.modelSin == "automatic":
            self.requestEdgeboard.getRecognitionResult("../picture/image2.png")

        elif self.videoThread.modelSin == "manual":
            self.videoThread.screenshotSin = True
            time.sleep(0.5)
            self.requestEdgeboard.getRecognitionResult("../picture/manual.png")

        self.requestEdgeboard.resultAnalysis()
        self.line = 0
        try:
            if self.requestEdgeboard.similarity >= 80:
                self.totalPrice = 0
                self.classifiedArea.insertRow(self.line)
                self.classifiedArea.setItem(self.line, 0, QTableWidgetItem(str(self.requestEdgeboard.bottleName)))
                self.classifiedArea.setItem(self.line, 1, QTableWidgetItem(str(self.requestEdgeboard.price)))
                self.line += 1
                QApplication.processEvents()  # 刷新界面

                # 求总价
                for it in range(0, self.classifiedArea.rowCount()):
                    if self.classifiedArea.item(it, 1) is None:
                        continue
                    price = self.classifiedArea.item(it, 1).text()
                    self.totalPrice = self.totalPrice + eval(price)
                self.totalPrice = round(self.totalPrice, 2)
                self.priceArea.setPlainText(str(self.totalPrice))
                QApplication.processEvents()

                self.videoThread.sg90StartSin = True

                self.insertDataThread.insertDataSin = True
                self.insertDataThread.label = self.requestEdgeboard.result
                self.insertDataThread.name = self.requestEdgeboard.bottleName
                self.insertDataThread.price = self.requestEdgeboard.price
                self.insertDataThread.openId = self.setOpenId

        except Exception as ex:
            print("setIdentifySpecies ->", ex)

    # 设置用户信息
    def setUserInformation(self, openId, nickName, avatarUrl):
        try:
            print(openId, nickName, avatarUrl)
            self.avatar = QPixmap()
            self.avatar.loadFromData(requests.Session().get(url=avatarUrl).content)

            self.avatarUrl.setPixmap(self.avatar)
            self.label_3.setText(nickName)

            self.setOpenId = openId
            self.setNickName = nickName
            self.setAvatarUrl = avatarUrl
            print(self.setOpenId)

        except Exception as ex:
            print("setUserInformation ->", ex)

    # 按键状态检测
    def setSwitchCondition(self, switchCondition):
        try:
            print(switchCondition)
            if switchCondition == 'open':
                self.videoThread.sinVideo = True
                self.videoThread.start()

                self.avatarUrl.setPixmap(self.avatar)
                self.label_3.setText(self.setNickName)

                self.automatic_but.setEnabled(True)
                self.manual_but.setEnabled(True)
                if self.videoThread.modelSin == 'manual':
                    self.identify_but.setEnabled(True)

            if switchCondition == 'close':
                self.classifiedArea.clearContents()
                self.avatarUrl.clear()
                self.videoThread.playLabel.clear()
                self.label_3.clear()
                self.priceArea.clear()

                self.videoThread.sg90StartSin = False
                self.videoThread.servo.SG90Stop()

                self.videoThread.sinVideo = False
                self.identify_but.setEnabled(False)
                self.automatic_but.setEnabled(False)
                self.manual_but.setEnabled(False)

                self.line = 0
        except Exception as ex:
            print("setSwitchCondition ->", ex)

    # 模式选择
    def butChecked(self, but):
        if but.text() == '自动':
            if but.isChecked():
                print("自动")
                self.videoThread.modelSin = "automatic"
                self.identify_but.setEnabled(False)
        if but.text() == '手动':
            if but.isChecked():
                self.videoThread.modelSin = "manual"
                self.identify_but.setEnabled(True)
                print("手动")


class VideoThread(QThread):
    videoSin = pyqtSignal()

    def __init__(self, parent=None):
        super(VideoThread, self).__init__(parent)
        self.cap = cv.VideoCapture(0)
        self.playLabel = QLabel()
        self.classifiedArea = QTableWidget()
        self.priceArea = QTextEdit()

        self.sinVideo = True
        self.screenshotSin = False
        self.modelSin = 'without'

        self.servo = Servo()
        self.sg90StartSin = False

        self.es = None
        self.kernel = None
        self.image = None
        self.frame = 24
        self.times = 0.25

    def run(self):
        # 获取图形尺寸
        size = (int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
        print('size:' + repr(size))
        self.es = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 4))
        self.kernel = np.ones((5, 5), np.uint8)
        self.background = None
        n = 0  # 总共进行的帧数
        items = [0] * 3  # 定义一个长度为3的数组，用来存放相邻三秒内的mse指标
        items = np.array(items)
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

                if self.background is None:
                    self.background = gray_frame
                    continue

                # 对于每个从背景之后读取的帧都会计算和背景之间的差，并得到一个差分图(different map)
                # 需要应用阈值出来来得到一幅黑白图像，并通过下面的代码来膨胀（dilate）图像，从而对孔（hole）和缺陷（imperfection）进行归一化处理
                diff = cv.absdiff(self.background, gray_frame)
                diff = cv.threshold(diff, 25, 255, cv.THRESH_BINARY)[1]  # 二值化阈值处理
                diff = cv.dilate(diff, self.es, iterations=2)  # 形态学膨胀

                # 显示矩形框
                icon,contours, hierarchy = cv.findContours(diff.copy(), cv.RETR_EXTERNAL,
                                                      cv.CHAIN_APPROX_SIMPLE)  # 该函数用来计算一幅图像中目标的轮廓
                for c in contours:
                    if cv.contourArea(c) < 1500:  # 用于矩形区域，只显示大于给定阈值的轮廓，所以一些微小的变化不会显示
                        continue
                    (x, y, w, h) = cv.boundingRect(c)  # 用于计算矩形边框的边界
                    cv.rectangle(self.image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # 加载视频流到ui界面
                showFarm = self.image
                showImage = QImage(showFarm, showFarm.shape[1], showFarm.shape[0], QImage.Format_RGB888)
                self.playLabel.setPixmap(QPixmap.fromImage(showImage))
                # 判断页面是否静止
                if self.modelSin == "automatic":
                    if n % (self.frame * self.times) == 0:
                        err = np.sum((self.oldimg.astype('float') - self.nowimg.astype('float')) ** 2)
                        err /= float(self.oldimg.shape[0] * self.oldimg.shape[1])
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
                        elif variance < 10000 and average < 500 and j >= 2:
                            # 使用多线程执行识别模块，节约代码执行时间
                            print("开始识别")
                            self.videoSin.emit()
                            j = 0
                elif self.modelSin == "manual" and self.screenshotSin:
                    cv.imwrite("../picture/manual.png", self.image)
                    self.screenshotSin = False

                if self.sg90StartSin:
                    self.servo.driveSG90()
                    self.sg90StartSin = False
        except Exception as ex:
            print("错误！！！\n" + str(ex))


class MQTTThread(QThread):
    user_sin = pyqtSignal(object, object, object)
    switch_sin = pyqtSignal(str)

    def __init__(self, parent=None):
        super(MQTTThread, self).__init__(parent)

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
            data = json.loads(msg.payload.decode())
            if msg.topic == 'user/openId':
                self.user_sin.emit(data['openId'], data['nickName'], data['avatarUrl'])
            else:
                self.switch_sin.emit(data['msg'])

        client.subscribe(topic)
        client.on_message = on_message

    def run(self):
        client = self.connect_mqtt()
        self.subscribe(client, "user/#")
        client.loop_forever()


class InsertDataThread(QThread):

    def __init__(self, parent=None):
        super(InsertDataThread, self).__init__(parent)
        self.openId = None
        self.label = None
        self.name = None
        self.price = None

        self.mysql = MysqlClass()
        self.insertDataSin = False

    def run(self):
        try:
            while True:
                if self.insertDataSin:
                    self.setIdentificationData(self.label, self.name, self.price, self.openId)
                    self.insertDataSin = False
                    print("数据插入成功")
        except Exception as e:
            print("InsertDataThread-run ->", e)

    def setIdentificationData(self, label, name, price, openId):
        try:
            print(label, name, price, openId)
            date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            userId = self.mysql.select_one("SELECT userId FROM user_db WHERE `openId`=%s", [openId])
            self.mysql.insert("INSERT INTO IdentifyingInformation(`label`,`name`,`price`,`date`,`user`) VALUES(%s,%s,"
                              "%s,%s,%s)", [label, name, price, date, userId])
            self.mysql.update("UPDATE user_db SET `total`=`total`+%s WHERE `openId`=%s", [price, openId])
        except Exception as e:
            print("setIdentificationData ->", e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    im = MyMainWindow()
    im.show()
    sys.exit(app.exec_())
