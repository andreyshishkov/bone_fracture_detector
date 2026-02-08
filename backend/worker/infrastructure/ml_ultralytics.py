from pathlib import Path
from typing import Type

import cv2
import numpy as np

from backend.worker.config import MODELS_DIR


MODEL_CONFIG: dict[str, tuple[str, str]] = {
    "nano": ("yolo11s_bf.pt", "YOLO"),
    "large": ("rtdetr-bf.pt", "RTDETR"),
}

_models_cache: dict[str, object] = {}


def _get_model_class(model_type: str) -> Type:
    """Возвращает класс модели по model_type."""
    from ultralytics import RTDETR, YOLO
    _, class_name = MODEL_CONFIG[model_type]
    return YOLO if class_name == "YOLO" else RTDETR


def get_model_path(model_type: str) -> Path:
    """Путь к файлу весов по типу модели."""
    if model_type not in MODEL_CONFIG:
        raise ValueError(f"Неизвестный model_type: {model_type}. Доступны: {list(MODEL_CONFIG)}")
    filename, _ = MODEL_CONFIG[model_type]
    path = MODELS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Файл модели не найден: {path}")
    return path


def get_model(model_type: str):
    """Возвращает загруженную модель YOLO или RTDETR (с кэшем по model_type)."""
    if model_type in _models_cache:
        return _models_cache[model_type]
    model_class = _get_model_class(model_type)
    path = get_model_path(model_type)
    model = model_class(str(path))
    _models_cache[model_type] = model
    return model


def preprocess_clahe(img_path: str | Path) -> np.ndarray:
    """
    Предобработка изображения CLAHE-фильтром.

    :param img_path: путь к изображению (PNG/JPEG)
    :return: изображение в RGB (numpy array, uint8)
    """
    path = str(img_path)
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Не удалось прочитать изображение: {img_path}")
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    processed_img = clahe.apply(img)
    return cv2.cvtColor(processed_img, cv2.COLOR_GRAY2RGB)


def run_detection(
    input_path: Path,
    output_path: Path,
    model_type: str,
) -> Path:
    """
    Запускает детекцию на изображении и сохраняет результат с отрисовкой в output_path.

    :param input_path: путь к исходному изображению (PNG/JPEG)
    :param output_path: путь для сохранения изображения с боксами
    :param model_type: "nano" или "large"
    :return: output_path при успехе
    :raises: при любой ошибке (загрузка модели, инференс, сохранение) исключение пробрасывается выше
    """
    processed_img = preprocess_clahe(input_path)
    model = get_model(model_type)
    results = model.predict(source=processed_img, verbose=False)

    if not results:
        raise ValueError("Модель не вернула результатов")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    results[0].save(filename=str(output_path))
    return output_path
