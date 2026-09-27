"""Эмулятор shell с виртуальной файловой системой (VFS).

Этап 3: работа с VFS, загруженной из XML-файла.
"""

import sys
import argparse

from vfs import Vfs, VfsError

VFS_NAME = "vfs"


def cmd_ls(vfs, args):
    """Выводит содержимое каталога."""
    path = args[0] if args else "."
    node = vfs.resolve_path(path)
    if not node.is_dir:
        print(node.name)
        return
    for name in sorted(node.children):
        child = node.children[name]
        mark = "/" if child.is_dir else ""
        print(f"{name}{mark}")


def cmd_cd(vfs, args):
    """Меняет текущий каталог."""
    path = args[0] if args else "/"
    node = vfs.resolve_path(path)
    if not node.is_dir:
        raise VfsError(f"Не каталог: {path}")
    vfs.cwd = node


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
}


def run_command(vfs, cmd, args):
    """Выполняет команду над VFS.

    Возвращает True при успехе, False если команда неизвестна.
    """
    if cmd in COMMANDS:
        COMMANDS[cmd](vfs, args)
        return True
    print(f"{cmd}: command not found")
    return False


def prompt(vfs):
    """Формирует приглашение вида vfs:/$ или vfs:/имя$."""
    if vfs.cwd is vfs.root:
        return f"{VFS_NAME}:/$ "
    return f"{VFS_NAME}:/{vfs.cwd.name}$ "


def execute_line(vfs, line):
    """Выполняет одну строку. Возвращает статус."""
    parts = line.split()
    cmd, args = parts[0], parts[1:]
    if cmd == "exit":
        return "exit"
    try:
        if run_command(vfs, cmd, args):
            return "ok"
        return "error"
    except VfsError as e:
        print(f"{cmd}: {e}")
        return "error"


def run_script(vfs, script_path):
    """Выполняет скрипт, останавливается при первой ошибке."""
    try:
        with open(script_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                print(f"{prompt(vfs)}{line}")
                result = execute_line(vfs, line)
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


def repl(vfs):
    """Интерактивный режим."""
    print(f"Добро пожаловать в эмулятор shell. VFS: {VFS_NAME}")
    print("Введите 'exit' для выхода.")
    while True:
        try:
            line = input(prompt(vfs))
        except EOFError:
            print()
            break
        line = line.strip()
        if not line:
            continue
        if execute_line(vfs, line) == "exit":
            print("Выход.")
            break


def main():
    """Точка входа."""
    parser = argparse.ArgumentParser(
        description="Эмулятор shell с VFS"
    )
    parser.add_argument("--vfs", default="data/vfs_min.xml",
                        help="Путь к XML-файлу VFS")
    parser.add_argument("--script", help="Путь к стартовому скрипту")
    args = parser.parse_args()

    print("=== Параметры запуска ===")
    print(f"VFS path: {args.vfs}")
    print(f"Script path: {args.script}")
    print("=========================")

    try:
        vfs = Vfs.from_xml(args.vfs)
    except VfsError as e:
        print(f"Ошибка загрузки VFS: {e}")
        sys.exit(1)

    if args.script:
        run_script(vfs, args.script)
    else:
        repl(vfs)


if __name__ == "__main__":
    main()