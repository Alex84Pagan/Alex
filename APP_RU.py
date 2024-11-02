import sqlite3  # Импорт встроенной библиотеки для работы с SQLite
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QMessageBox, QComboBox, QTextEdit, QDateEdit)
from PySide6.QtCore import Qt, QDate  # Импорт классов из QtCore
from PySide6.QtGui import QFont  # Импорт класса для работы со шрифтами


# Функция для создания базы данных
def create_database():
    conn = sqlite3.connect('fuel_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS refueling_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_number TEXT NOT NULL,
            fuel_date DATE NOT NULL,
            fuel_card TEXT,
            previous_mileage INTEGER,
            current_mileage INTEGER NOT NULL,
            diesel_liters REAL NOT NULL,
            currency TEXT CHECK(currency IN ('EUR', 'PLN')) NOT NULL,
            diesel_price_per_liter REAL NOT NULL,
            total_diesel_cost REAL NOT NULL,
            full_tank BOOLEAN NOT NULL,
            adblue_liters REAL DEFAULT 0,
            adblue_price_per_liter REAL DEFAULT 0,
            total_adblue_cost REAL DEFAULT 0,
            distance_traveled INTEGER DEFAULT 0,
            average_fuel_consumption REAL DEFAULT 0,
            total_cost_eur REAL DEFAULT 0,
            total_cost_pln REAL DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


class FuelApp(QWidget):
    def __init__(self):
        super().__init__()
        self.is_dark_theme = False
        self.initUI()

    def initUI(self):
        # Основной макет
        main_layout = QVBoxLayout()

        # Кнопка для переключения темы
        self.toggle_theme_button = QPushButton("Light/Dark Theme")
        self.toggle_theme_button.clicked.connect(self.toggle_theme)
        main_layout.addWidget(self.toggle_theme_button)

        # Создание колонки с полями для ввода данных
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("Номер автомобиля"))
        self.vehicle_number_input = QLineEdit()
        input_layout.addWidget(self.vehicle_number_input)

        input_layout.addWidget(QLabel("Дата заправки"))
        self.fuel_date_input = QDateEdit(calendarPopup=True)
        self.fuel_date_input.setDate(QDate.currentDate())
        input_layout.addWidget(self.fuel_date_input)

        input_layout.addWidget(QLabel("Топливная карта"))
        self.fuel_card_input = QLineEdit()
        input_layout.addWidget(self.fuel_card_input)

        input_layout.addWidget(QLabel("Предыдущий пробег"))
        self.previous_mileage_input = QLineEdit()
        input_layout.addWidget(self.previous_mileage_input)

        input_layout.addWidget(QLabel("Текущий пробег"))
        self.current_mileage_input = QLineEdit()
        input_layout.addWidget(self.current_mileage_input)

        input_layout.addWidget(QLabel("Количество литров Diesel"))
        self.diesel_liters_input = QLineEdit()
        input_layout.addWidget(self.diesel_liters_input)

        input_layout.addWidget(QLabel("Валюта"))
        self.currency_dropdown = QComboBox()
        self.currency_dropdown.addItems(["EUR", "PLN"])
        input_layout.addWidget(self.currency_dropdown)

        input_layout.addWidget(QLabel("Цена за литр Diesel"))
        self.diesel_price_per_liter_input = QLineEdit()
        input_layout.addWidget(self.diesel_price_per_liter_input)

        input_layout.addWidget(QLabel("Полный бак?"))
        self.full_tank_input = QComboBox()
        self.full_tank_input.addItems(["Да", "Нет"])
        input_layout.addWidget(self.full_tank_input)

        input_layout.addWidget(QLabel("Количество литров AdBlue"))
        self.adblue_liters_input = QLineEdit()
        input_layout.addWidget(self.adblue_liters_input)

        input_layout.addWidget(QLabel("Цена за литр AdBlue"))
        self.adblue_price_per_liter_input = QLineEdit()
        input_layout.addWidget(self.adblue_price_per_liter_input)

        # Кнопка сохранения данных
        save_button = QPushButton("Сохранить данные")
        save_button.clicked.connect(self.calculate_and_save_data)
        input_layout.addWidget(save_button)

        # Создание колонки для фильтров поиска
        filter_layout = QVBoxLayout()
        filter_layout.addWidget(QLabel("Фильтр: Номер автомобиля"))
        self.vehicle_number_filter = QLineEdit()
        filter_layout.addWidget(self.vehicle_number_filter)

        filter_layout.addWidget(QLabel("Фильтр: Топливная карта"))
        self.fuel_card_filter = QLineEdit()
        filter_layout.addWidget(self.fuel_card_filter)

        filter_layout.addWidget(QLabel("Дата начала"))
        self.start_date_filter = QDateEdit(calendarPopup=True)
        self.start_date_filter.setDate(QDate.currentDate())
        filter_layout.addWidget(self.start_date_filter)

        filter_layout.addWidget(QLabel("Дата окончания"))
        self.end_date_filter = QDateEdit(calendarPopup=True)
        self.end_date_filter.setDate(QDate.currentDate())
        filter_layout.addWidget(self.end_date_filter)

        # Кнопка для поиска
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.search_data)
        filter_layout.addWidget(search_button)

        # Горизонтальный макет для колонок
        columns_layout = QHBoxLayout()
        columns_layout.addLayout(input_layout)
        columns_layout.addLayout(filter_layout)

        # Добавление колонок в основной макет
        main_layout.addLayout(columns_layout)

        # Поле для вывода информации
        main_layout.addWidget(QLabel("Результаты поиска:"))
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setStyleSheet("border: 2px solid red; padding: 5px;")
        main_layout.addWidget(self.output_text)

        # Установка основного макета
        self.setLayout(main_layout)
        self.setWindowTitle("Интерфейс управления топливом")
        self.setGeometry(200, 200, 800, 1000)

    # Функция переключения темы
    def toggle_theme(self):
        if self.is_dark_theme:
            self.set_light_theme()
        else:
            self.set_dark_theme()
        self.is_dark_theme = not self.is_dark_theme

    # Функция установки светлой темы
    def set_light_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: white; color: black; }
            QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QDateEdit { color: black; }
        """)

    # Функция установки темной темы
    def set_dark_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #333333; color: white; }
            QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit, QDateEdit { color: white; }
        """)

    # Функция поиска данных
    def search_data(self):
        try:
            vehicle_number = self.vehicle_number_filter.text()
            fuel_card = self.fuel_card_filter.text()
            start_date = self.start_date_filter.date().toString("yyyy-MM-dd")
            end_date = self.end_date_filter.date().toString("yyyy-MM-dd")

            query = '''
                    SELECT vehicle_number, fuel_date, fuel_card, previous_mileage, current_mileage,
                       diesel_liters, currency, diesel_price_per_liter, total_diesel_cost,
                       full_tank, adblue_liters, adblue_price_per_liter, total_adblue_cost,
                       distance_traveled, average_fuel_consumption, total_cost_eur, total_cost_pln
                FROM refueling_data
                WHERE (vehicle_number = ? OR ? = '')
                  AND (fuel_card = ? OR ? = '')
                  AND (fuel_date BETWEEN ? AND ?)
                '''
            parameters = (vehicle_number, vehicle_number, fuel_card, fuel_card, start_date, end_date)

            conn = sqlite3.connect('fuel_data.db')
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            results = cursor.fetchall()
            conn.close()

            if results:
                output_text = ""
                for row in results:
                    output_text += (
                        f"Номер машины: {row[0]}, "
                        f"Дата заправки: {row[1]}, "
                        f"Топливная карта: {row[2]}, "
                        f"Предыдущий пробег: {row[3]}, "
                        f"Текущий пробег: {row[4]}, "
                        f"Количество литров Diesel: {row[5]}, "
                        f"Валюта: {row[6]}, "
                        f"Цена за литр Diesel: {row[7]}, "
                        f"Общая стоимость Diesel: {row[8]}, "
                        f"Полный бак: {row[9]}, "
                        f"Количество литров AdBlue: {row[10]}, "
                        f"Цена за литр AdBlue: {row[11]}, "
                        f"Общая стоимость AdBlue: {row[12]}, "
                        f"Пройденный километраж: {row[13]}, "
                        f"Средний расход топлива: {row[14]}\n "
                        "------------------------------------------------------------------------------------------------------------\n"
                    )
                self.output_text.setPlainText(output_text)

                # Изменение шрифта и его размера
                font = QFont()
                font.setPointSize(14)  # Установка размера шрифта
                self.output_text.setFont(font)  # Применение шрифта к QPlainTextEdit
            else:
                QMessageBox.information(self, "Результаты поиска", "Данные не найдены.")
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Ошибка базы данных", str(e))

    # Функция для вычисления и сохранения данных
    def calculate_and_save_data(self):
        try:
            vehicle_number = self.vehicle_number_input.text()
            fuel_date = self.fuel_date_input.date().toString("yyyy-MM-dd")
            fuel_card = self.fuel_card_input.text()
            previous_mileage = int(self.previous_mileage_input.text())
            current_mileage = int(self.current_mileage_input.text())
            diesel_liters = float(self.diesel_liters_input.text())
            currency = self.currency_dropdown.currentText()
            diesel_price_per_liter = float(self.diesel_price_per_liter_input.text())
            full_tank = self.full_tank_input.currentText() == "Да"
            adblue_liters = float(self.adblue_liters_input.text()) if self.adblue_liters_input.text() else 0
            adblue_price_per_liter = float(self.adblue_price_per_liter_input.text()) if self.adblue_price_per_liter_input.text() else 0

            total_diesel_cost = diesel_liters * diesel_price_per_liter
            total_adblue_cost = adblue_liters * adblue_price_per_liter

            # Пройденный километраж
            distance_traveled = current_mileage - previous_mileage
            average_fuel_consumption = (diesel_liters / distance_traveled) * 100 if distance_traveled > 0 else 0

            # Сохранение данных в базу данных
            conn = sqlite3.connect('fuel_data.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO refueling_data (vehicle_number, fuel_date, fuel_card, previous_mileage,
                current_mileage, diesel_liters, currency, diesel_price_per_liter, total_diesel_cost,
                full_tank, adblue_liters, adblue_price_per_liter, total_adblue_cost,
                distance_traveled, average_fuel_consumption)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (vehicle_number, fuel_date, fuel_card, previous_mileage, current_mileage,
                  diesel_liters, currency, diesel_price_per_liter, total_diesel_cost, full_tank,
                  adblue_liters, adblue_price_per_liter, total_adblue_cost,
                  distance_traveled, average_fuel_consumption))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Успех", "Данные успешно сохранены.")
            self.clear_inputs()
        except (ValueError, sqlite3.Error) as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    # Функция очистки полей ввода
    def clear_inputs(self):
        self.vehicle_number_input.clear()
        self.fuel_date_input.setDate(QDate.currentDate())
        self.fuel_card_input.clear()
        self.previous_mileage_input.clear()
        self.current_mileage_input.clear()
        self.diesel_liters_input.clear()
        self.diesel_price_per_liter_input.clear()
        self.full_tank_input.setCurrentIndex(0)
        self.adblue_liters_input.clear()
        self.adblue_price_per_liter_input.clear()


if __name__ == '__main__':
    create_database()  # Создание базы данных
    app = QApplication([])
    window = FuelApp()
    window.show()
    app.exec()
