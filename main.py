from PyQt5.QtWidgets import QApplication, QFileDialog

from gui import GUI

import numpy as np
import imutils
import cv2
import sys

from wb_comps import comp_for_channel, gray_world
from gamma_comps import gamma_correction
from sharpening import unsharp_mask


class App:
    def __init__(self, ui_path):
        self.gui = GUI(ui_path)

        # Properties
        self.filename = None

        self.image_original = None
        self.image_result = None
        self.image_wb = None
        self.image_gamma = None
        self.image_sharp = None
        self.image_sharp_gamma = None

        self.alpha_red = self.gui.slider_wb_alpha_red.value() / 10.0
        self.alpha_blue = self.gui.slider_wb_alpha_blue.value() / 10.0
        self.gamma = self.gui.slider_gamma.value() / 10.0
        self.sigma = self.gui.slider_sharp_sigma.value()
        self.strength = self.gui.slider_sharp_strength.value() / 100.0

        # Connects
        self.gui.button_load.clicked.connect(self.load_image)
        self.gui.button_process.clicked.connect(self.process_image)
        self.gui.slider_wb_alpha_red.valueChanged.connect(self.set_alpha_red)
        self.gui.slider_wb_alpha_blue.valueChanged.connect(self.set_alpha_blue)
        self.gui.slider_gamma.valueChanged.connect(self.set_gamma)
        self.gui.slider_sharp_sigma.valueChanged.connect(self.set_sigma)
        self.gui.slider_sharp_strength.valueChanged.connect(self.set_strength)

        self.gui.show()

    def load_image(self):
        try:
            self.filename = QFileDialog.getOpenFileName(filter="Képfájlok (*.png *.jpg *.jpeg *.bmp)")[0]
            self.image_original = cv2.imread(self.filename)
            self.gui.make_display_img(self.image_original, 'left')
        except Exception as e:
            print("Nem lett kép kiválasztva, vagy egyéb hiba.")

    def process_image(self):
        if self.image_original is None:
            return

        img_norm = cv2.normalize(self.image_original, None, 0.0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        img_proc = img_norm.copy()

        process_text = "Process:\n"

        # WHITE BALANCE
        if self.gui.check_wb_precomp.isChecked():
            img_proc = comp_for_channel('red', img_norm, alpha=self.alpha_red)
            img_proc = comp_for_channel('blue', img_proc, alpha=self.alpha_blue)

        if self.gui.check_wb.isChecked():
            img_proc = gray_world(img_proc)
            process_text += f"WB Red: {self.alpha_red}, WB Blue: {self.alpha_blue}\n"

        # GAMMA and SHARPENING
        if self.gui.check_gamma_sharp_msf.isChecked():
            img_proc = gamma_correction(img_proc, self.gamma)
            process_text += f"Gamma: {self.gamma}"
            img_proc = unsharp_mask(img_proc, self.sigma, self.strength)
            process_text += f"Sharpening: sigma={self.sigma} strength={self.strength}"

        print(process_text)
        self.image_result = img_proc
        self.gui.make_display_img(self.image_result, 'right')

    def set_alpha_red(self, value):
        # Property
        self.alpha_red = value / 10.0
        # Label
        new_value = str(self.gui.slider_wb_alpha_red.value() / 10.0)
        self.gui.value_wb_alpha_red.setText(new_value)

    def set_alpha_blue(self, value):
        # Property
        self.alpha_blue = value / 10.0
        # Label
        new_value = str(self.gui.slider_wb_alpha_blue.value() / 10.0)
        self.gui.value_wb_alpha_blue.setText(new_value)

    def set_gamma(self, value):
        self.gamma = value / 10.0
        new_value = str(self.gui.slider_gamma.value() / 10.0)
        self.gui.value_gamma.setText(new_value)

    def set_sigma(self, value):
        self.sigma = value
        new_value = str(self.gui.slider_sharp_sigma.value())
        self.gui.value_sharp_sigma.setText(new_value)

    def set_strength(self, value):
        self.strength = value / 10.0
        new_value = str(self.gui.slider_sharp_strength.value() / 10.0)
        self.gui.value_sharp_strength.setText(new_value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = App("image2.ui")
    app.exec_()
