import sys

VFS_NAME = "vfs"


def run_command(cmd, args):
    """Заглушки команд этапа 1."""
    if cmd == "ls":
        print(f"[ls] имя команды: ls, аргументы: {args}")
    elif cmd == "cd":
        print(f"[cd] имя команды: cd, аргументы: {args}")
    else:
        print(f"{cmd}: command not found")
        return False
    return True


def repl():
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
        parts = line.split()
        cmd, args = parts[0], parts[1:]
        if cmd == "exit":
            print("Выход.")
            break
        run_command(cmd, args)


if __name__ == "__main__":
    repl()