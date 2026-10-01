from pathlib import Path

RESOURCES_DIR = Path(__file__).resolve().parent / "resources"


def image_path(filename):
    path = RESOURCES_DIR / "images" / f"{filename}.jpg"

    if not path.exists():
        raise FileNotFoundError(f"Такого файлу не існує: {path}")
    return path


def load_message(filename):
    path = RESOURCES_DIR / "messages" / f"{filename}.txt"

    if not path.exists():
        raise FileNotFoundError(f"Такого файлу не існує: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_prompt(filename):
    path = RESOURCES_DIR / "prompts" / f"{filename}.txt"

    if not path.exists():
        raise FileNotFoundError(f"Такого файлу не існує: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
