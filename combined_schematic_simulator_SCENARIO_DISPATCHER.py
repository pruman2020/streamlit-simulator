import time

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


# -------------------------------
# 📈 Графіки параметрів
# -------------------------------
st.markdown("## 📊 Параметри за останнє оновлення")

df_graphs = pd.DataFrame([
    {
        "Блок": blk.name,
        "Температура": blk.temperature,
        "Вологість": blk.humidity,
        "Вітер": blk.wind,
        "Статус": blk.status
    }
    for blk in st.session_state.blocks.values()
    if blk.enabled
])

if not df_graphs.empty:
    st.line_chart(df_graphs.set_index("Блок")[["Температура"]])
    st.line_chart(df_graphs.set_index("Блок")[["Вологість"]])
    st.line_chart(df_graphs.set_index("Блок")[["Вітер"]])
    st.bar_chart(df_graphs["Статус"].value_counts())

# -------------------------------
# 🔁 Поетапна симуляція подій
# -------------------------------
if st.button("▶️ Запустити симуляцію події з етапами"):
    for i, step in enumerate(event_options[selected_event], 1):
        st.write(f"**Крок {i}:** {step}")
        time.sleep(0.8)
    st.success("✅ Подію завершено")


# -------------------------------
# 📉 Діаграма розсіювання
# -------------------------------
scatter_data = df_graphs[["Температура", "Вологість", "Блок"]] if not df_graphs.empty else pd.DataFrame()

if not scatter_data.empty:
    st.markdown("### 🔘 Діаграма розсіювання: Темп vs Вологість")
    st.altair_chart(
        alt.Chart(scatter_data).mark_circle(size=90).encode(
            x="Температура",
            y="Вологість",
            color="Блок",
            tooltip=["Блок", "Температура", "Вологість"]
        ).interactive(),
        use_container_width=True
    )

# -------------------------------
# 📊 Діаграма стану ліній (блоків)
# -------------------------------
st.markdown("### 📊 Діаграма станів блоків")
if not df_graphs.empty:
    st.bar_chart(df_graphs["Статус"].value_counts())

# -------------------------------
# 🔁 Анімована симуляція подій
# -------------------------------
if st.button("▶️ Анімувати подію з прогресом"):
    steps = event_options[selected_event]
    progress = st.progress(0)
    for i, step in enumerate(steps):
        st.write(f"**Крок {i+1}/{len(steps)}:** {step}")
        progress.progress((i + 1) / len(steps))
        time.sleep(1)
    st.success("✅ Симуляцію завершено")


# -------------------------------
# 🧑‍✈️ Панель диспетчера
# -------------------------------
st.markdown("## 🧑‍✈️ Панель диспетчера")

dispatcher_actions = []

col1, col2 = st.columns(2)
with col1:
    if st.button("🔌 Вимкнути всі блоки"):
        for blk in st.session_state.blocks.values():
            blk.enabled = False
        dispatcher_actions.append("Диспетчер вимкнув всі блоки")

    if st.button("🔍 Запустити самотестування"):
        dispatcher_actions.append("Запущено самотестування блоків")
        for blk in st.session_state.blocks.values():
            if blk.enabled:
                blk.status = "Тестування..."
        st.success("🧪 Самотестування в процесі...")

with col2:
    if st.button("🧊 Виявити ожеледь"):
        dispatcher_actions.append("Виконано перевірку на ожеледь")
        for blk in st.session_state.blocks.values():
            if blk.enabled and blk.temperature < -5 and blk.humidity > 80:
                blk.status = "Ожеледь"
        st.info("Перевірено всі блоки на умови ожеледі")

    if st.button("📶 Перевірити зв'язок"):
        dispatcher_actions.append("Перевірено GSM-зв'язок з блоками")
        st.toast("Усі блоки на зв'язку ✅", icon="📡")

# Виведення журналу дій диспетчера
if dispatcher_actions:
    st.markdown("### 🧾 Журнал дій диспетчера")
    for action in dispatcher_actions:
        st.write(f"🕒 {datetime.now().strftime('%H:%M:%S')} — {action}")
