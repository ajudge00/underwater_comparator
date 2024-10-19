from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QSlider, QLabel, QFileDialog, QCheckBox, \
    QDoubleSpinBox, QComboBox
from PyQt5.QtGui import QImage
from PyQt5 import uic, QtGui
import numpy as np
import imutils
import cv2
import sys


class GUI(QMainWindow):
    def __init__(self, ui_path):
        super(GUI, self).__init__()

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

        self.check_wb_precomp.stateChanged.connect(
            lambda: self.change_result_combo("wbpc", self.check_wb_precomp.isChecked())
        )
        self.check_wb.stateChanged.connect(
            lambda: self.change_result_combo("wb", self.check_wb.isChecked())
        )
        self.check_gamma_sharp_msf.stateChanged.connect(
            lambda: self.change_result_combo("gsmsf", self.check_gamma_sharp_msf.isChecked())
        )

        self.original_choice_groups = list(self.view_choices.keys())
        self.current_choice_groups = self.original_choice_groups.copy()
        self.build_result_combo()

        self.show()

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
