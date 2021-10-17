from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qt_ui.main_window import Ui_MainWindow
from video_work import cvDecode,play_Work
import sys

class MainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        #   导入Qt的qss样式
        self.qssFileName = "qss/mainWin.qss"
        self.qss = QSSLoad()
        self.qssFile = self.qss.readQssFile(self.qssFileName)
        self.setStyleSheet(self.qssFile)

        #按钮事件绑定
        self.btn_input.clicked.connect(self.load_path)
        self.btn_pause.clicked.connect(self.pause_video)
        self.btn_pause.setEnabled(False)
        self.init_work()

    def init_work(self):
        self.decodework = cvDecode()
        self.decodework.threadFlag = 1
        self.decodework.start()

        self.playwork = play_Work()
        self.playwork.threadFlag = 1
        self.playwork.playLabel = self.label_video
        # self.playwork.start()

        # self.pool = QThreadPool()  # Qt线程池
        # self.pool.globalInstance()
        # self.pool.setMaxThreadCount(10)  # 设置最大线程
        # self.pool.start(self.playwork)

        self.play_thread = QThread()    # 创建线程
        self.playwork.moveToThread(self.play_thread)
        self.play_thread.started.connect(self.playwork.play)    # 线程与类方法进行绑定
        self.play_thread.start()



    #   视频导入功能
    def load_path(self):
        self.btn_pause.setEnabled(True)
        #   设置文件扩展名过滤,注意用双分号间隔
        fileName, filetype = QFileDialog.getOpenFileName(self, "选取文件", "./", "Excel Files (*.mp4);;Excel Files (*.avi)")

        self.decodework.changeFlag = 1
        self.decodework.video_path = r""+fileName
        self.playwork.playFlag = 1

    #   暂停/播放功能
    def pause_video(self):
        if self.btn_pause.text()=="暂停":
            self.btn_pause.setText("播放")
            self.playwork.playFlag = 0
        else:
            self.btn_pause.setText("暂停")
            self.playwork.playFlag = 1

    def closeEvent(self, event):
        print("关闭线程")
        # Qt需要先退出循环才能关闭线程
        if self.decodework.isRunning():
            self.decodework.threadFlag = 0
            self.decodework.quit()
        # if self.playwork.isRunning():
        #     self.playwork.threadFlag = 0
        #     self.playwork.quit()
        # self.playwork.threadFlag = 0
        # self.pool.clear()

        if self.play_thread.isRunning():
            self.playwork.threadFlag = 0
            self.play_thread.quit()
class QSSLoad:
    @staticmethod
    def readQssFile(qssFileName):
        with open(qssFileName, 'r', encoding='UTF-8') as file:
            return file.read()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

