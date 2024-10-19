from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QSlider, QLabel, QFileDialog, QCheckBox, \
    QDoubleSpinBox, QComboBox
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
    def __init__(self, ui_path):
        super(UI, self).__init__()

        uic.loadUi(ui_path, self)

        # Widgets
        self.img_left = self.findChild(QLabel, "img_original")
        self.img_right = self.findChild(QLabel, "img_result")
        self.button_load = self.findChild(QPushButton, "button_load")
        self.button_process = self.findChild(QPushButton, "button_process")
        self.button_save = self.findChild(QPushButton, "button_save")
        self.combo_pipeline = self.findChild(QComboBox, "combo_pipeline")
        self.combo_see_stage = self.findChild(QComboBox, "combo_see_stage")

        self.slider_wb_alpha_red = self.findChild(QSlider, "slider_wb_alpha_red")
        self.slider_wb_alpha_blue = self.findChild(QSlider, "slider_wb_alpha_blue")
        self.slider_gamma = self.findChild(QSlider, "slider_gamma")
        self.slider_sharp_sigma = self.findChild(QSlider, "slider_sharp_sigma")
        self.slider_sharp_strength = self.findChild(QSlider, "slider_sharp_strength")

        self.value_wb_alpha_red = self.findChild(QLabel, "value_wb_alpha_red")
        self.value_wb_alpha_blue = self.findChild(QLabel, "value_wb_alpha_blue")
        self.value_gamma = self.findChild(QLabel, "value_gamma")
        self.value_sharp_sigma = self.findChild(QLabel, "value_sharp_sigma")
        self.value_sharp_strength = self.findChild(QLabel, "value_sharp_strength")

        self.check_wb_precomp = self.findChild(QCheckBox, "check_wb_pc")
        self.check_wb = self.findChild(QCheckBox, "check_wb")
        self.check_gamma_sharp_msf = self.findChild(QCheckBox, "check_gamma_sharp_msf")

        # Properties
        self.filename = None

        self.image_original = None
        self.image_result = None
        self.image_wb = None
        self.image_gamma = None
        self.image_sharp = None
        self.image_sharp_gamma = None

        self.alpha_red = self.slider_wb_alpha_red.value() / 10.0
        self.alpha_blue = self.slider_wb_alpha_blue.value() / 10.0
        self.gamma = self.slider_gamma.value() / 10.0
        self.sigma = self.slider_sharp_sigma.value()
        self.strength = self.slider_sharp_strength.value() / 100.0

        # Connects
        self.button_load.clicked.connect(self.load_image)
        self.button_process.clicked.connect(self.process_image)
        self.slider_wb_alpha_red.valueChanged.connect(self.set_alpha_red)
        self.slider_wb_alpha_blue.valueChanged.connect(self.set_alpha_blue)
        self.slider_gamma.valueChanged.connect(self.set_gamma)
        self.slider_sharp_sigma.valueChanged.connect(self.set_sigma)
        self.slider_sharp_strength.valueChanged.connect(self.set_strength)

        self.check_wb_precomp.stateChanged.connect(
            lambda: self.change_result_combo("wbpc", self.check_wb_precomp.isChecked())
        )
        self.check_wb.stateChanged.connect(
            lambda: self.change_result_combo("wb", self.check_wb.isChecked())
        )
        self.check_gamma_sharp_msf.stateChanged.connect(
            lambda: self.change_result_combo("gsmsf", self.check_gamma_sharp_msf.isChecked())
        )

        self.view_choices = {
            "original": ["Original"],
            "wbpc": ["After White Balance Pre-comp"],
            "wb": ["After White Balance"],
            "gsmsf": ["After Gamma",
                      "After Sharpening",
                      "After Gamma + Sharpening",
                      "Laplacian Contrast Weight Map (Gamma)",
                      "Saliency Weight Map (Gamma)",
                      "Saturation Weight Map (Gamma)",
                      "Laplacian Contrast Weight Map (Sharpening)",
                      "Saliency Weight Map (Sharpening)",
                      "Saturation Weight Map (Sharpening)"],
            "fr": ["Final Result"]
        }

        self.view_choices_flattened = [
            "Original", "After White Balance Pre-comp", "After White Balance", "After Gamma", "After Sharpening",
            "After Gamma + Sharpening", "Laplacian Contrast Weight Map (Gamma)", "Saliency Weight Map (Gamma)",
            "Saturation Weight Map (Gamma)", "Laplacian Contrast Weight Map (Sharpening)",
            "Saliency Weight Map (Sharpening)", "Saturation Weight Map (Sharpening)", "Final Result"
        ]

        self.original_choice_groups = list(self.view_choices.keys())
        self.current_choice_groups = self.original_choice_groups.copy()
        self.build_result_combo()

        self.show()

    def load_image(self):
        try:
            self.filename = QFileDialog.getOpenFileName(filter="Képfájlok (*.png *.jpg *.jpeg *.bmp)")[0]
            self.image_original = cv2.imread(self.filename)
            self.make_display_img(self.image_original, 'left')
        except Exception as e:
            print("Nem lett kép kiválasztva, vagy egyéb hiba.")

    def process_image(self):
        if self.image_original is None:
            return

        img_norm = cv2.normalize(self.image_original, None, 0.0, 1.0, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        img_proc = img_norm.copy()

        process_text = "Process:\n"

        # WHITE BALANCE
        if self.check_wb_precomp.isChecked():
            img_proc = comp_for_channel('red', img_norm, alpha=self.alpha_red)
            img_proc = comp_for_channel('blue', img_proc, alpha=self.alpha_blue)

        if self.check_wb.isChecked():
            img_proc = gray_world(img_proc)
            process_text += f"WB Red: {self.alpha_red}, WB Blue: {self.alpha_blue}\n"

        # GAMMA and SHARPENING
        if self.check_gamma_sharp_msf.isChecked():
            img_proc = gamma_correction(img_proc, self.gamma)
            process_text += f"Gamma: {self.gamma}"
            img_proc = unsharp_mask(img_proc, self.sigma, self.strength)
            process_text += f"Sharpening: sigma={self.sigma} strength={self.strength}"

        print(process_text)
        self.image_result = img_proc
        self.make_display_img(self.image_result, 'right')

    def set_alpha_red(self, value):
        # Property
        self.alpha_red = value / 10.0
        # Label
        new_value = str(self.slider_wb_alpha_red.value() / 10.0)
        self.value_wb_alpha_red.setText(new_value)

    def set_alpha_blue(self, value):
        # Property
        self.alpha_blue = value / 10.0
        # Label
        new_value = str(self.slider_wb_alpha_blue.value() / 10.0)
        self.value_wb_alpha_blue.setText(new_value)

    def set_alpha_blue_spinner(self, value):
        self.alpha_blue = value
        self.slider_wb_alpha_blue.setValue(int(self.alpha_blue * 10))

    def set_gamma(self, value):
        self.gamma = value / 10.0
        new_value = str(self.slider_gamma.value() / 10.0)
        self.value_gamma.setText(new_value)

    def set_sigma(self, value):
        self.sigma = value
        new_value = str(self.slider_sharp_sigma.value())
        self.value_sharp_sigma.setText(new_value)

    def set_strength(self, value):
        self.strength = value / 10.0
        new_value = str(self.slider_sharp_strength.value() / 10.0)
        self.value_sharp_strength.setText(new_value)

    def change_result_combo(self, choice: str, checked: bool):
        if checked:
            i = self.original_choice_groups.index(choice)
            self.current_choice_groups.insert(i, choice)
        else:
            self.current_choice_groups.remove(choice)

        self.build_result_combo()

    def build_result_combo(self):
        self.combo_see_stage.clear()
        for group in self.current_choice_groups:
            self.combo_see_stage.addItems(self.view_choices[group])

        self.combo_see_stage.setCurrentIndex(self.combo_see_stage.count() - 1)

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
    UIWindow = UI("image2.ui")
    app.exec_()
