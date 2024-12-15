import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QCheckBox, QGroupBox, QMessageBox, QRadioButton, QButtonGroup,
    QDateEdit
)
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from fpdf import FPDF
import os

FONT_PATH = "Roboto-Regular.ttf"

BASE_PRICE_PER_M2_REGULAR = 50
BASE_PRICE_PER_M2_GENERAL = 70
BASE_PRICE_PER_M2_POST_CONSTRUCTION = 100

EXTRA_SERVICES = {
    "Дезинфекция": 2000,
    "Дезинсекция": 2000,
    "Дератизация": 2000,
    "Химчистка мебели": 1600,
    "Химчистка ковров": 1000,
    "Мойка фасадов": 0,
    "Мойка окон": 650,
    "Глажка белья": 600,
    "Мойка духовки": 800,
    "Мойка микроволновки": 300,
    "Мойка холодильника": 600,
    "Освежить шторы парогенератором": 700,
    "Мойка люстр": 600,
    "Эко уборка": 1000,
}

class CleaningCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Калькулятор расчёта уборки")
        self.setGeometry(100, 100, 400, 700)
        self.total_cost = 0
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Поле для ввода площади
        area_layout = QHBoxLayout()
        label_area = QLabel("Площадь (м²):")
        self.entry_area = QLineEdit()
        self.entry_area.setPlaceholderText("Введите площадь")
        area_layout.addWidget(label_area)
        area_layout.addWidget(self.entry_area)
        main_layout.addLayout(area_layout)
    
        # Поле для выбора даты уборки (Date Picker)
        date_layout = QHBoxLayout()
        label_date = QLabel("Дата уборки:")
        self.entry_date = QDateEdit()
        self.entry_date.setCalendarPopup(True)
        self.entry_date.setDate(QDate.currentDate())
        self.entry_date.setDisplayFormat("dd.MM.yyyy")
        date_layout.addWidget(label_date)
        date_layout.addWidget(self.entry_date)
        main_layout.addLayout(date_layout)

        # Группа радиокнопок для выбора типа уборки
        cleaning_type_group = QGroupBox("Тип уборки")
        cleaning_type_layout = QVBoxLayout()

        self.radio_regular = QRadioButton("Поддерживающий")
        self.radio_general = QRadioButton("Генеральный")
        self.radio_post_construction = QRadioButton("Послестроительный")

        self.radio_regular.setChecked(True)

        cleaning_type_layout.addWidget(self.radio_regular)
        cleaning_type_layout.addWidget(self.radio_general)
        cleaning_type_layout.addWidget(self.radio_post_construction)

        cleaning_type_group.setLayout(cleaning_type_layout)
        main_layout.addWidget(cleaning_type_group)

        self.cleaning_type_buttons = QButtonGroup()
        self.cleaning_type_buttons.addButton(self.radio_regular)
        self.cleaning_type_buttons.addButton(self.radio_general)
        self.cleaning_type_buttons.addButton(self.radio_post_construction)

        # Дополнительные услуги (чекбоксы)
        services_group = QGroupBox("Дополнительные услуги")
        services_layout = QVBoxLayout()
        self.service_checkboxes = {}
        for service in EXTRA_SERVICES:
            checkbox = QCheckBox(service)
            services_layout.addWidget(checkbox)
            self.service_checkboxes[service] = checkbox
        services_group.setLayout(services_layout)
        main_layout.addWidget(services_group)

        # Кнопка для расчёта итоговой стоимости
        self.btn_calculate = QPushButton("Рассчитать")
        self.btn_calculate.clicked.connect(self.calculate_total)
        main_layout.addWidget(self.btn_calculate)

        # Кнопка для сохранения расчёта в PDF
        self.btn_save_pdf = QPushButton("Сохранить расчёт в PDF")
        self.btn_save_pdf.clicked.connect(self.save_to_pdf)
        main_layout.addWidget(self.btn_save_pdf)

        # Поле для отображения итоговой суммы
        self.label_total = QLabel("Итого: 0 руб.")
        self.label_total.setAlignment(Qt.AlignCenter)
        self.label_total.setStyleSheet("font-size: 16px;")
        main_layout.addWidget(self.label_total)

        self.setLayout(main_layout)

    def calculate_total(self):
        try:
            area_text = self.entry_area.text()
            area = float(area_text)
            if area <= 0:
                raise ValueError("Площадь должна быть больше 0")

            if self.radio_regular.isChecked():
                base_price = BASE_PRICE_PER_M2_REGULAR
            elif self.radio_general.isChecked():
                base_price = BASE_PRICE_PER_M2_GENERAL
            elif self.radio_post_construction.isChecked():
                base_price = BASE_PRICE_PER_M2_POST_CONSTRUCTION
            else:
                raise ValueError("Выберите тип уборки")

            self.total_cost = area * base_price

            for service, checkbox in self.service_checkboxes.items():
                if checkbox.isChecked():
                    self.total_cost += EXTRA_SERVICES[service]

            selected_date = self.entry_date.date().toPyDate()
            today = datetime.today().date()
            delta_days = (selected_date - today).days

            if delta_days < 0:
                raise ValueError("Дата уборки не может быть в прошлом")

            if delta_days <= 30:
                surcharge = (30 - delta_days) * 0.02 * self.total_cost
                self.total_cost += surcharge

            self.label_total.setText(f"Итого: {self.total_cost:.2f} руб.")
        except ValueError as ve:
            QMessageBox.critical(self, "Ошибка", str(ve))
        except Exception:
            QMessageBox.critical(self, "Ошибка", "Введите корректные данные.")

    def save_to_pdf(self):
        file_name = "cleaning_calculation.pdf"
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.add_font('Roboto', '', FONT_PATH, uni=True)
            pdf.set_font('Roboto', '', 14)

            # Добавляем текст в PDF, приводя значения к строковому типу
            pdf.cell(0, 10, "Расчёт стоимости уборки", ln=True)
            pdf.cell(0, 10, f"Площадь: {str(self.entry_area.text())} м²", ln=True)
            pdf.cell(0, 10, f"Дата уборки: {str(self.entry_date.text())}", ln=True)
            pdf.cell(0, 10, f"Итоговая стоимость: {str(self.label_total.text())}", ln=True)

            pdf.output(file_name)
            QMessageBox.information(self, "Успех", f"Расчёт сохранён в файл {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении PDF: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = CleaningCalculator()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
