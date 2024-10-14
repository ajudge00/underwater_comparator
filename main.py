from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QSlider, QLabel, QFileDialog, QCheckBox, \
    QDoubleSpinBox
from PyQt5.QtGui import QImage
from PyQt5 import uic, QtGui
import numpy as np
import imutils
import cv2
import sys

from wb_comps import comp_for_channel, gray_world
from gamma_comps import gamma_correction
from sharpening import unsharp_mask


class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi("image1.ui", self)

        # Widgets
        self.img_left = self.findChild(QLabel, "label_image_original")
        self.img_right = self.findChild(QLabel, "label_image_proc")
        self.button_load = self.findChild(QPushButton, "button_load")
        self.button_process = self.findChild(QPushButton, "button_process")
        self.button_save = self.findChild(QPushButton, "button_save")

        self.slider_alpha_red = self.findChild(QSlider, "slider_alpha_red")
        self.slider_alpha_blue = self.findChild(QSlider, "slider_alpha_blue")
        self.slider_gamma = self.findChild(QSlider, "slider_gamma")
        self.slider_sigma = self.findChild(QSlider, "slider_sigma")
        self.slider_strength = self.findChild(QSlider, "slider_strength")

        self.label_alpha_red = self.findChild(QLabel, "label_alpha_red")
        self.label_alpha_blue = self.findChild(QLabel, "label_alpha_blue")
        # self.spinner_alpha_blue = self.findChild(QDoubleSpinBox, "spinner_alpha_blue")
        self.label_gamma = self.findChild(QLabel, "label_gamma")
        self.label_sigma = self.findChild(QLabel, "label_sigma")
        self.label_strength = self.findChild(QLabel, "label_strength")

        self.check_wb = self.findChild(QCheckBox, "check_wb")
        self.check_gamma = self.findChild(QCheckBox, "check_gamma")
        self.check_sharp = self.findChild(QCheckBox, "check_sharp")
        self.weight = self.findChild(QLabel, "check_weight")
        self.check_multi = self.findChild(QCheckBox, "check_multi")

        # Properties
        self.filename = None
        self.image_original = None
        self.image_processed = None
        self.alpha_red = self.slider_alpha_red.value() / 10.0
        self.alpha_blue = self.slider_alpha_blue.value() / 10.0
        self.gamma = self.slider_gamma.value() / 10.0
        self.sigma = self.slider_sigma.value()
        self.strength = self.slider_strength.value() / 10.0

        # Connects
        self.button_load.clicked.connect(self.load_image)
        self.button_process.clicked.connect(self.process_image)
        self.slider_alpha_red.valueChanged.connect(self.set_alpha_red)
        self.slider_alpha_blue.valueChanged.connect(self.set_alpha_blue)
        self.slider_gamma.valueChanged.connect(self.set_gamma)
        self.slider_sigma.valueChanged.connect(self.set_sigma)
        self.slider_strength.valueChanged.connect(self.set_strength)
        # self.spinner_alpha_blue.valueChanged.connect(self.set_alpha_blue_spinner)

        self.show()

    def load_image(self):
        try:
            self.filename = QFileDialog.getOpenFileName(filter="Képfájlok (*.png *.jpg *.jpeg *.bmp)")[0]
            self.image_original = cv2.imread(self.filename)
            self.make_display_img(self.image_original, 'left')
        except Exception as e:
            print("Nem lett kép kiválasztva, vagy egyéb hiba.")

    def process_image(self):
        img_norm = cv2.normalize(self.image_original, None, 0.0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        img_proc = img_norm.copy()

        process_text = "Process:\n"

        # WHITE BALANCE
        if self.check_wb.isChecked():
            img_proc = comp_for_channel('red', img_norm, alpha=self.alpha_red)
            img_proc = comp_for_channel('blue', img_proc, alpha=self.alpha_blue)
            img_proc = gray_world(img_proc)
            process_text += f"WB Red: {self.alpha_red}, WB Blue: {self.alpha_blue}\n"

        # GAMMA
        if self.check_gamma.isChecked():
            img_proc = gamma_correction(img_proc, self.gamma)
            process_text += f"Gamma: {self.gamma}"

        # SHARPENING
        elif self.check_sharp.isChecked():
            img_proc = unsharp_mask(img_proc, self.sigma, self.strength)
            process_text += f"Sharpening: sigma={self.sigma} strength={self.strength}"

        print(process_text)
        self.make_display_img(img_proc, 'right')

    def set_alpha_red(self, value):
        # Property
        self.alpha_red = value / 10.0
        # Label
        new_value = str(self.slider_alpha_red.value() / 10.0)
        self.label_alpha_red.setText(new_value)

    def set_alpha_blue(self, value):
        # Property
        self.alpha_blue = value / 10.0
        # Label
        new_value = str(self.slider_alpha_blue.value() / 10.0)
        self.label_alpha_blue.setText(new_value)

    def set_alpha_blue_spinner(self, value):
        self.alpha_blue = value
        self.slider_alpha_blue.setValue(int(self.alpha_blue * 10))

    def set_gamma(self, value):
        self.gamma = value / 10.0
        new_value = str(self.slider_gamma.value() / 10.0)
        self.label_gamma.setText(new_value)

    def set_sigma(self, value):
        self.sigma = value
        new_value = str(self.slider_sigma.value())
        self.label_sigma.setText(new_value)

    def set_strength(self, value):
        self.strength = value / 10.0
        new_value = str(self.slider_strength.value() / 10.0)
        self.label_strength.setText(new_value)

    def make_display_img(self, img, side):
        if img.dtype == np.float32:
            img = (img * 255).astype(np.uint8)

        image_resized = imutils.resize(img, width=640)
        frame = cv2.cvtColor(image_resized, cv2.COLOR_BGR2RGB)
        image_displayed = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888)

        if side == 'left':
            self.img_left.setPixmap(QtGui.QPixmap.fromImage(image_displayed))
        elif side == 'right':
            self.img_right.setPixmap(QtGui.QPixmap.fromImage(image_displayed))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec_()
