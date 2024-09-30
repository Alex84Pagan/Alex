import flet as ft
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    page.title = "Адаптивное приложение"
    page.window_resizable = True
    page.scroll = "adaptive"

# Имя файла для базы данных
DATABASE_FILE = "plots_data.db"

# Функция для подключения к базе данных SQLite
def connect_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    return conn, cursor

# Инициализация базы данных
def init_db():
    conn, cursor = connect_db()

    # Создание таблицы для участков
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plots (
        plot_number INTEGER PRIMARY KEY,
        owner_name TEXT,
        phone_number TEXT,
        email TEXT,
        is_privatised BOOLEAN
    )
    ''')

    # Создание таблицы для истории платежей
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plot_number INTEGER,
        payment_type TEXT,  -- тип платежа: членский взнос, электричество, вода
        amount REAL,        -- сумма платежа
        payment_date TEXT,  -- дата платежа
        FOREIGN KEY (plot_number) REFERENCES plots(plot_number)
    )
    ''')

    # Создание таблицы для расходов
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_type TEXT,  -- тип расхода
        amount REAL,        -- сумма расхода
        expense_date TEXT   -- дата расхода
    )
    ''')

    conn.commit()
    conn.close()

# Функция для проверки корректности данных
def validate_input(plot_number, owner_name, owner_phone_number, owner_email):
    errors = []
    if not plot_number.isdigit():
        errors.append("Номер участка должен быть числом.")
    if not owner_name:
        errors.append("ФИО владельца не должно быть пустым.")
    if not owner_phone_number.isdigit():
        errors.append("Номер телефона должен содержать только цифры.")
    if '@' not in owner_email or '.' not in owner_email:
        errors.append("Неверный формат email.")
    return errors

# Функция для проверки корректности даты в формате DD/MM/YYYY
def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Функция для сохранения информации о владельце участка
def save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised):
    conn, cursor = connect_db()

    cursor.execute("SELECT * FROM plots WHERE plot_number = ?", (plot_number,))
    plot = cursor.fetchone()

    if plot:
        # Обновление информации о владельце
        cursor.execute('''
            UPDATE plots
            SET owner_name = ?, phone_number = ?, email = ?, is_privatised = ?
            WHERE plot_number = ?
        ''', (owner_name, owner_phone_number, owner_email, is_privatised, plot_number))
    else:
        # Добавление нового участка
        cursor.execute('''
            INSERT INTO plots (plot_number, owner_name, phone_number, email, is_privatised)
            VALUES (?, ?, ?, ?, ?)
        ''', (plot_number, owner_name, owner_phone_number, owner_email, is_privatised))

    conn.commit()
    conn.close()

# Функция для поиска участка по номеру
def find_plot(plot_number):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM plots WHERE plot_number = ?", (plot_number,))
    plot = cursor.fetchone()
    conn.close()

    if plot:
        return {
            "plot_number": plot[0],
            "owner_name": plot[1],
            "phone_number": plot[2],
            "email": plot[3],
            "is_privatised": plot[4],
        }
    return None

# Функция для поиска участка по ФИО владельца
def find_plot_by_owner_name(owner_name):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM plots WHERE owner_name LIKE ?", (f"%{owner_name}%",))
    plot = cursor.fetchone()
    conn.close()

    if plot:
        return {
            "plot_number": plot[0],
            "owner_name": plot[1],
            "phone_number": plot[2],
            "email": plot[3],
            "is_privatised": plot[4],
        }
    return None

# Функция для добавления новой записи о платеже
def add_payment(plot_number, payment_type, amount, payment_date):
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO payments (plot_number, payment_type, amount, payment_date)
        VALUES (?, ?, ?, ?)
    ''', (plot_number, payment_type, amount, payment_date))
    conn.commit()
    conn.close()

# Функция для получения истории платежей для участка
def get_payment_history(plot_number):
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT payment_type, amount, payment_date FROM payments
        WHERE plot_number = ?
        ORDER BY payment_date DESC
    ''', (plot_number,))
    payments = cursor.fetchall()
    conn.close()

    return payments

# Функция для получения общего отчета по платежам за определенный период
def get_total_payments(period_start, period_end):
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT payment_type, SUM(amount) FROM payments
        WHERE payment_date BETWEEN ? AND ?
        AND payment_type != "Показания электросчётчика"
        GROUP BY payment_type
    ''', (period_start, period_end))
    results = cursor.fetchall()

    cursor.execute('''
        SELECT SUM(amount) FROM payments
        WHERE payment_date BETWEEN ? AND ?
        AND payment_type != "Показания электросчётчика"
    ''', (period_start, period_end))
    total_amount = cursor.fetchone()[0] or 0

    conn.close()
    return results, total_amount

# Функция для получения отчета по платежам с деталями: дата, номер участка, тип платежа, сумма
def get_payments_by_date(period_start, period_end):
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT payment_date, plot_number, payment_type, amount 
        FROM payments
        WHERE payment_date BETWEEN ? AND ?
        ORDER BY payment_date ASC
    ''', (period_start, period_end))
    results = cursor.fetchall()
    conn.close()
    return results

# Функция для добавления новой записи о расходе
def add_expense(expense_type, amount, expense_date):
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO expenses (expense_type, amount, expense_date)
        VALUES (?, ?, ?)
    ''', (expense_type, amount, expense_date))
    conn.commit()
    conn.close()

def get_expense_report(period_start, period_end):
    conn, cursor = connect_db()

    # Извлечение данных о расходах с указанием даты
    cursor.execute('''
        SELECT expense_type, expense_date, SUM(amount) 
        FROM expenses
        WHERE expense_date BETWEEN ? AND ?
        GROUP BY expense_type, expense_date
    ''', (period_start, period_end))

    # Извлекаем результаты запроса
    results = cursor.fetchall() or []  # Если данных нет, вернуть пустой список

    # Получение общей суммы расходов за указанный период
    cursor.execute('''
        SELECT SUM(amount) 
        FROM expenses
        WHERE expense_date BETWEEN ? AND ?
    ''', (period_start, period_end))

    total_amount = cursor.fetchone()[0] or 0  # Если данных нет, вернуть 0

    cursor.close()  # Закрытие курсора
    conn.close()  # Закрытие соединения

    return results, total_amount

# Основная функция для интерфейса приложения
def main(page: ft.Page):
    init_db()  # Инициализация базы данных при старте программы

    page.title = "Management System"
    page.scroll = "adaptive"
    output = ft.Text()  # Вывод сообщений

    # Функция переключения темы
    def switch_theme(e):
        page.theme_mode = "dark" if theme_switch.value else "light"
        page.update()

    # Функция поиска участка по номеру или ФИО владельца
    def search_plot(e):
        plot_number = search_plot_input.value.strip()
        owner_name = search_owner_name_input.value.strip()

        plot_info = None
        if plot_number.isdigit():
            plot_info = find_plot(int(plot_number))
        elif owner_name:
            plot_info = find_plot_by_owner_name(owner_name)

        if plot_info:
            payments = get_payment_history(plot_info["plot_number"])
            payment_history = "\n".join([f"Дата: {p[2]} - {p[0]}: {p[1]} " for p in payments])

            output.value = (
                f"Информация о владельце участка {plot_info['plot_number']}:\n"
                f"ФИО: {plot_info['owner_name']}\n"
                f"Телефон: {plot_info['phone_number']}\n"
                f"Email: {plot_info['email']}\n"
                f"Приватизирован: {'Да' if plot_info['is_privatised'] else 'Нет'}\n\n"
                f"История платежей:\n{payment_history}"
            )
        else:
            output.value = "Участок не найден."

        search_plot_input.value = ""
        search_owner_name_input.value = ""
        page.update()

    # Функция обновления информации о участке и добавления платежей
    def update_plot_info(e):
        plot_number = update_plot_number_input.value.strip()
        membership_fee = update_membership_fee_input.value
        meter_reading = update_meter_reading_input.value
        electricity_payment = update_electricity_payment_input.value
        water_payment = update_water_payment_input.value
        payment_date = update_payment_date_input.value

        if not plot_number.isdigit():
            output.value = "Номер участка должен быть числом."
            page.update()
            return

        if not validate_date(payment_date):
            output.value = "Дата должна быть в формате DD/MM/YYYY."
            page.update()
            return

        if membership_fee:
            add_payment(int(plot_number), "Членский взнос", float(membership_fee), payment_date)
        if meter_reading:
            add_payment(int(plot_number), "Показания электросчётчика", float(meter_reading), payment_date)
        if electricity_payment:
            add_payment(int(plot_number), "Оплата за электричество", float(electricity_payment), payment_date)
        if water_payment:
            add_payment(int(plot_number), "Оплата за воду", float(water_payment), payment_date)

        output.value = f"Платежи для участка {plot_number} обновлены."

        update_plot_number_input.value = ""
        update_membership_fee_input.value = ""
        update_meter_reading_input.value = ""
        update_electricity_payment_input.value = ""
        update_water_payment_input.value = ""
        update_payment_date_input.value = ""
        page.update()

    # Функция сохранения данных о владельце участка
    def save_data(e):
        plot_number = plot_number_input.value.strip()
        owner_name = owner_name_input.value
        owner_phone_number = owner_phone_number_input.value
        owner_email = owner_email_input.value
        is_privatised = privatised_checkbox.value

        # Валидация данных
        errors = validate_input(plot_number, owner_name, owner_phone_number, owner_email)
        if errors:
            output.value = "\n".join(errors)
            page.update()
            return

        save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised)
        output.value = f"Информация о владельце для участка {plot_number} сохранена."

        plot_number_input.value = ""
        owner_name_input.value = ""
        owner_phone_number_input.value = ""
        owner_email_input.value = ""
        privatised_checkbox.value = False
        page.update()

    # Функция показа отчета по платежам за определенный период (каждый платеж и общий отчет)
    def show_payment_report(e):
        start_date = report_start_date_input.value.strip()
        end_date = report_end_date_input.value.strip()

        if not validate_date(start_date) or not validate_date(end_date):
            report_output.value = "Дата должна быть в формате DD/MM/YYYY."
            page.update()
            return

        # Подключение к базе данных
        conn, cursor = connect_db()

        # Получаем все платежи за указанный период, включая номер участка
        cursor.execute('''
            SELECT plot_number, payment_type, amount, payment_date FROM payments
            WHERE payment_date BETWEEN ? AND ?
            AND payment_type != "Показания электросчётчика"
            ORDER BY payment_date ASC
        ''', (start_date, end_date))

        payments = cursor.fetchall()

        # Если платежей нет, выводим сообщение
        if not payments:
            report_output.value = "За указанный период платежей не найдено."
            conn.close()
            page.update()
            return

        # Переменная для общей суммы всех платежей
        total_amount = 0

        # Подготовим отчет по каждому платежу
        report_details = "Платежи за период:\n"

        for payment in payments:
            plot_number, payment_type, amount, payment_date = payment
            report_details += f"Дата: {payment_date}, Участок: {plot_number}, Тип: {payment_type}, Сумма: {amount:.2f}\n"
            total_amount += amount  # Суммируем общую сумму платежей

        # Закрываем соединение с базой данных
        conn.close()

        # Общая сумма всех платежей
        report_details += f"\nОбщая сумма платежей за период с {start_date} по {end_date}: {total_amount:.2f}."

        # Обновляем вывод отчета
        report_output.value = report_details

        # Очищаем поля ввода
        report_start_date_input.value = ""
        report_end_date_input.value = ""
        page.update()

    # Функция показа отчета по расходам за определенный период
    def show_expense_report(e):
        start_date = expense_report_start_date_input.value.strip()
        end_date = expense_report_end_date_input.value.strip()

        if not validate_date(start_date) or not validate_date(end_date):
            expense_report_output.value = "Дата должна быть в формате DD/MM/YYYY."
            page.update()
            return

        expense_results, total_amount = get_expense_report(start_date, end_date)

        if expense_results:
            # Изменяем порядок: Дата (r[1]), затем Тип (r[0]) и Сумма (r[2])
            expense_report_output.value = "\n".join([f"Дата: {r[1]}, Тип: {r[0]}, Сумма: {float(r[2]):.2f}" for r in
                                                     expense_results]) + f"\n\nОбщая сумма: {total_amount:.2f}"
        else:
            expense_report_output.value = "Нет данных за указанный период."

        expense_report_start_date_input.value = ""
        expense_report_end_date_input.value = ""
        page.update()

    # Функция добавления расхода
    def add_expense_data(e):
        expense_type = expense_type_input.value.strip()
        amount = expense_amount_input.value
        expense_date = expense_date_input.value

        # Проверка корректности даты
        if not validate_date(expense_date):
            expense_output.value = "Дата должна быть в формате DD/MM/YYYY."
            page.update()
            return

        try:
            # Преобразуем сумму расхода в float
            amount_float = float(amount)
        except ValueError:
            expense_output.value = "Сумма расхода должна быть числом."
            page.update()
            return

        # Добавляем расход в базу данных
        add_expense(expense_type, amount_float, expense_date)
        expense_output.value = f"Расходы добавлены: {expense_type} - {amount_float:.2f} на {expense_date}."

        # Очистка полей ввода
        expense_type_input.value = ""
        expense_amount_input.value = ""
        expense_date_input.value = ""
        page.update()

    theme_switch = ft.Switch(label="Dark Theme", value=False, on_change=switch_theme)

    search_plot_input = ft.TextField(label="Введите номер участка", width=300)
    search_owner_name_input = ft.TextField(label="Введите ФИО владельца", width=300)
    search_button = ft.ElevatedButton("Найти участок по №/ФИО", on_click=search_plot)

    plot_number_input = ft.TextField(label="Номер участка", width=300)
    owner_name_input = ft.TextField(label="ФИО владельца", width=300)
    owner_phone_number_input = ft.TextField(label="Номер телефона", width=300)
    owner_email_input = ft.TextField(label="Email владельца", width=300)
    privatised_checkbox = ft.Checkbox(label="Приватизирован", value=False)
    save_button = ft.ElevatedButton("Сохранить", on_click=save_data)

    update_plot_number_input = ft.TextField(label="Номер участка", width=300)
    update_payment_date_input = ft.TextField(label="Дата платежа (DD/MM/YYYY)", width=300)
    update_membership_fee_input = ft.TextField(label="Членский взнос", width=300)
    update_meter_reading_input = ft.TextField(label="Показания электросчётчика", width=300)
    update_electricity_payment_input = ft.TextField(label="Сумма оплаты за электричество", width=300)
    update_water_payment_input = ft.TextField(label="Сумма оплаты за воду", width=300)
    update_plot_info_button = ft.ElevatedButton("Обновить данные участка", on_click=update_plot_info)

    report_start_date_input = ft.TextField(label="Дата начала периода (DD/MM/YYYY)", width=300)
    report_end_date_input = ft.TextField(label="Дата конца периода (DD/MM/YYYY)", width=300)
    show_report_button = ft.ElevatedButton("Показать отчет по платежам", on_click=show_payment_report)
    report_output = ft.Text()

    expense_type_input = ft.TextField(label="Тип расхода", width=300)
    expense_amount_input = ft.TextField(label="Сумма расхода", width=300)
    expense_date_input = ft.TextField(label="Дата расхода (DD/MM/YYYY)", width=300)
    add_expense_button = ft.ElevatedButton("Добавить расход", on_click=add_expense_data)
    expense_output = ft.Text()

    expense_report_start_date_input = ft.TextField(label="Дата начала периода (DD/MM/YYYY)", width=300)
    expense_report_end_date_input = ft.TextField(label="Дата конца периода (DD/MM/YYYY)", width=300)
    show_expense_report_button = ft.ElevatedButton("Показать отчет по расходам", on_click=show_expense_report)
    expense_report_output = ft.Text()

    page.add(
        ft.Column(
            [
                theme_switch,
                ft.Row(
                    [
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text("Поиск по № или ФИО", size=20, weight=ft.FontWeight.BOLD),
                                    search_plot_input,
                                    search_owner_name_input,
                                    search_button
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                expand=True
                            ),
                            padding=10,
                            expand=True
                        ),
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text("Ввод данных владельца", size=20, weight=ft.FontWeight.BOLD),
                                    plot_number_input,
                                    owner_name_input,
                                    owner_phone_number_input,
                                    owner_email_input,
                                    privatised_checkbox,
                                    save_button
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                expand=True
                            ),
                            padding=10,
                            expand=True
                        ),
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text("Обновление оплаты", size=20, weight=ft.FontWeight.BOLD),
                                    update_plot_number_input,
                                    update_payment_date_input,
                                    update_membership_fee_input,
                                    update_meter_reading_input,
                                    update_electricity_payment_input,
                                    update_water_payment_input,
                                    update_plot_info_button
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                expand=True
                            ),
                            padding=10,
                            expand=True
                        ),
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text("Отчеты по платежам", size=20, weight=ft.FontWeight.BOLD),
                                    report_start_date_input,
                                    report_end_date_input,
                                    show_report_button,
                                    report_output
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                expand=True
                            ),
                            padding=10,
                            expand=True
                        ),
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text("Ввод расхода", size=20, weight=ft.FontWeight.BOLD),
                                    expense_date_input,
                                    expense_type_input,
                                    expense_amount_input,
                                    add_expense_button,
                                    expense_output
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                expand=True
                            ),
                            padding=10,
                            expand=True
                        ),
                        ft.Container(
                            ft.Column(
                                [
                                    ft.Text("Отчет по расходам", size=20, weight=ft.FontWeight.BOLD),
                                    expense_report_start_date_input,
                                    expense_report_end_date_input,
                                    show_expense_report_button,
                                    expense_report_output
                                ],
                                alignment=ft.MainAxisAlignment.START,
                                expand=True
                            ),
                            padding=10,
                            expand=True
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START
                ),
                ft.Divider(height=1, thickness=2, color=ft.colors.BLACK),  # Общая горизонтальная линия
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Информация по платежам:", size=16, weight=ft.FontWeight.BOLD),
                                output
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        ),
                        ft.Column(
                            [
                                ft.Text("Отчеты по платежам:", size=16, weight=ft.FontWeight.BOLD),
                                report_output
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        ),
                        ft.Column(
                            [
                                ft.Text("Информация о расходах:", size=16, weight=ft.FontWeight.BOLD),
                                expense_output
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        ),
                        ft.Column(
                            [
                                ft.Text("Отчет по расходам:", size=16, weight=ft.FontWeight.BOLD),
                                expense_report_output
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    spacing=20,
                    vertical_alignment=ft.CrossAxisAlignment.START
                )
            ],
            expand=True
        )
    )


ft.app(target=main)
