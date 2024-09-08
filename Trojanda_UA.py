import flet as ft

# Ім'я файлу для збереження даних
DATA_FILE = "plots_data.txt"

# База даних ділянок (завантажується з файлу)
plots = []

def load_data():
    """Завантаження даних з файлу в список plots."""
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
        pass  # Якщо файл не знайдено, починаємо з пустої бази даних

def save_to_file():
    """Збереження даних з списку plots у файл."""
    with open(DATA_FILE, "w") as file:
        for plot in plots:
            file.write(f"{plot['plot_number']},{plot['owner_name']},{plot['phone_number']},"
                       f"{plot['email']},{plot['is_privatised']},{plot['membership_fee']},"
                       f"{plot['electric_meter_reading']},{plot['electricity_payment']},"
                       f"{plot['water_payment']}\n")

def save_to_plots(plot_number, owner_name, owner_phone_number, owner_email, is_privatised):
    """Додавання або оновлення інформації про власника ділянки."""
    plot = find_plot(plot_number)

    if plot:
        # Оновлюємо інформацію про власника, якщо ділянка знайдена
        plot["owner_name"] = owner_name
        plot["phone_number"] = owner_phone_number
        plot["email"] = owner_email
        plot["is_privatised"] = is_privatised
    else:
        # Додаємо нову ділянку
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
    """Пошук ділянки по номеру."""
    for plot in plots:
        if plot["plot_number"] == plot_number:
            return plot
    return None

def find_plot_by_owner_name(owner_name):
    """Пошук ділянки по ПІБ власника."""
    for plot in plots:
        if plot["owner_name"].lower() == owner_name.lower():
            return plot
    return None

def update_plot_data(plot_number, membership_fee=None, meter_reading=None, electricity_payment=None,
                     water_payment=None):
    """Оновлення даних ділянки."""
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
    load_data()  # Завантажуємо дані при старті програми

    page.title = "Система управління ділянками"
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
                f"Інформація про власника ділянки {plot_info['plot_number']}:\n"
                f"ПІБ: {plot_info['owner_name']}\n"
                f"Телефон: {plot_info['phone_number']}\n"
                f"Email: {plot_info['email']}\n"
                f"Приватизована: {'Так' if plot_info['is_privatised'] else 'Ні'}\n"
                f"Членський внесок: {plot_info['membership_fee']}\n"
                f"Показання електролічильника: {plot_info['electric_meter_reading']}\n"
                f"Оплата за електрику: {plot_info['electricity_payment']}\n"
                f"Оплата за воду: {plot_info['water_payment']}"
            )
        else:
            output.value = "Ділянка не знайдена."

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

        output.value = f"Дані для ділянки {plot_number} оновлені." if success else "Ділянка не знайдена."

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

        output.value = f"Дані ділянки {plot_number} оновлені!"

        plot_number_input.value = ""
        owner_name_input.value = ""
        owner_phone_number_input.value = ""
        owner_email_input.value = ""
        privatised_checkbox.value = False
        page.update()

    theme_switch = ft.Switch(label="Темна тема", value=False, on_change=switch_theme)

    def calculate(e):
        try:
            expression = calc_input.value
            calc_output.value = str(eval(expression))
        except Exception as ex:
            calc_output.value = f"Помилка: {ex}"
        page.update()

    calc_input = ft.TextField(label="Введіть вираз", width=300)
    calc_button = ft.ElevatedButton("Обчислити", on_click=calculate)
    calc_output = ft.Text()

    search_plot_input = ft.TextField(label="Введіть номер ділянки", width=300)
    search_owner_name_input = ft.TextField(label="Введіть ПІБ власника", width=300)
    search_button = ft.ElevatedButton("Знайти ділянку по №/ПІБ", on_click=search_plot)

    update_plot_number_input = ft.TextField(label="Номер ділянки", width=300)
    update_membership_fee_input = ft.TextField(label="Членський внесок", width=300)
    update_meter_reading_input = ft.TextField(label="Показання електролічильника", width=300)
    update_electricity_payment_input = ft.TextField(label="Сума оплати за електрику", width=300)
    update_water_payment_input = ft.TextField(label="Сума оплати за воду", width=300)
    update_plot_info_button = ft.ElevatedButton("Оновити дані ділянки", on_click=update_plot_info)

    plot_number_input = ft.TextField(label="Номер ділянки", width=300)
    owner_name_input = ft.TextField(label="ПІБ власника", width=300)
    owner_phone_number_input = ft.TextField(label="Телефон власника", width=300)
    owner_email_input = ft.TextField(label="Email власника", width=300)
    privatised_checkbox = ft.Checkbox(label="Приватизована", value=False)
    save_button = ft.ElevatedButton("Зберегти", on_click=save_data)

    output = ft.Text()

    page.add(
        ft.Column(
            [
                theme_switch,
                ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text("Пошук ділянки по № або ПІБ", size=20, weight=ft.FontWeight.BOLD)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            width=350
                        ),
                        ft.Column(
                            [
                                ft.Text("Оновлення показань та оплати", size=20, weight=ft.FontWeight.BOLD)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            width=350
                        ),
                        ft.Column(
                            [
                                ft.Text("Введення даних власника", size=20, weight=ft.FontWeight.BOLD)
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

