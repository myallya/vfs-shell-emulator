"""Эмулятор shell с виртуальной файловой системой (VFS).

Этап 2: параметры командной строки и выполнение стартового скрипта.
"""

import sys
import argparse

VFS_NAME = "vfs"


def run_command(cmd, args):
    """Выполняет команду.

    Возвращает True при успехе, False при ошибке.
    """
    if cmd == "ls":
        print(f"[ls] имя команды: ls, аргументы: {args}")
    elif cmd == "cd":
        print(f"[cd] имя команды: cd, аргументы: {args}")
    else:
        print(f"{cmd}: command not found")
        return False
    return True


def execute_line(line):
    """Выполняет одну строку ввода.

    Возвращает:
        "exit"  — если была команда exit
        "ok"    — если команда выполнена
        "error" — если команда не найдена
    """
    parts = line.split()
    cmd, args = parts[0], parts[1:]
    if cmd == "exit":
        return "exit"
    if run_command(cmd, args):
        return "ok"
    return "error"


def run_script(script_path):
    """Выполняет команды из файла-скрипта.

    Останавливается при первой ошибке. Имитирует диалог:
    печатает приглашение и введённую команду.
    """
    try:
        with open(script_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                print(f"{VFS_NAME}:/$ {line}")
                result = execute_line(line)
                if result == "exit":
                    print("Выход.")
                    return
                if result == "error":
                    print(f"Ошибка в скрипте на строке: {line}")
                    print("Остановка скрипта.")
                    sys.exit(1)
    except FileNotFoundError:
        print(f"Ошибка: скрипт не найден: {script_path}")
        sys.exit(1)


def repl():
    """Интерактивный режим работы (REPL)."""
    print(f"Добро пожаловать в эмулятор shell. VFS: {VFS_NAME}")
    print("Введите 'exit' для выхода.")
    while True:
        try:
            line = input(f"{VFS_NAME}:/$ ")
        except EOFError:
            print()
            break
        line = line.strip()
        if not line:
            continue
        if execute_line(line) == "exit":
            print("Выход.")
            break


def main():
    """Точка входа: разбор аргументов и запуск."""
    parser = argparse.ArgumentParser(
        description="Эмулятор shell с VFS"
    )
    parser.add_argument("--vfs", help="Путь к XML-файлу VFS")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    args = parser.parse_args()

    # Отладочный вывод параметров (требование этапа 2)
    print("=== Параметры запуска ===")
    print(f"VFS path: {args.vfs}")
    print(f"Script path: {args.script}")
    print("=========================")

    if args.script:
        run_script(args.script)
    else:
        repl()


if __name__ == "__main__":
    main()