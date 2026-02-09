"""
Модуль инициализации проекта.
"""

from pathlib import Path


def init_project():
    """
    Инициализация проекта: создает необходимые директории.
    """
    # Определяем корневую директорию проекта
    project_root = Path(__file__).parent.parent

    # Только необходимые директории
    directories = [
        project_root / "data",
        project_root / "logs",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    return project_root


# Автоматически инициализируем при импорте
if __name__ != "__main__":
    project_root = init_project()
