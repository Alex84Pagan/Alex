import flet as ft
import sqlite3
from datetime import datetime

def main(page: ft.Page):
    page.title = "Адаптивний додаток"
    page.window_resizable = True
    page.scroll = "adaptive"

# Назва файлу для бази даних
DATABASE_FILE = "plots_data.db"

# Функція для підключення до бази даних SQLite
def connect_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    return conn, cursor

# Ініціалізація бази даних
def init_db():
    conn, cursor = connect_db()

    # Створення таблиці для ділянок
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS plots (
        plot_number INTEGER PRIMARY KEY,
        owner_name TEXT,
        phone_number TEXT,
        email TEXT,
        is_privatised BOOLEAN
    )
    ''')

    # Створення таблиці для історії платежів
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        plot_number INTEGER,
        payment_type TEXT,  -- тип платежу: членський внесок, електрика, вода
        amount REAL,        -- сума платежу
        payment_date TEXT,  -- дата платежу
        FOREIGN KEY (plot_number) REFERENCES plots(plot_number)
    )
    ''')

    # Створення таблиці для витрат
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expenses (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_type TEXT,  -- тип витрат
        amount REAL,        -- сума витрат
        expense_date TEXT   -- дата витрат
    )
    ''')

    conn.commit()
    conn.close()

# Функція для перевірки коректності даних
def validate_input(plot_number, owner_name, owner_phone_number, owner_email):
    errors = []
    if not plot_number.isdigit():
        errors.append("Номер ділянки має бути числом.")
    if not owner_name:
        errors.append("ПІБ власника не може бути порожнім.")
    if not owner_phone_number.isdigit():
        errors.append("Номер телефону має містити тільки цифри.")
    if '@' not in owner_email or '.' not in owner_email:
        errors.append("Невірний формат email.")
    return errors

# Функція для перевірки коректності дати в форматі DD/MM/YYYY
def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Функція для збереження інформації про власника ділянки
def save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised):
    conn, cursor = connect_db()

    cursor.execute("SELECT * FROM plots WHERE plot_number = ?", (plot_number,))
    plot = cursor.fetchone()

    if plot:
        # Оновлення інформації про власника
        cursor.execute('''
            UPDATE plots
            SET owner_name = ?, phone_number = ?, email = ?, is_privatised = ?
            WHERE plot_number = ?
        ''', (owner_name, owner_phone_number, owner_email, is_privatised, plot_number))
    else:
        # Додавання нової ділянки
        cursor.execute('''
            INSERT INTO plots (plot_number, owner_name, phone_number, email, is_privatised)
            VALUES (?, ?, ?, ?, ?)
        ''', (plot_number, owner_name, owner_phone_number, owner_email, is_privatised))

    conn.commit()
    conn.close()

# Функція для пошуку ділянки за номером
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

# Функція для пошуку ділянки за ПІБ власника
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

# Функція для додавання нового запису про платіж
def add_payment(plot_number, payment_type, amount, payment_date):
    conn, cursor = connect_db()
    cursor.execute('''
        INSERT INTO payments (plot_number, payment_type, amount, payment_date)
        VALUES (?, ?, ?, ?)
    ''', (plot_number, payment_type, amount, payment_date))
    conn.commit()
    conn.close()

# Функція для отримання історії платежів для ділянки
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

# Функція для отримання загального звіту про платежі за певний період
def get_total_payments(period_start, period_end):
    conn, cursor = connect_db()
    cursor.execute('''
        SELECT payment_type, SUM(amount) FROM payments
        WHERE payment_date BETWEEN ? AND ?
        AND payment_type != "Показання електролічильника"
        GROUP BY payment_type
    ''', (period_start, period_end))
    results = cursor.fetchall()

    cursor.execute('''
        SELECT SUM(amount) FROM payments
        WHERE payment_date BETWEEN ? AND ?
        AND payment_type != "Показання електролічильника"
    ''', (period_start, period_end))
    total_amount = cursor.fetchone()[0] or 0

    conn.close()
    return results, total_amount

# Функція для отримання звіту про платежі з деталями: дата, номер ділянки, тип платежу, сума
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

# Функція для додавання нового запису про витрату
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

    # Витяг даних про витрати з вказанням дати
    cursor.execute('''
        SELECT expense_type, expense_date, SUM(amount) 
        FROM expenses
        WHERE expense_date BETWEEN ? AND ?
        GROUP BY expense_type, expense_date
    ''', (period_start, period_end))

    # Витягуємо результати запиту
    results = cursor.fetchall() or []  # Якщо даних немає, повернути порожній список

    # Отримання загальної суми витрат за вказаний період
    cursor.execute('''
        SELECT SUM(amount) 
        FROM expenses
        WHERE expense_date BETWEEN ? AND ?
    ''', (period_start, period_end))

    total_amount = cursor.fetchone()[0] or 0  # Якщо даних немає, повернути 0

    cursor.close()  # Закриття курсора
    conn.close()  # Закриття з'єднання

    return results, total_amount

# Основна функція для інтерфейсу програми
def main(page: ft.Page):
    init_db()  # Ініціалізація бази даних при старті програми

    page.title = "Система управління"
    page.scroll = "adaptive"
    output = ft.Text()  # Виведення повідомлень

    # Функція перемикання теми
    def switch_theme(e):
        page.theme_mode = "dark" if theme_switch.value else "light"
        page.update()

    # Функція пошуку ділянки за номером або ПІБ власника
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
                f"Інформація про власника ділянки {plot_info['plot_number']}:\n"
                f"ПІБ: {plot_info['owner_name']}\n"
                f"Телефон: {plot_info['phone_number']}\n"
                f"Email: {plot_info['email']}\n"
                f"Приватизовано: {'Так' if plot_info['is_privatised'] else 'Ні'}\n\n"
                f"Історія платежів:\n{payment_history}"
            )
        else:
            output.value = "Ділянка не знайдена."

        search_plot_input.value = ""
        search_owner_name_input.value = ""
        page.update()

    # Функція оновлення інформації про ділянку та додавання платежів
    def update_plot_info(e):
        plot_number = update_plot_number_input.value.strip()
        membership_fee = update_membership_fee_input.value
        meter_reading = update_meter_reading_input.value
        electricity_payment = update_electricity_payment_input.value
        water_payment = update_water_payment_input.value
        payment_date = update_payment_date_input.value

        if not plot_number.isdigit():
            output.value = "Номер ділянки має бути числом."
            page.update()
            return

        if not validate_date(payment_date):
            output.value = "Дата має бути в форматі DD/MM/YYYY."
            page.update()
            return

        if membership_fee:
            add_payment(int(plot_number), "Членський внесок", float(membership_fee), payment_date)
        if meter_reading:
            add_payment(int(plot_number), "Показання електролічильника", float(meter_reading), payment_date)
        if electricity_payment:
            add_payment(int(plot_number), "Оплата за електрику", float(electricity_payment), payment_date)
        if water_payment:
            add_payment(int(plot_number), "Оплата за воду", float(water_payment), payment_date)

        output.value = f"Платежі для ділянки {plot_number} оновлені."

        update_plot_number_input.value = ""
        update_membership_fee_input.value = ""
        update_meter_reading_input.value = ""
        update_electricity_payment_input.value = ""
        update_water_payment_input.value = ""
        update_payment_date_input.value = ""
        page.update()

    # Функція збереження даних про власника ділянки
    def save_data(e):
        plot_number = plot_number_input.value.strip()
        owner_name = owner_name_input.value
        owner_phone_number = owner_phone_number_input.value
        owner_email = owner_email_input.value
        is_privatised = privatised_checkbox.value

        # Валідація даних
        errors = validate_input(plot_number, owner_name, owner_phone_number, owner_email)
        if errors:
            output.value = "\n".join(errors)
            page.update()
            return

        save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised)
        output.value = f"Інформація про власника для ділянки {plot_number} збережена."

        plot_number_input.value = ""
        owner_name_input.value = ""
        owner_phone_number_input.value = ""
        owner_email_input.value = ""
        privatised_checkbox.value = False
        page.update()

    # Функція показу звіту по платежах за визначений період (кожен платіж і загальний звіт)
    def show_payment_report(e):
        start_date = report_start_date_input.value.strip()
        end_date = report_end_date_input.value.strip()

        if not validate_date(start_date) or not validate_date(end_date):
            report_output.value = "Дата має бути в форматі DD/MM/YYYY."
            page.update()
            return

        # Підключення до бази даних
        conn, cursor = connect_db()

        # Отримуємо всі платежі за вказаний період, включаючи номер ділянки
        cursor.execute('''
            SELECT plot_number, payment_type, amount, payment_date FROM payments
            WHERE payment_date BETWEEN ? AND ?
            AND payment_type != "Показання електролічильника"
            ORDER BY payment_date ASC
        ''', (start_date, end_date))

        payments = cursor.fetchall()

        # Якщо платежів немає, виводимо повідомлення
        if not payments:
            report_output.value = "За вказаний період платежів не знайдено."
            conn.close()
            page.update()
            return

        # Змінна для загальної суми всіх платежів
        total_amount = 0

        # Підготовка звіту по кожному платежу
        report_details = "Платежі за період:\n"

        for payment in payments:
            plot_number, payment_type, amount, payment_date = payment
            report_details += f"Дата: {payment_date}, Ділянка: {plot_number}, Тип: {payment_type}, Сума: {amount:.2f}\n"
            total_amount += amount  # Підсумовуємо загальну суму платежів

        # Закриття з'єднання з базою даних
        conn.close()

        # Загальна сума всіх платежів
        report_details += f"\nЗагальна сума платежів за період з {start_date} по {end_date}: {total_amount:.2f}."

        # Оновлюємо виведення звіту
        report_output.value = report_details

        # Очищення полів вводу
        report_start_date_input.value = ""
        report_end_date_input.value = ""
        page.update()

    # Функція показу звіту по витратах за визначений період
    def show_expense_report(e):
        start_date = expense_report_start_date_input.value.strip()
        end_date = expense_report_end_date_input.value.strip()

        if not validate_date(start_date) or not validate_date(end_date):
            expense_report_output.value = "Дата має бути в форматі DD/MM/YYYY."
            page.update()
            return

        expense_results, total_amount = get_expense_report(start_date, end_date)

        if expense_results:
            # Зміна порядку: Дата (r[1]), потім Тип (r[0]) і Сума (r[2])
            expense_report_output.value = "\n".join([f"Дата: {r[1]}, Тип: {r[0]}, Сума: {float(r[2]):.2f}" for r in
                                                     expense_results]) + f"\n\nЗагальна сума: {total_amount:.2f}"
        else:
            expense_report_output.value = "Даних за вказаний період немає."

        expense_report_start_date_input.value = ""
        expense_report_end_date_input.value = ""
        page.update()

    # Функція додавання витрат
    def add_expense_data(e):
        expense_type = expense_type_input.value.strip()
        amount = expense_amount_input.value
        expense_date = expense_date_input.value

        # Перевірка коректності дати
        if not validate_date(expense_date):
            expense_output.value = "Дата має бути в форматі DD/MM/YYYY."
            page.update()
            return

        try:
            # Перетворюємо суму витрат у float
            amount_float = float(amount)
        except ValueError:
            expense_output.value = "Сума витрат має бути числом."
            page.update()
            return

        # Додаємо витрати до бази даних
        add_expense(expense_type, amount_float, expense_date)
        expense_output.value = f"Витрати додані: {expense_type} - {amount_float:.2f} на {expense_date}."

        # Очищення полів вводу
        expense_type_input.value = ""
        expense_amount_input.value = ""
        expense_date_input.value = ""
        page.update()

    theme_switch = ft.Switch(label="Dark", value=False, on_change=switch_theme)

    search_plot_input = ft.TextField(label="Введіть номер ділянки", width=300)
    search_owner_name_input = ft.TextField(label="Введіть ПІБ власника", width=300)
    search_button = ft.ElevatedButton("Знайти ділянку за №/ПІБ", on_click=search_plot)

    plot_number_input = ft.TextField(label="Номер ділянки", width=300)
    owner_name_input = ft.TextField(label="ПІБ власника", width=300)
    owner_phone_number_input = ft.TextField(label="Номер телефону", width=300)
    owner_email_input = ft.TextField(label="Email власника", width=300)
    privatised_checkbox = ft.Checkbox(label="Приватизовано", value=False)
    save_button = ft.ElevatedButton("Зберегти", on_click=save_data)

    update_plot_number_input = ft.TextField(label="Номер ділянки", width=300)
    update_payment_date_input = ft.TextField(label="Дата платежу (DD/MM/YYYY)", width=300)
    update_membership_fee_input = ft.TextField(label="Членський внесок", width=300)
    update_meter_reading_input = ft.TextField(label="Показання електролічильника", width=300)
    update_electricity_payment_input = ft.TextField(label="Сума оплати за електрику", width=300)
    update_water_payment_input = ft.TextField(label="Сума оплати за воду", width=300)
    update_plot_info_button = ft.ElevatedButton("Оновити дані ділянки", on_click=update_plot_info)

    report_start_date_input = ft.TextField(label="Дата початку періоду (DD/MM/YYYY)", width=300)
    report_end_date_input = ft.TextField(label="Дата кінця періоду (DD/MM/YYYY)", width=300)
    show_report_button = ft.ElevatedButton("Показати звіт по платежах", on_click=show_payment_report)
    report_output = ft.Text()

    expense_type_input = ft.TextField(label="Тип витрат", width=300)
    expense_amount_input = ft.TextField(label="Сума витрат", width=300)
    expense_date_input = ft.TextField(label="Дата витрат (DD/MM/YYYY)", width=300)
    add_expense_button = ft.ElevatedButton("Додати витрати", on_click=add_expense_data)
    expense_output = ft.Text()

    expense_report_start_date_input = ft.TextField(label="Дата початку періоду (DD/MM/YYYY)", width=300)
    expense_report_end_date_input = ft.TextField(label="Дата кінця періоду (DD/MM/YYYY)", width=300)
    show_expense_report_button = ft.ElevatedButton("Показати звіт по витратах", on_click=show_expense_report)
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
                                    ft.Text("Пошук за № або ПІБ", size=20, weight=ft.FontWeight.BOLD),
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
                                    ft.Text("Введення даних власника", size=20, weight=ft.FontWeight.BOLD),
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
                                    ft.Text("Оновлення оплати", size=20, weight=ft.FontWeight.BOLD),
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
                                    ft.Text("Звіти по платежах", size=20, weight=ft.FontWeight.BOLD),
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
                                    ft.Text("Введення витрат", size=20, weight=ft.FontWeight.BOLD),
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
                                    ft.Text("Звіт по витратах", size=20, weight=ft.FontWeight.BOLD),
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
                ft.Divider(height=1, thickness=2, color=ft.colors.BLACK),  # Загальна горизонтальна лінія
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Інформація по платежах:", size=16, weight=ft.FontWeight.BOLD),
                                output
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        ),
                        ft.Column(
                            [
                                ft.Text("Звіти по платежах:", size=16, weight=ft.FontWeight.BOLD),
                                report_output
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        ),
                        ft.Column(
                            [
                                ft.Text("Інформація по витратах:", size=16, weight=ft.FontWeight.BOLD),
                                expense_output
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            expand=True
                        ),
                        ft.Column(
                            [
                                ft.Text("Звіт по витратах:", size=16, weight=ft.FontWeight.BOLD),
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