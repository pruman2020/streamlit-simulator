
import streamlit as st
import random
import pandas as pd
import time
from datetime import datetime
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(layout="wide")
st.title("🔌 Повний симулятор мережі з диспетчерською, графом, подіями та журналом")

# -------------------------------
# Ініціалізація стану
# -------------------------------
if "blocks" not in st.session_state:
    st.session_state.blocks = {
        f"TP{i}": {
            "enabled": True,
            "temperature": 0,
            "humidity": 0,
            "wind": 0,
            "status": "Норма"
        } for i in range(1, 5)
    }
if "events" not in st.session_state:
    st.session_state.events = []

# -------------------------------
# 🔌 Бокова панель перемикачів
# -------------------------------
st.sidebar.title("⚙️ Керування блоками")
for name, blk in st.session_state.blocks.items():
    blk["enabled"] = st.sidebar.toggle(f"{name}: {'🟢' if blk['enabled'] else '🔴'}", value=blk["enabled"])

# -------------------------------
# 🔁 Оновлення параметрів
# -------------------------------
if st.button("🔁 Оновити параметри блоків"):
    for name, blk in st.session_state.blocks.items():
        if blk["enabled"]:
            blk["temperature"] = round(random.uniform(-15, 10), 1)
            blk["humidity"] = round(random.uniform(40, 100), 1)
            blk["wind"] = round(random.uniform(0, 35), 1)
            if blk["temperature"] < -5 and blk["humidity"] > 80:
                blk["status"] = "Ожеледь"
            elif blk["wind"] > 25:
                blk["status"] = "Порив"
            else:
                blk["status"] = "Норма"
            st.session_state.events.append({
                "Час": datetime.now().strftime("%H:%M:%S"),
                "Блок": name,
                "Статус": blk["status"],
                "Температура": blk["temperature"],
                "Вологість": blk["humidity"],
                "Вітер": blk["wind"]
            })

# -------------------------------
# 🧑‍✈️ Панель диспетчера
# -------------------------------
st.markdown("## 🧑‍✈️ Панель диспетчера")

col1, col2 = st.columns(2)
if col1.button("🔌 Вимкнути всі"):
    for blk in st.session_state.blocks.values():
        blk["enabled"] = False
        blk["status"] = "Вимкнено"

if col2.button("🧊 Перевірити ожеледь"):
    for blk in st.session_state.blocks.values():
        if blk["enabled"] and blk["temperature"] < -5 and blk["humidity"] > 80:
            blk["status"] = "Ожеледь"

# -------------------------------
# 📋 Таблиця параметрів
# -------------------------------
st.markdown("## 📋 Параметри ТП")
df = pd.DataFrame([
    {
        "Блок": name,
        "Температура": blk["temperature"],
        "Вологість": blk["humidity"],
        "Вітер": blk["wind"],
        "Статус": blk["status"]
    } for name, blk in st.session_state.blocks.items()
    if blk["enabled"]
])
st.dataframe(df, use_container_width=True)

# -------------------------------
# 📈 Графіки
# -------------------------------
if not df.empty:
    st.line_chart(df.set_index("Блок")[["Температура", "Вологість", "Вітер"]])
    st.bar_chart(df["Статус"].value_counts())

# -------------------------------
# 📝 Журнал подій
# -------------------------------
st.markdown("## 🗂 Журнал подій")
log_df = pd.DataFrame(st.session_state.events)
if not log_df.empty:
    st.dataframe(log_df.tail(10), use_container_width=True)
    st.download_button("⬇️ Завантажити журнал CSV", log_df.to_csv(index=False).encode("utf-8"), file_name="events.csv")

# -------------------------------
# ⚙️ Симуляція подій
# -------------------------------
st.markdown("## 🔄 Симуляція подій")

event_steps = {
    "Самотестування": ["А. Диспетчер → GSM", "Б. GSM → TP", "В. TP тестує", "Г. Результат → диспетчер"],
    "КЗ": ["А. TP передає КЗ", "Б. GSM отримує", "В. Передача до диспетчера", "Г. Відображення"],
    "Обрив": ["А. TP виявляє обрив", "Б. GSM приймає", "В. Передача до диспетчера"]
}
selected_event = st.selectbox("Оберіть подію", list(event_steps.keys()))

if st.button("▶️ Анімувати подію"):
    steps = event_steps[selected_event]
    prog = st.progress(0)
    for i, step in enumerate(steps):
        st.write(f"**Крок {i+1}/{len(steps)}:** {step}")
        time.sleep(0.7)
        prog.progress((i+1)/len(steps))
    st.success("✅ Симуляцію завершено")

# -------------------------------
# 🕸 Граф мережі
# -------------------------------
st.markdown("## 🕸 Структура мережі")

status_colors = {
    "Норма": "green",
    "Ожеледь": "skyblue",
    "Порив": "orange",
    "Вимкнено": "gray"
}

nodes = [
    Node(id="Диспетчер", label="Диспетчер", size=25, color="lightgray"),
    Node(id="GSM", label="GSM", size=20, color="lightblue")
]
edges = [Edge(source="Диспетчер", target="GSM")]

for tp, blk in st.session_state.blocks.items():
    color = status_colors.get(blk["status"], "green") if blk["enabled"] else "gray"
    nodes.append(Node(id=tp, label=tp, color=color))
    edges.append(Edge(source="GSM", target=tp))

config = Config(width=800, height=500, directed=False, physics=True, hierarchical=False)
agraph(nodes=nodes, edges=edges, config=config)
