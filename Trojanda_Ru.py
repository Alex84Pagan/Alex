import flet as ft

# Имя файла для сохранения данных
DATA_FILE = "plots_data.txt"

# База данных участков (загружается из файла)
plots = []

def load_data():
    """Загрузка данных из файла в список plots."""
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
        pass  # Если файл не найден, начинаем с пустой базы данных

def save_to_file():
    """Сохранение данных из списка plots в файл."""
    with open(DATA_FILE, "w") as file:
        for plot in plots:
            file.write(f"{plot['plot_number']},{plot['owner_name']},{plot['phone_number']},"
                       f"{plot['email']},{plot['is_privatised']},{plot['membership_fee']},"
                       f"{plot['electric_meter_reading']},{plot['electricity_payment']},"
                       f"{plot['water_payment']}\n")

def save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised):
    """Добавление или обновление информации о владельце участка."""
    plot = find_plot(plot_number)

    if plot:
        # Обновляем информацию о владельце, если участок найден
        plot["owner_name"] = owner_name
        plot["phone_number"] = owner_phone_number
        plot["email"] = owner_email
        plot["is_privatised"] = is_privatised
    else:
        # Добавляем новый участок
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
    """Поиск участка по номеру."""
    for plot in plots:
        if plot["plot_number"] == plot_number:
            return plot
    return None

def find_plot_by_owner_name(owner_name):
    """Поиск участка по ФИО владельца."""
    for plot in plots:
        if plot["owner_name"].lower() == owner_name.lower():
            return plot
    return None

def update_plot_data(plot_number, membership_fee=None, meter_reading=None, electricity_payment=None,
                     water_payment=None):
    """Обновление данных участка."""
    plot = find_plot(plot_number)
    if plot:
        if membership_fee is not None:
            plot["membership_fee"] = membership_fee
        if meter_reading is not None:
            plot["electric_meter_reading"] = meter_reading
        if electricity_payment is not None:
            plot["electricity_payment"] = electricity_payment
        if water_payment is not None:
            plot["water_payment"] = water_payment
        save_to_file()
        return True
    return False

def main(page: ft.Page):
    load_data()  # Загружаем данные при старте программы

    page.title = "Plot Management System"
    page.scroll = "adaptive"

    def switch_theme(e):
        page.theme_mode = "dark" if theme_switch.value else "light"
        page.update()

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
                f"Информация о владельце участка {plot_info['plot_number']}:\n"
                f"ФИО: {plot_info['owner_name']}\n"
                f"Телефон: {plot_info['phone_number']}\n"
                f"Email: {plot_info['email']}\n"
                f"Приватизирован: {'Да' if plot_info['is_privatised'] else 'Нет'}\n"
                f"Членский взнос: {plot_info['membership_fee']}\n"
                f"Показания электросчетчика: {plot_info['electric_meter_reading']}\n"
                f"Оплата за электричество: {plot_info['electricity_payment']}\n"
                f"Оплата за воду: {plot_info['water_payment']}"
            )
        else:
            output.value = "Участок не найден."

        search_plot_input.value = ""
        search_owner_name_input.value = ""
        page.update()

    def update_plot_info(e):
        plot_number = int(update_plot_number_input.value)
        membership_fee = update_membership_fee_input.value
        meter_reading = update_meter_reading_input.value
        electricity_payment = update_electricity_payment_input.value
        water_payment = update_water_payment_input.value

        success = update_plot_data(
            plot_number,
            membership_fee=float(membership_fee) if membership_fee else None,
            meter_reading=float(meter_reading) if meter_reading else None,
            electricity_payment=float(electricity_payment) if electricity_payment else None,
            water_payment=float(water_payment) if water_payment else None
        )

        output.value = f"Данные для участка {plot_number} обновлены." if success else "Участок не найден."

        update_plot_number_input.value = ""
        update_membership_fee_input.value = ""
        update_meter_reading_input.value = ""
        update_electricity_payment_input.value = ""
        update_water_payment_input.value = ""
        page.update()

    def save_data(e):
        plot_number = int(plot_number_input.value)
        owner_name = owner_name_input.value
        owner_phone_number = owner_phone_number_input.value
        owner_email = owner_email_input.value
        is_privatised = privatised_checkbox.value

        save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised)

        output.value = f"Данные участка {plot_number} обновлены!"

        plot_number_input.value = ""
        owner_name_input.value = ""
        owner_phone_number_input.value = ""
        owner_email_input.value = ""
        privatised_checkbox.value = False
        page.update()

    theme_switch = ft.Switch(label="Темная тема", value=False, on_change=switch_theme)

    def calculate(e):
        try:
            expression = calc_input.value
            calc_output.value = str(eval(expression))
        except Exception as ex:
            calc_output.value = f"Ошибка: {ex}"
        page.update()

    calc_input = ft.TextField(label="Введите выражение", width=300)
    calc_button = ft.ElevatedButton("Посчитать", on_click=calculate)
    calc_output = ft.Text()

    search_plot_input = ft.TextField(label="Введите номер участка", width=300)
    search_owner_name_input = ft.TextField(label="Введите ФИО владельца", width=300)
    search_button = ft.ElevatedButton("Найти участок по №/ФИО", on_click=search_plot)

    update_plot_number_input = ft.TextField(label="Номер участка", width=300)
    update_membership_fee_input = ft.TextField(label="Членский взнос", width=300)
    update_meter_reading_input = ft.TextField(label="Показания электросчетчика", width=300)
    update_electricity_payment_input = ft.TextField(label="Сумма оплаты за электричество", width=300)
    update_water_payment_input = ft.TextField(label="Сумма оплаты за воду", width=300)
    update_plot_info_button = ft.ElevatedButton("Обновить данные участка", on_click=update_plot_info)

    plot_number_input = ft.TextField(label="Номер участка", width=300)
    owner_name_input = ft.TextField(label="ФИО владельца", width=300)
    owner_phone_number_input = ft.TextField(label="Телефон владельца", width=300)
    owner_email_input = ft.TextField(label="Email владельца", width=300)
    privatised_checkbox = ft.Checkbox(label="Приватизирован", value=False)
    save_button = ft.ElevatedButton("Сохранить", on_click=save_data)

    output = ft.Text()

    page.add(
        ft.Column(
            [
                theme_switch,
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Поиск участка по № или ФИО", size=20, weight=ft.FontWeight.BOLD)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            width=350
                        ),
                        ft.Column(
                            [
                                ft.Text("Обновление показаний и оплаты", size=20, weight=ft.FontWeight.BOLD)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            width=350
                        ),
                        ft.Column(
                            [
                                ft.Text("Ввод данных владельца", size=20, weight=ft.FontWeight.BOLD)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            width=350
                        ),
                        ft.Column(
                            [
                                ft.Text("Калькулятор", size=20, weight=ft.FontWeight.BOLD)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            width=350
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                ft.Row(
                    [
                        ft.Column([search_plot_input, search_owner_name_input, search_button], width=350),
                        ft.Column([update_plot_number_input, update_membership_fee_input, update_meter_reading_input,
                                   update_electricity_payment_input, update_water_payment_input,
                                   update_plot_info_button], width=350),
                        ft.Column([plot_number_input, owner_name_input, owner_phone_number_input, owner_email_input,
                                   privatised_checkbox, save_button], width=350),
                        ft.Column([calc_input, calc_button, calc_output], width=350),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                output
            ]
        )
    )

ft.app(target=main)