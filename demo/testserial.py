# -*- codeing = utf-8 -*-
# @Time : 2021/10/23 11:44
# @Author : liman
# @File : testserial.py
# @Software : PyCharm
import serial
import time


class serialclass():

    def open_ser(self):
        port = 'com9'  # 串口号
        baudrate = 115200
        try:
            self.ser = serial.Serial(port, baudrate, timeout=5)
            print("成功打开串口！")
        except Exception as ex:
            print("打开串口失败", ex)

    def send_msg(self):
        try:
            send_data = '1'
            self.ser.write(str(send_data).encode('gbk'))
            print("数据已发送", send_data)
        except Exception as ex:
            print("发送异常", ex)

    def read_msg(self):
        try:
            print("等待数据接收")
            while True:
                data = self.ser.read(self.ser.in_waiting).decode('gbk')
                if data != '':
                    break
            print("已经接收数据:", data)
        except Exception as ex:
            print("读取异常", ex)

    def close_ser(self):
        try:
            self.ser.close()
            if self.ser.isOpen():
                print("串口未关闭")
            else:
                print("串口已经关闭")
        except Exception as ex:
            print("串口关闭异常！", ex)


if __name__ == '__main__':
    ser = serialclass()
    ser.open_ser()
    # ser.send_msg()
    # ser.read_msg()
    # ser.close_ser()
