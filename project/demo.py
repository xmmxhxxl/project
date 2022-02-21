# -*- codeing = utf-8 -*-
# @Time : 2021/9/29 14:53
# @Author : 黎满
# @File : demoshow.py
# @Software : PyCharm
import sys
import time
from threading import *

import cv2 as cv
import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import *

from demoProject import Ui_Form
from project.edgeboardResquart import fication


class MyMainWindow(QWidget, Ui_Form):
    i = 0

    def __init__(self):
        super().__init__()
        th = Thread(target=self.show_camera)
        th.start()
        self.setupUi(self)
        # self.priceButton.clicked.connect(self.screenshot)
        self.priceButton_2.clicked.connect(self.claerc)

    def initTimer(self):
        self.timer = QTimer(self)
        self.timer.start(1)
        self.timer.timeout.connect(self.show_camre)

    def camera_open(self):
        cap = cv.VideoCapture(1)
        if cap.isOpened():
            print('open')
        else:
            print('摄像头未打开')

    def show_camera(self):
        self.cap = cv.VideoCapture(1)
        # 获取图形尺寸
        size = (int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
        print('size:' + repr(size))

        self.es = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 4))
        self.kernel = np.ones((5, 5), np.uint8)
        self.background = None
        frame = 24  # 帧数
        n = 0  # 总共进行的帧数
        times = 3  # 每隔2秒判断一次n += 1
        global midimg
        # try:
        while True:
                # 读取视频流
                grabbed, self.image = self.cap.read()
                if n == frame:
                    midimg = self.image
                elif n % frame == 0:
                    oldimg = midimg
                    nowimg = self.image
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
                    # time.sleep(2)
                    # cv.imwrite("../picture/image1.jpg", self.frameshow)
                # frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                # 加载视频流到ui界面
                showfram = self.image
                showImage = QImage(showfram, showfram.shape[1], showfram.shape[0], QImage.Format_BGR888)
                self.label.setPixmap(QPixmap.fromImage(showImage))
                # 判断页面是否静止
                localtime = time.asctime(time.localtime(time.time()))
                if n % (frame * times) == 0:
                    err = np.sum((oldimg.astype('float') - nowimg.astype('float')) ** 2)
                    err /= float(oldimg.shape[0] * oldimg.shape[1])
                    print(err)
        # except Exception as ex:
        #     print("错误！！！\n" + str(ex))

    def screenshot(self):
        print("screenshot")
        self.fi = fication()
        self.fi.detect()
        self.fi.resultAnalysis()
        tabl = self.classifiedArea

        if self.fi.xiangsidu >= 80:
            self.totalPrice = 0
            # 设置表格显示标签、相似度、价格
            tabl.setItem(self.i, 0, QTableWidgetItem(str(self.fi.label2)))
            tabl.setItem(self.i, 1, QTableWidgetItem(str(self.fi.price)))
            # self.fi.insertIdentificationData()
            # 求总价
            try:
                for it in range(0, self.i + 1):
                    price = tabl.item(it, 1).text()
                    print(self.fi.price)
                    self.totalPrice = self.totalPrice + eval(price)
                self.totalPrice = round(self.totalPrice, 2)
                print('总价是', self.totalPrice)
                priceArea = self.priceArea
                priceArea.setPlainText(str(self.totalPrice))
                self.i += 1
                if self.i > 9:
                    self.i = 1
            except Exception as ex:
                print("当前没有数据")
                print(ex)

    def claerc(self):
        self.i = 0
        self.classifiedArea.clearContents()
        self.priceArea.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    im = MyMainWindow()
    im.show()
    sys.exit(app.exec_())
