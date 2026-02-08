import os
import time

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


st.title("Детектор переломов костей")

model_option = st.selectbox(
    "Выберите модель",
    ("nano", "large"),
    help="Нано работает быстрее, но large более точный",
)

uploaded_file = st.file_uploader(
    "Загрузите рентген снимок (в формате JPG или PNG)",
    type=["png", "jpg"],
)

if uploaded_file is not None and st.button("Анализировать снимок"):
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/detections",
            params={"model_type": model_option},
            files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        task_id = data["id"]
    except requests.RequestException as e:
        st.error(f"При отправке произошла ошибка: {e}")
    else:
        with st.spinner("Алгоритм ищет переломы…"):
            while True:
                resp = requests.get(f"{BACKEND_URL}/api/detections/{task_id}", timeout=10)
                resp.raise_for_status()
                task = resp.json()
                status = task["status"]

                if status == "completed":
                    st.success("Готово.")
                    result_url = task.get("result_image_url")
                    if result_url:
                        image_url = f"{BACKEND_URL}/api/media/{result_url}"
                        st.image(image_url, caption="Результат детекции")
                    break
                elif status == "failed":
                    st.error(f"Ошибка: {task.get('error_message', 'Неизвестная ошибка')}")
                    break

                time.sleep(1)

        if st.button("Начать новую детекцию", type="primary"):
            st.rerun()
