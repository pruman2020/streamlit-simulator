
import streamlit as st
import random
from datetime import datetime
import pandas as pd
import altair as alt

st.set_page_config(layout="wide")

# -------------------------------
# Дані блоків
# -------------------------------
class Block:
    def __init__(self, name):
        self.name = name
        self.enabled = True
        self.status = "Норма"
        self.temperature = 0
        self.humidity = 0
        self.wind = 0

    def update_status(self):
        if not self.enabled:
            self.status = "Вимкнено"
        elif self.temperature < -5 and self.humidity > 80:
            self.status = "Ожеледь"
        elif self.wind > 25:
            self.status = "Порив"
        else:
            self.status = "Норма"

# -------------------------------
# Ініціалізація
# -------------------------------
if "blocks" not in st.session_state:
    st.session_state.blocks = {f"BB{i}": Block(f"BB{i}") for i in range(1, 8)}
    st.session_state.events = []

# -------------------------------
# Ліва панель керування
# -------------------------------
st.sidebar.title("🔌 Керування")
for name, blk in st.session_state.blocks.items():
    blk.enabled = st.sidebar.toggle(f"{name}: {'🟢' if blk.enabled else '🔴'}", value=blk.enabled)

# -------------------------------
# Верхній блок: час, оновлення, схема
# -------------------------------
col1, col2 = st.columns([2, 3])

with col1:
    st.markdown("### 🕒 Поточний час")
    st.markdown(f"**{datetime.now().strftime('%H:%M:%S')}**")

    if st.button("🔁 Оновити"):
        for blk in st.session_state.blocks.values():
            blk.temperature = round(random.uniform(-15, 10), 1)
            blk.humidity = round(random.uniform(50, 100), 1)
            blk.wind = round(random.uniform(0, 40), 1)
            blk.update_status()
            st.session_state.events.append({
                "Час": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Блок": blk.name,
                "Статус": blk.status,
                "Температура": blk.temperature,
                "Вологість": blk.humidity,
                "Вітер": blk.wind
            })

with col2:
    st.image("https://raw.githubusercontent.com/m3t4lray/gpt-assets/main/gsm_schematic.png", use_container_width=True)

# -------------------------------
# Таблиця параметрів
# -------------------------------
st.markdown("### 📋 Параметри блоків")
for blk in st.session_state.blocks.values():
    with st.expander(f"{blk.name} — {blk.status}"):
        if blk.enabled:
            st.write(f"🌡 Темп: {blk.temperature} °C | 💧 Вологість: {blk.humidity} % | 💨 Вітер: {blk.wind} м/с")
        else:
            st.warning("Блок вимкнено")

# -------------------------------
# 🔁 Симуляція подій
# -------------------------------
st.markdown("### ⚙️ Симуляція подій")

event_options = {
    "Самотестування": [
        "А. Диспетчерська станція → GSM",
        "Б. GSM → блок виносний",
        "В. Блок тестує і повертає результат",
        "Г. GSM → диспетчерська станція",
        "Д. Вивід результату на монітор"
    ],
    "Опитування сенсорів": [
        "А. Диспетчерська станція → GSM",
        "Б. GSM → блок виносний",
        "В. Опитування сенсорів завершено"
    ],
    "Поява льоду": [
        "А. Диспетчерська станція → GSM",
        "Б. GSM → блок виносний",
        "В. Команда на плавку льоду",
        "Г. Включено пристрій плавлення"
    ],
    "Коротке замикання": [
        "А. Сенсор КЗ → блок виносний",
        "Б. Блок → GSM",
        "В. GSM → диспетчер",
        "Г. Вивід на монітор"
    ],
    "Обрив проводів": [
        "А. Сенсор обриву → блок виносний",
        "Б. Блок → GSM",
        "В. GSM → диспетчер",
        "Г. Вивід на монітор"
    ]
}

selected_event = st.selectbox("Оберіть подію для симуляції", list(event_options.keys()))
if st.button("▶️ Симулювати подію"):
    for step in event_options[selected_event]:
        st.success(step)

# -------------------------------
# Завантаження CSV журналу
# -------------------------------
st.markdown("### 🗂 Журнал подій")
df_log = pd.DataFrame(st.session_state.events)
if not df_log.empty:
    st.dataframe(df_log, use_container_width=True)
    st.download_button("⬇️ Завантажити CSV", df_log.to_csv(index=False).encode("utf-8"), file_name="events.csv")
else:
    st.info("Подій ще не зафіксовано.")
