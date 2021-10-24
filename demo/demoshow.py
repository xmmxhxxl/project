# -*- codeing = utf-8 -*-
# @Time : 2021/10/7 14:38
# @Author : liman
# @File : demoshow.py
# @Software : PyCharm
# -*- codeing = utf-8 -*-
# @Time : 2021/9/29 14:53
# @Author : 黎满
# @File : demoshow.py
# @Software : PyCharm
import sys
import time
from PIL import Image
from PIL import ImageChops
from PyQt5.QtCore import *
from PyQt5.uic.properties import QtCore

from project.edgeboardResquart import fication
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QImage, QFont
from ui.demoProject import Ui_Form
from ui.demoProject import *
import cv2 as cv
from threading import *
import threading
import numpy as np
from project.camera import camerashowfram
from demo.testserial import serialclass


class MyMainWindow(QWidget, Ui_Form):
    j = 0

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.priceButton_2.clicked.connect(self.claerc)
        self.labeltxt = self.label
        print('开始')
        self.thread = MyThread()
        self.thread.playLabel = self.label
        self.thread.classifiedArea = self.classifiedArea
        self.thread.priceArea = self.priceArea
        # self.trigger.connect(self.show_camera)
        self.thread._sinout.connect(self.sin)
        # self.shibie = self.thread.shibie
        self.thread.start()
        # self.identify = IdentifyThread()

    def sin(self):
        print("准备刷新界面")
        self.fi = fication()
        self.fi.detect()
        self.fi.resultAnalysis()
        # self.identify.start()
        # self.fi = self.identify.identify
        if self.fi.xiangsidu >= 60:
            print("尝试刷新界面")
            self.totalPrice = 0
            # 设置表格显示标签、相似度、价格
            self.classifiedArea.setItem(self.j, 0, QTableWidgetItem(str(self.fi.label2)))
            self.classifiedArea.setItem(self.j, 1, QTableWidgetItem(str(self.fi.price)))
            ser = serialclass()
            ser.open_ser()
            ser.send_msg()
            QApplication.processEvents()
            print("尝试刷新界面")
            # self.fi.insertIdentificationData()
            # 求总价
            try:
                for it in range(0, self.j + 1):
                    price = self.classifiedArea.item(it, 1).text()
                    print(self.fi.price)
                    self.totalPrice = self.totalPrice + eval(price)
                self.totalPrice = round(self.totalPrice, 2)
                print('总价是', self.totalPrice)
                self.priceArea.setPlainText(str(self.totalPrice))
                self.j += 1
                if self.j > 9:
                    self.j = 1
                print("没有刷新界面")
                QApplication.processEvents()
            except Exception as ex:
                print("当前没有数据")
                print(ex)

    def claerc(self):
        # self.thread.start()
        self.j = 0
        self.classifiedArea.clearContents()
        self.priceArea.clear()


# 使用多线程来读取视频流
class MyThread(QThread):
    _sinout = pyqtSignal()  # 信号
    print('成功')

    def __init__(self, parent=None):
        super(MyThread, self).__init__(parent)
        print('初始化')
        self.playLabel = QLabel()
        self.classifiedArea = QTableWidget()
        self.priceArea = QTextEdit()

    def run(self):
        self.cap = cv.VideoCapture(1)
        print('成功打开摄像头')
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
            while True:
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
                # frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                # 加载视频流到ui界面
                showfram = self.image
                self.showImage = QImage(showfram, showfram.shape[1], showfram.shape[0], QImage.Format_BGR888)
                self.playLabel.setPixmap(QPixmap.fromImage(self.showImage))
                # 判断页面是否静止
                # localtime = time.asctime(time.localtime(time.time()))
                # self.ifstatic()
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
                        self._sinout.emit()
                        j = 0
        except Exception as ex:
            print("错误！！！\n" + str(ex))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    im = MyMainWindow()
    im.show()
    print('结束')
    sys.exit(app.exec_())
