"""Виртуальная файловая система (VFS) в памяти.

Загружается из XML-файла. Содержимое файлов хранится в base64.
"""

import xml.etree.ElementTree as ET
import base64


class VfsError(Exception):
    """Ошибка работы с VFS."""


class VfsNode:
    """Узел VFS: файл или директория."""

    def __init__(self, name, is_dir, content=b"",
                 owner="root", group="root", mode=None):
        """Создаёт узел.

        Args:
            name: имя файла или папки.
            is_dir: True для папки, False для файла.
            content: содержимое файла (bytes).
            owner: владелец.
            group: группа.
            mode: права доступа (int, восьмеричное).
        """
        self.name = name
        self.is_dir = is_dir
        self.content = content
        self.children = {}
        self.owner = owner
        self.group = group
        if mode is None:
            self.mode = 0o755 if is_dir else 0o644
        else:
            self.mode = mode


class Vfs:
    """Виртуальная файловая система."""

    def __init__(self):
        """Создаёт пустую VFS с корнем."""
        self.root = VfsNode("/", is_dir=True)
        self.cwd = self.root

    @classmethod
    def from_xml(cls, path):
        """Загружает VFS из XML-файла.

        Raises:
            VfsError: если файл не найден или повреждён.
        """
        vfs = cls()
        try:
            tree = ET.parse(path)
        except FileNotFoundError:
            raise VfsError(f"Файл VFS не найден: {path}")
        except ET.ParseError as e:
            raise VfsError(f"Неверный формат XML: {e}")

        root_elem = tree.getroot()
        if root_elem.tag != "vfs":
            raise VfsError("Корневой тег должен быть <vfs>")

        for child in root_elem:
            if child.tag == "dir":
                vfs._load_dir(vfs.root, child)
            elif child.tag == "file":
                vfs._load_file(vfs.root, child)
            else:
                raise VfsError(f"Неизвестный тег: {child.tag}")
        return vfs

    def _load_dir(self, parent, elem):
        """Рекурсивно загружает директорию."""
        name = elem.get("name")
        if not name:
            raise VfsError("У <dir> нет атрибута name")
        node = VfsNode(name, is_dir=True)
        parent.children[name] = node
        for child in elem:
            if child.tag == "dir":
                self._load_dir(node, child)
            elif child.tag == "file":
                self._load_file(node, child)

    def _load_file(self, parent, elem):
        """Загружает файл и декодирует base64."""
        name = elem.get("name")
        if not name:
            raise VfsError("У <file> нет атрибута name")
        raw = elem.get("content", "")
        try:
            content = base64.b64decode(raw) if raw else b""
        except Exception:
            raise VfsError(f"Ошибка base64 в файле {name}")
        node = VfsNode(name, is_dir=False, content=content)
        parent.children[name] = node

    def resolve_path(self, path):
        """Возвращает узел по пути.
        Поддерживает абсолютные и относительные пути,
        а также '.' и '..'.
        """
        if path.startswith("/"):
            node = self.root
            parts = [p for p in path.split("/") if p]
        else:
            node = self.cwd
            parts = [p for p in path.split("/") if p]

        for p in parts:
            if p == ".":
                continue
            if p == "..":
                node = self._parent_of(node)
                continue
            if not node.is_dir or p not in node.children:
                raise VfsError(f"Нет такого файла или каталога: {path}")
            node = node.children[p]
        return node

    def path_to(self, node):
        """Возвращает строковый путь до узла от корня."""
        if node is self.root:
            return "/"
        parts = []

        def find(current, target, acc):
            for name, child in current.children.items():
                if child is target:
                    return acc + [name]
                if child.is_dir:
                    res = find(child, target, acc + [name])
                    if res:
                        return res
            return None

        result = find(self.root, node, [])
        if result is None:
            return "/"
        return "/" + "/".join(result) 
    
    def _parent_of(self, node):
        """Возвращает родителя узла (обходом от корня)."""
        if node is self.root:
            return self.root

        def find(current, target):
            for child in current.children.values():
                if child is target:
                    return current
                if child.is_dir:
                    res = find(child, target)
                    if res:
                        return res
            return None

        return find(self.root, node) or self.root