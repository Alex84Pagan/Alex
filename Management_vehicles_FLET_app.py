import flet as ft
import sqlite3
from datetime import datetime

# Имя файла для базы данных
DATABASE_FILE = "data_base.db"

# Функция для подключения к базе данных SQLite
def connect_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    return conn, cursor

# Инициализация базы данных
def init_db():
    conn, cursor = connect_db()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_number TEXT UNIQUE NOT NULL,
        insurance_number TEXT NOT NULL,
        insurance_expiry TEXT NOT NULL,
        inspection_expiry TEXT NOT NULL,
        tachograph_calibration TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS trailers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trailer_number TEXT UNIQUE NOT NULL,
        trailer_insurance_number TEXT NOT NULL,
        trailer_insurance_expiry TEXT NOT NULL,
        trailer_inspection_expiry TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

# Функция для проверки формата даты
def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, "%d/%m/%Y")
        return True
    except ValueError:
        return False

# Функция для сохранения или обновления данных о машине
def save_or_update_vehicle(vehicle_number, insurance_number=None, insurance_expiry=None, inspection_expiry=None,
                           tachograph_calibration=None):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM vehicles WHERE vehicle_number = ?", (vehicle_number,))
    result = cursor.fetchone()

    if result:
        # Сохраняем текущие данные, если новые данные не были введены
        current_insurance_number = result[1] if not insurance_number else insurance_number
        current_insurance_expiry = result[2] if not insurance_expiry else insurance_expiry
        current_inspection_expiry = result[3] if not inspection_expiry else inspection_expiry
        current_tachograph_calibration = result[4] if not tachograph_calibration else tachograph_calibration

        cursor.execute('''
        UPDATE vehicles
        SET insurance_number = ?, insurance_expiry = ?, inspection_expiry = ?, tachograph_calibration = ?
        WHERE vehicle_number = ?''',
                       (current_insurance_number, current_insurance_expiry, current_inspection_expiry, current_tachograph_calibration, vehicle_number))
    else:
        # Вставляем новые данные, если запись не существует
        cursor.execute('''
        INSERT INTO vehicles (vehicle_number, insurance_number, insurance_expiry, inspection_expiry, tachograph_calibration)
        VALUES (?, ?, ?, ?, ?)''',
                       (vehicle_number, insurance_number, insurance_expiry, inspection_expiry, tachograph_calibration))

    conn.commit()
    conn.close()

# Функция для сохранения или обновления данных о прицепе
def save_or_update_trailer(trailer_number, trailer_insurance_number=None, trailer_insurance_expiry=None,
                           trailer_inspection_expiry=None):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM trailers WHERE trailer_number = ?", (trailer_number,))
    result = cursor.fetchone()

    if result:
        # Сохраняем текущие данные, если новые данные не были введены
        current_trailer_insurance_number = result[1] if not trailer_insurance_number else trailer_insurance_number
        current_trailer_insurance_expiry = result[2] if not trailer_insurance_expiry else trailer_insurance_expiry
        current_trailer_inspection_expiry = result[3] if not trailer_inspection_expiry else trailer_inspection_expiry

        cursor.execute('''
        UPDATE trailers
        SET trailer_insurance_number = ?, trailer_insurance_expiry = ?, trailer_inspection_expiry = ?
        WHERE trailer_number = ?''',
                       (current_trailer_insurance_number, current_trailer_insurance_expiry, current_trailer_inspection_expiry, trailer_number))
    else:
        # Вставляем новые данные, если запись не существует
        cursor.execute('''
        INSERT INTO trailers (trailer_number, trailer_insurance_number, trailer_insurance_expiry, trailer_inspection_expiry)
        VALUES (?, ?, ?, ?)''',
                       (trailer_number, trailer_insurance_number, trailer_insurance_expiry, trailer_inspection_expiry))

    conn.commit()
    conn.close()

# Функция для поиска по дате
def search_by_date(start_date, end_date):
    conn, cursor = connect_db()

    cursor.execute('''
    SELECT * FROM vehicles 
    WHERE insurance_expiry BETWEEN ? AND ? 
       OR inspection_expiry BETWEEN ? AND ? 
       OR tachograph_calibration BETWEEN ? AND ?''',
                   (start_date, end_date, start_date, end_date, start_date, end_date))
    vehicle_results = cursor.fetchall()

    cursor.execute('''
    SELECT * FROM trailers 
    WHERE trailer_insurance_expiry BETWEEN ? AND ?
       OR trailer_inspection_expiry BETWEEN ? AND ?''',
                   (start_date, end_date, start_date, end_date))
    trailer_results = cursor.fetchall()

    conn.close()
    return vehicle_results, trailer_results

# Функция для поиска машины по номеру
def search_vehicle_by_number(vehicle_number):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM vehicles WHERE vehicle_number = ?", (vehicle_number,))
    result = cursor.fetchall()
    conn.close()
    return result

# Функция для поиска прицепа по номеру
def search_trailer_by_number(trailer_number):
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM trailers WHERE trailer_number = ?", (trailer_number,))
    result = cursor.fetchall()
    conn.close()
    return result

# Функция для очистки полей
def clear_fields(*fields):
    for field in fields:
        field.value = ""
    fields[0].page.update()

# Основная функция приложения
def main(page: ft.Page):
    page.title = "Management vehicles"
    page.window.resizable = True
    page.scroll = "adaptive"

    dark_mode = False

    # Функция для переключения темы
    def toggle_dark_mode(e):
        nonlocal dark_mode
        dark_mode = not dark_mode
        page.theme_mode = "dark" if dark_mode else "light"
        page.update()

    # Pola wprowadzania danych dla pojazdu
    vehicle_number = ft.TextField(label="Numer pojazdu")
    insurance_number = ft.TextField(label="Numer ubezpieczenia")
    insurance_expiry = ft.TextField(label="Data wygaśnięcia ubezpieczenia (DD/MM/RRRR)")
    inspection_expiry = ft.TextField(label="Data wygaśnięcia przeglądu (DD/MM/RRRR)")
    tachograph_calibration = ft.TextField(label="Data kalibracji tachografu (DD/MM/RRRR)")

    # Pola wprowadzania danych dla przyczepy
    trailer_number = ft.TextField(label="Numer przyczepy")
    trailer_insurance_number = ft.TextField(label="Numer ubezpieczenia przyczepy")
    trailer_insurance_expiry = ft.TextField(label="Data wygaśnięcia ubezpieczenia przyczepy (DD/MM/RRRR)")
    trailer_inspection_expiry = ft.TextField(label="Data wygaśnięcia przeglądu przyczepy (DD/MM/RRRR)")

    # Pola do wyszukiwania
    search_vehicle_number = ft.TextField(label="Wyszukaj według numeru pojazdu")
    search_trailer_number = ft.TextField(label="Wyszukaj według numeru przyczepy")
    search_start_date = ft.TextField(label="Data początkowa (DD/MM/RRRR)")
    search_end_date = ft.TextField(label="Data końcowa (DD/MM/RRRR)")

    # Funkcje dla przycisków
    def save_vehicle_click(e):
        save_or_update_vehicle(
            vehicle_number.value, insurance_number.value, insurance_expiry.value,
            inspection_expiry.value, tachograph_calibration.value
        )
        clear_fields(vehicle_number, insurance_number, insurance_expiry, inspection_expiry, tachograph_calibration)
        page.dialog = ft.AlertDialog(title=ft.Text("Dane pojazdu zostały pomyślnie zapisane/zaktualizowane!"))
        page.dialog.open = True
        page.update()

    def save_trailer_click(e):
        save_or_update_trailer(
            trailer_number.value, trailer_insurance_number.value, trailer_insurance_expiry.value,
            trailer_inspection_expiry.value
        )
        clear_fields(trailer_number, trailer_insurance_number, trailer_insurance_expiry, trailer_inspection_expiry)
        page.dialog = ft.AlertDialog(title=ft.Text("Dane przyczepy zostały pomyślnie zapisane/zaktualizowane!"))
        page.dialog.open = True
        page.update()

    def search_by_date_click(e):
        if not (is_valid_date(search_start_date.value) and is_valid_date(search_end_date.value)):
            page.dialog = ft.AlertDialog(
                title=ft.Text("Błąd", size=18),  # Увеличенный шрифт заголовка для ошибки
                content=ft.Text("Nieprawidłowy format daty! Użyj DD/MM/RRRR.", size=18)
                # Увеличенный шрифт сообщения об ошибке
            )
            page.dialog.open = True
            page.update()
            return

        vehicles, trailers = search_by_date(search_start_date.value, search_end_date.value)
        vehicle_data = "\n".join([f"Pojazd: {v[1]}, Ubezpieczenie: {v[2]}, Data wygaśnięcia ubezpieczenia: {v[3]}, "
                                  f"Data wygaśnięcia przeglądu: {v[4]}, Data kalibracji tachografu: {v[5]}" for v in
                                  vehicles])
        trailer_data = "\n".join([f"Przyczepa: {t[1]}, Ubezpieczenie: {t[2]}, Data wygaśnięcia ubezpieczenia: {t[3]}, "
                                  f"Data wygaśnięcia przeglądu: {t[4]}" for t in trailers])
        content_text = f"Pojazdy:\n{vehicle_data or 'Brak wyników'}\n\nPrzyczepy:\n{trailer_data or 'Brak wyników'}"

        clear_fields(search_start_date, search_end_date)
        page.dialog = ft.AlertDialog(
            title=ft.Text("Wyniki wyszukiwania", size=18),  # Увеличенный шрифт заголовка
            content=ft.Text(content_text, size=18)  # Увеличенный шрифт содержимого
        )
        page.dialog.open = True
        page.update()

    def search_vehicle_click(e):
        result = search_vehicle_by_number(search_vehicle_number.value)
        if result:
            vehicle_data = f"Numer pojazdu: {result[0][1]}\nUbezpieczenie: {result[0][2]}\nData wygaśnięcia ubezpieczenia: {result[0][3]}\n" \
                           f"Data przeglądu: {result[0][4]}\nData kalibracji tachografu: {result[0][5]}"
            page.dialog = ft.AlertDialog(
                title=ft.Text("Informacje o pojeździe", size=18),
                content=ft.Text(vehicle_data, size=18)  # увеличенный шрифт
            )
        else:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Błąd", size=18),
                content=ft.Text("Pojazd nie został znaleziony!", size=18)
            )
        clear_fields(search_vehicle_number)
        page.dialog.open = True
        page.update()

    def search_trailer_click(e):
        result = search_trailer_by_number(search_trailer_number.value)
        if result:
            trailer_data = f"Numer przyczepy: {result[0][1]}\nUbezpieczenie: {result[0][2]}\nData wygaśnięcia ubezpieczenia: {result[0][3]}\n" \
                           f"Data przeglądu: {result[0][4]}"
            page.dialog = ft.AlertDialog(
                title=ft.Text("Informacje o przyczepie", size=18),  # Увеличенный шрифт заголовка
                content=ft.Text(trailer_data, size=18)  # Увеличенный шрифт содержимого
            )
        else:
            page.dialog = ft.AlertDialog(
                title=ft.Text("Błąd", size=18),  # Увеличенный шрифт заголовка для ошибки
                content=ft.Text("Przyczepa nie została znaleziona!", size=18)  # Увеличенный шрифт сообщения об ошибке
            )
        clear_fields(search_trailer_number)
        page.dialog.open = True
        page.update()

    # Przycisk
    save_vehicle_button = ft.ElevatedButton(text="Zapisz/Zaktualizuj pojazd", on_click=save_vehicle_click)
    save_trailer_button = ft.ElevatedButton(text="Zapisz/Zaktualizuj przyczepę", on_click=save_trailer_click)
    search_by_date_button = ft.ElevatedButton(text="Wyszukaj według daty", on_click=search_by_date_click)
    search_vehicle_button = ft.ElevatedButton(text="Wyszukaj pojazd", on_click=search_vehicle_click)
    search_trailer_button = ft.ElevatedButton(text="Wyszukaj przyczepę", on_click=search_trailer_click)
    toggle_theme_button = ft.ElevatedButton(text="light/dark", on_click=toggle_dark_mode)

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        toggle_theme_button,  # Переключение темы
                        ft.Text("Management vehicles", size=24)
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(  # Один контейнер с рамкой
                    content=ft.Row(
                        [
                        ft.Container(
                             ft.Column(
                                    [
                                        ft.Text("Truck", size=20, weight=ft.FontWeight.BOLD),
                                        vehicle_number,
                                        insurance_number,
                                        insurance_expiry,
                                        inspection_expiry,
                                        tachograph_calibration,
                                        save_vehicle_button,
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER  # Центрируем по горизонтали
                                ),
                                padding=10
                            ),
                            ft.Container(
                                ft.Column(
                                    [
                                        ft.Text("Trailer", size=20, weight=ft.FontWeight.BOLD),
                                        trailer_number,
                                        trailer_insurance_number,
                                        trailer_insurance_expiry,
                                        trailer_inspection_expiry,
                                        save_trailer_button,
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER  # Центрируем по горизонтали
                                ),
                                padding=10
                            ),
                            ft.Container(
                                ft.Column(
                                    [
                                        ft.Text("Search", size=20, weight=ft.FontWeight.BOLD),
                                        search_vehicle_number,
                                        search_vehicle_button,
                                        search_trailer_number,
                                        search_trailer_button,
                                        ft.Divider(),
                                        search_start_date,
                                        search_end_date,
                                        search_by_date_button,
                                        ft.Divider(),
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER  # Центрируем по горизонтали
                                ),
                                padding=10
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_AROUND  # Размещаем колонки равномерно
                    ),
                    padding=10,
                    border=ft.border.all(3, "red"),  # Общая красная рамка
                    border_radius=ft.border_radius.all(10)  # Закругленные углы для рамки
                )
            ]
        )
    )

# Инициализация базы данных и запуск приложения
if __name__ == "__main__":
    init_db()
    ft.app(target=main)