import flet as ft

# Ім'я файлу для збереження даних
DATA_FILE = "plots_data.txt"

# База даних ділянок (завантажується з файлу)
plots = []

def load_data():
    """Завантаження даних з файлу у список plots."""
    try:
        with open(DATA_FILE, "r") as file:
            for line in file:
                fields = line.strip().split(",")
                plot = {
                    "plot_number": int(fields[0]),
                    "owner_name": fields[1],
                    "phone_number": fields[2],
                    "email": fields[3],
                    "is_privatised": fields[4].lower() == 'true',
                    "membership_fee": float(fields[5]),
                    "electric_meter_reading": float(fields[6]),
                    "electricity_payment": float(fields[7]),
                    "water_payment": float(fields[8])
                }
                plots.append(plot)
    except FileNotFoundError:
        pass

def save_to_file():
    """Збереження даних зі списку plots у файл."""
    with open(DATA_FILE, "w") as file:
        for plot in plots:
            file.write(f"{plot['plot_number']},{plot['owner_name']},{plot['phone_number']},"
                       f"{plot['email']},{plot['is_privatised']},{plot['membership_fee']},"
                       f"{plot['electric_meter_reading']},{plot['electricity_payment']},"
                       f"{plot['water_payment']}\n")

def save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised):
    """Додавання нової ділянки до списку plots і збереження у файл."""
    plot = {
        "plot_number": plot_number,
        "owner_name": owner_name,
        "phone_number": owner_phone_number,
        "email": owner_email,
        "is_privatised": is_privatised,
        "membership_fee": 0,
        "electric_meter_reading": 0,
        "electricity_payment": 0,
        "water_payment": 0
    }
    plots.append(plot)
    save_to_file()

def find_plot(plot_number):
    """Пошук ділянки за номером."""
    for plot in plots:
        if plot["plot_number"] == plot_number:
            return plot
    return None

def find_plot_by_owner_name(owner_name):
    """Пошук ділянки за ПІБ власника."""
    for plot in plots:
        if plot["owner_name"].lower() == owner_name.lower():
            return plot
    return None

def update_plot_data(plot_number, membership_fee, meter_reading, electricity_payment, water_payment):
    """Оновлення членських внесків, показань лічильника, оплати за електроенергію та воду для ділянки."""
    plot = find_plot(plot_number)
    if plot:
        plot["membership_fee"] = membership_fee
        plot["electric_meter_reading"] = meter_reading
        plot["electricity_payment"] = electricity_payment
        plot["water_payment"] = water_payment
        save_to_file()
        return True
    return False

def main(page: ft.Page):
    load_data()  # Завантажуємо дані з файлу при старті програми

    page.title = "Система управління ділянками"
    page.scroll = "adaptive"

    # Перемикач для теми
    def switch_theme(e):
        if theme_switch.value:
            page.theme_mode = "dark"
        else:
            page.theme_mode = "light"
        page.update()

    # Функція для пошуку ділянки за номером або ПІБ власника
    def search_plot(e):
        plot_number = search_plot_input.value.strip()
        owner_name = search_owner_name_input.value.strip()

        plot_info = None
        if plot_number.isdigit():
            plot_info = find_plot(int(plot_number))
        elif owner_name:
            plot_info = find_plot_by_owner_name(owner_name)

        if plot_info:
            output.value = (
                f"Інформація про власника ділянки {plot_info['plot_number']}:\n"
                f"ПІБ: {plot_info['owner_name']}\n"
                f"Телефон: {plot_info['phone_number']}\n"
                f"Email: {plot_info['email']}\n"
                f"Приватизовано: {'Так' if plot_info['is_privatised'] else 'Ні'}\n"
                f"Членський внесок: {plot_info['membership_fee']}\n"
                f"Показання лічильника: {plot_info['electric_meter_reading']}\n"
                f"Оплата за електроенергію: {plot_info['electricity_payment']}\n"
                f"Оплата за воду: {plot_info['water_payment']}"
            )
        else:
            output.value = "Ділянка не знайдена."

        # Очищення полів після пошуку
        search_plot_input.value = ""
        search_owner_name_input.value = ""
        page.update()

    # Функція для оновлення всіх даних по ділянці
    def update_plot_info(e):
        plot_number = int(update_plot_number_input.value)
        membership_fee = float(update_membership_fee_input.value)
        meter_reading = float(update_meter_reading_input.value)
        electricity_payment = float(update_electricity_payment_input.value)
        water_payment = float(update_water_payment_input.value)

        if update_plot_data(plot_number, membership_fee, meter_reading, electricity_payment, water_payment):
            output.value = f"Дані для ділянки {plot_number} оновлено."
        else:
            output.value = "Ділянка не знайдена."

        # Очищення полів після оновлення
        update_plot_number_input.value = ""
        update_membership_fee_input.value = ""
        update_meter_reading_input.value = ""
        update_electricity_payment_input.value = ""
        update_water_payment_input.value = ""
        page.update()

    # Функція для обробки натискання на кнопку "Зберегти"
    def save_data(e):
        plot_number = int(plot_number_input.value)
        owner_name = owner_name_input.value
        owner_phone_number = owner_phone_number_input.value
        owner_email = owner_email_input.value
        is_privatised = privatised_checkbox.value

        save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised)

        output.value = f"Дані ділянки {plot_number} збережено!"

        # Очищення полів після збереження
        plot_number_input.value = ""
        owner_name_input.value = ""
        owner_phone_number_input.value = ""
        owner_email_input.value = ""
        privatised_checkbox.value = False
        page.update()

    # Перемикач для темної теми
    theme_switch = ft.Switch(label="Темна тема", value=False, on_change=switch_theme)

    # Функція для калькулятора
    def calculate(e):
        try:
            expression = calc_input.value
            result = eval(expression)
            calc_output.value = str(result)
        except Exception as ex:
            calc_output.value = f"Помилка: {ex}"
        page.update()

    # Калькулятор
    calc_input = ft.TextField(label="Введіть вираз", width=300)
    calc_button = ft.ElevatedButton("Порахувати", on_click=calculate)
    calc_output = ft.Text()

    # Пошук ділянки за номером або ПІБ
    search_plot_input = ft.TextField(label="Введіть номер ділянки", width=300)
    search_owner_name_input = ft.TextField(label="Введіть ПІБ власника", width=300)
    search_button = ft.ElevatedButton("Знайти ділянку за №/ПІБ", on_click=search_plot)

    # Оновлення даних ділянки
    update_plot_number_input = ft.TextField(label="Номер ділянки", width=300)
    update_membership_fee_input = ft.TextField(label="Членський внесок", width=300)
    update_meter_reading_input = ft.TextField(label="Показання лічильника", width=300)
    update_electricity_payment_input = ft.TextField(label="Сума оплати за електроенергію", width=300)
    update_water_payment_input = ft.TextField(label="Сума оплати за воду", width=300)
    update_plot_info_button = ft.ElevatedButton("Оновити дані ділянки", on_click=update_plot_info)

    # Введення даних власника ділянки
    plot_number_input = ft.TextField(label="Номер ділянки", width=300)
    owner_name_input = ft.TextField(label="ПІБ власника", width=300)
    owner_phone_number_input = ft.TextField(label="Телефон власника", width=300)
    owner_email_input = ft.TextField(label="Email власника", width=300)
    privatised_checkbox = ft.Checkbox(label="Приватизовано", value=False)
    save_button = ft.ElevatedButton("Зберегти", on_click=save_data)

    output = ft.Text()

    # Створення горизонтальних стовпців (Row) з елементами
    page.add(
        ft.Column(
            [
                theme_switch,
                ft.Row(
                    [
                        ft.Text("Пошук ділянки за № або ПІБ", size=20, weight=ft.FontWeight.BOLD, width=350),
                        ft.Text("Оновлення показань та оплати", size=20, weight=ft.FontWeight.BOLD, width=350),
                        ft.Text("Введення даних власника", size=20, weight=ft.FontWeight.BOLD, width=350),
                        ft.Text("Калькулятор", size=20, weight=ft.FontWeight.BOLD, width=350),
                    ]
                ),
                ft.Row(
                    [
                        ft.Column(
                            [search_plot_input, search_owner_name_input, search_button],
                            width=350,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Column(
                            [update_plot_number_input, update_membership_fee_input, update_meter_reading_input, update_electricity_payment_input, update_water_payment_input, update_plot_info_button],
                            width=350,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Column(
                            [plot_number_input, owner_name_input, owner_phone_number_input, owner_email_input, privatised_checkbox, save_button],
                            width=350,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Column(
                            [calc_input, calc_button, calc_output],
                            width=350,
                            alignment=ft.MainAxisAlignment.START,
                        ),
                    ]
                ),
                ft.Divider(),
                output  # Виведення інформації під стовпцями
            ]
        )
    )

ft.app(target=main)
