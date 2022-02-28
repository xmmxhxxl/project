# coding=utf-8
from RPi import GPIO
import time


class Servo:

    def __init__(self):

        self.GPIO_pin_3 = 3
        self.GPIO_pin_4 = 4

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_pin_3, GPIO.OUT)
        GPIO.setup(self.GPIO_pin_4, GPIO.OUT)

        self.GPIO_PIN_PWM_3 = GPIO.PWM(self.GPIO_pin_3, 50)
        self.GPIO_PIN_PWM_4 = GPIO.PWM(self.GPIO_pin_4, 50)

        self.GPIO_PIN_PWM_3.start(0)
        self.GPIO_PIN_PWM_4.start(0)

    # 设置角度
    def setAngle(self, angle):
        if isinstance(angle, str):
            if angle.upper() == 'STOP':
                self.GPIO_PIN_PWM_3.ChangeDutyCycle(0)
                self.GPIO_PIN_PWM_4.ChangeDutyCycle(0)
        elif isinstance(angle, int) or isinstance(angle, float):
            self.GPIO_PIN_PWM_3.ChangeDutyCycle(1.82 + angle * 10 / 180)
            self.GPIO_PIN_PWM_4.ChangeDutyCycle(1.82 + angle * 10 / 180)

    def driveSG90(self):
        self.setAngle(180)
        time.sleep(0.3)
        self.setAngle('stop')
        time.sleep(2)

        self.setAngle(0)
        time.sleep(0.3)
        self.setAngle('stop')
        time.sleep(2)

    def SG90Stop(self):
        self.GPIO_PIN_PWM_3.stop()  # 关闭该引脚的 PWM
        self.GPIO_PIN_PWM_4.stop()  # 关闭该引脚的 PWM

        GPIO.cleanup()  # 清理 在退出时使用


# if __name__ == '__main__':
#     servo = Servo()
#     servo.driveSG90()
