"""PC Monitor - простий консольний монітор ресурсів комп'ютера.

Показує завантаження CPU, RAM та диска і зберігає дані у CSV-файл.
"""
import csv
import os
import time
from datetime import datetime

import psutil

LOG_FILE = "log.csv"
FIELDS = ["time", "cpu_percent", "ram_percent", "disk_percent"]


# ---------- Етап 2: основна логіка ----------
def get_stats():
    """Повертає поточні показники системи у вигляді словника."""
    disk_path = os.path.abspath(os.sep)  # корінь диска (працює на Windows/Linux/macOS)
    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "ram_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage(disk_path).percent,
    }


def save_to_csv(stats, filename=LOG_FILE):
    """Дописує один рядок показників у CSV-файл."""
    is_new = not os.path.exists(filename)
    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            writer.writeheader()
        writer.writerow(stats)


def read_log(filename=LOG_FILE):
    """Читає всі записи з CSV-файлу. Якщо файлу немає - повертає []."""
    if not os.path.exists(filename):
        return []
    with open(filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------- Етап 3: інтерфейс (консольне меню) ----------
def show_stats(stats):
    print(f"[{stats['time']}] CPU: {stats['cpu_percent']:5.1f}% | "
          f"RAM: {stats['ram_percent']:5.1f}% | "
          f"Диск: {stats['disk_percent']:5.1f}%")


def ask_int(prompt, default, minimum=1):
    """Безпечне читання цілого числа (повертає default при помилці)."""
    raw = input(prompt).strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        print("Помилка: потрібно ввести ціле число. Використано значення за замовчуванням.")
        return default
    if value < minimum:
        print(f"Помилка: число має бути не менше {minimum}. Використано значення за замовчуванням.")
        return default
    return value


def action_current():
    show_stats(get_stats())


def action_monitor():
    count = ask_int("Скільки вимірювань зробити? [5]: ", 5)
    pause = ask_int("Пауза між вимірюваннями, сек [2]: ", 2)
    print("Моніторинг запущено (Ctrl+C - зупинити)...")
    try:
        for _ in range(count):
            stats = get_stats()
            show_stats(stats)
            save_to_csv(stats)
            time.sleep(pause)
    except KeyboardInterrupt:
        print("\nМоніторинг зупинено користувачем.")
    print(f"Дані збережено у {LOG_FILE}")


def action_view_log():
    rows = read_log()
    if not rows:
        print("Лог порожній. Спочатку запустіть моніторинг (пункт 2).")
        return
    for row in rows[-10:]:  # останні 10 записів
        show_stats({k: (float(v) if k != "time" else v) for k, v in row.items()})
    avg_cpu = sum(float(r["cpu_percent"]) for r in rows) / len(rows)
    print(f"Усього записів: {len(rows)}, середнє CPU: {avg_cpu:.1f}%")


def action_clear_log():
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        print("Лог очищено.")
    else:
        print("Лог-файлу ще не існує.")


def main():
    actions = {
        "1": ("Показати поточні показники", action_current),
        "2": ("Запустити моніторинг із записом у файл", action_monitor),
        "3": ("Переглянути лог", action_view_log),
        "4": ("Очистити лог", action_clear_log),
    }
    while True:
        print("\n=== PC Monitor ===")
        for key, (title, _) in actions.items():
            print(f"{key}. {title}")
        print("0. Вихід")
        choice = input("Ваш вибір: ").strip()
        if choice == "0":
            print("До побачення!")
            break
        if choice in actions:
            actions[choice][1]()
        else:
            print("Невірний пункт меню, спробуйте ще раз.")


if __name__ == "__main__":
    main()
