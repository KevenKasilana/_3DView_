# 开发时间：2022/3/4 23:10
from _3D_Viewer import *
import sys
import cv2
import imageio
import nibabel as nib
import SimpleITK as sitk
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qdarkstyle

class Viewer_3D_app(QMainWindow, Ui_MainWindow):
    def __init__(self):
        print("执行了__init__")

        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # 各个面的保存地址  后面需要加个“.jpg”
        self.transverse_path = r'D:\PyQt daima\mission\NewApplication_3\cache\transverse'
        self.sagittal_path = r'D:\PyQt daima\mission\NewApplication_3\cache\sagittal'
        self.coronal_path = r'D:\PyQt daima\mission\NewApplication_3\cache\coronal'

        self.x_max = self.y_max = self.z_max = 0
        self.x = self.y = self.z = 0
        self.image_data = None

        # 输出当前tab的页数
        print(self.viewWidget.count())

        self.signal_connect()

    def signal_connect(self):
        print("执行了signal_connect")
        print("signal_connect里的：", self.viewWidget.count())

        self.actionOpen_Main_Image.triggered.connect(self.select_image)     # 菜单Open_Main_Image
        self.actionAdd_New_Tab.triggered.connect(self.add_new_Tab)          # 菜单Add_New_Tab
        self.select_btn.clicked.connect(self.get_location)                  # ”确定“按钮
        self.viewWidget.currentChanged.connect(self.tabchange)               # 改变Tab页面

    # 选择图像（菜单Open_Main_Image）
    def select_image(self):
        print("执行了select_image")

        # 打开文件
        self.path_abs, image_type = QFileDialog.getOpenFileName(self, "打开图片", ".", "*.nii;;*.jpg;;*.png;;;All Files(*)")
        print(self.path_abs)

        image = sitk.ReadImage(self.path_abs)                           # 读取图片
        self.image_data = sitk.GetArrayFromImage(image)                 # 将图片转化为numpy数组
        self.z_max, self.y_max, self.x_max = self.image_data.shape      # 获取图片的三维数据-depth, height, width
        print("所选图像的size为：", self.x_max, self.y_max, self.z_max)

        self.label_initial_settings(self.x_max, self.y_max, self.z_max)
        self.update_location(str(int(self.x_max//2)), str(int(self.y_max//2)), str(int(self.z_max//2)))

    # 三个面的图像的原始大小
    def label_initial_settings(self, width, height, depth):
        print("执行了label_initial_settings")

        self.transverse_plane_show.ori_img_size = (width, height)
        self.sagittal_plane_show.ori_img_size = (height, depth)
        self.coronal_plane_show.ori_img_size = (width, depth)

    # 更新图像
    def update_location(self, x, y, widget_id):
        print("执行了update_location")

        if widget_id == "transverse_plane_show":
            self.x_input_edit.setText(str(int(x)))  # 改了
            self.y_input_edit.setText(str(int(y)))
        elif widget_id == "sagittal_plane_show":
            self.y_input_edit.setText(str(int(x)))
            self.z_input_edit.setText(str(int(y)))
        elif widget_id == "coronal_plane_show":
            self.x_input_edit.setText(str(int(x)))
            self.z_input_edit.setText(str(int(y)))
        else:       # 输入（x, y, z）时，将初始位置设为中心位置
            self.x_input_edit.setText(x)
            self.y_input_edit.setText(y)
            self.z_input_edit.setText(widget_id)

        self.get_location()

    # 从文本框内获取坐标
    def get_location(self):
        print("执行了get_location")

        self.x = int(self.x_input_edit.text())
        self.y = int(self.y_input_edit.text())
        self.z = int(self.z_input_edit.text())
        self.get_image_of_three_view(self.x, self.y, self.z)

        self.update_view()

    # 获取三个面
    def get_image_of_three_view(self, x_index, y_index, z_index):
        print("执行了get_image_of_three_view")

        image_transverse = self.image_data[int(z_index) - 1, :, :]  # 为何要 -1
        image_coronal = self.image_data[:, int(y_index) - 1, :]
        image_sagittal = self.image_data[:, :, int(x_index) - 1]

        # 将当前显示的图片保存到对应路径上
        imageio.imwrite(self.transverse_path+str(self.viewWidget.currentIndex()+1)+".jpg", image_transverse)
        imageio.imwrite(self.sagittal_path+str(self.viewWidget.currentIndex()+1)+".jpg", image_sagittal)
        imageio.imwrite(self.coronal_path+str(self.viewWidget.currentIndex()+1)+".jpg", image_coronal)

    # 更新3个面
    def update_view(self):
        print("执行了update_view")

        self.transverse_plane_show.last_pos = self.sagittal_plane_show.last_pos = self.coronal_plane_show.last_pos = (self.x, self.y, self.z)
        # 矢状面和冠状面因图像保存原因需要镜像翻转后再显示 -- 对保存好的图片进行镜像操作后再显示出来
        sagittal_Pixmap = QPixmap.fromImage(QImage(self.sagittal_path+str(self.viewWidget.currentIndex()+1)+".jpg").mirrored(False, True))
        coronal_Pixmap = QPixmap.fromImage(QImage(self.coronal_path+str(self.viewWidget.currentIndex()+1)+".jpg").mirrored(False, True))

        self.transverse_plane_show.setPixmap(QPixmap(self.transverse_path+str(self.viewWidget.currentIndex()+1)+".jpg").scaled(self.transverse_plane_show.width(), self.transverse_plane_show.height(), 1))
        self.sagittal_plane_show.setPixmap(QPixmap(sagittal_Pixmap).scaled(self.sagittal_plane_show.width(), self.sagittal_plane_show.height(), 1))
        self.coronal_plane_show.setPixmap(QPixmap(coronal_Pixmap).scaled(self.coronal_plane_show.width(), self.coronal_plane_show.height(), 1))

    def tabchange(self, index):
        print("执行了tabchange")
        print("跳转了Tab页，当前Tab页为：", self.viewWidget.currentIndex()+1)
        self.update_view()
        self.viewWidget.setCurrentIndex(self.viewWidget.currentIndex())

    def add_new_Tab(self):
        print("执行了add_new_Tab")
        self.AddTab()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = Viewer_3D_app()

    app.setStyleSheet(qdarkstyle.load_stylesheet())

    viewer.show()
    #viewer.showFullScreen()
    sys.exit(app.exec_())
