# -*- codeing = utf-8 -*-
# @Time : 2021/9/29 22:19
# @Author : 黎满
# @File : camera.py
# @Software : PyCharm
import numpy as np
import cv2 as cv
from threading import *
import time

class camerashowfram():

    def cameraShow(self):
        self.cap = cv.VideoCapture(0)
        size = (int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)))
        print('size:' + repr(size))

        self.es = cv.getStructuringElement(cv.MORPH_ELLIPSE, (9, 4))
        self.kernel = np.ones((5, 5), np.uint8)
        self.background = None

        while True:
            # 读取视频流
            grabbed, self.frame = self.cap.read()
            # 对帧进行预处理，先转成灰度图，在进行高斯模糊
            # 用高斯滤波进行弧度处理，进行处理的原因是因为每个输入的视频帧都会因为自然振动、光照变化或者摄像头本身的原因产生噪声，对噪声进行平滑是为了避免在运动和跟踪的时候将其检测出来
            gray_frame = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)  # 灰度处理
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
                cv.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # time.sleep(2)
                # cv.imwrite("../picture/image1.jpg", self.frameshow)
            # frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            self.showfram = self.frame
            cv.imshow('contours', self.showfram)
            # cv.imshow("dis", diff)
            # print('dddd')
            key = cv.waitKey(1) & 0xff
            if key == ord('q'):
                break
        self.cap.release()
        cv.destroyWindow()


if __name__ == '__main__':
    c = camerashowfram()
    th = Thread(target=c.cameraShow())
    th.start()
