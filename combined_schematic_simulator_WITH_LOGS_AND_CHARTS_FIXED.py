import altair as alt
import pandas as pd

import streamlit as st
import random
from datetime import datetime

st.set_page_config(layout="wide")

class Block:
    STATUS_NORMAL = "Норма"
    STATUS_ICE    = "Ожеледь"
    STATUS_BREAK  = "Порив"
    STATUS_OFF    = "Вимкнено"

    def __init__(self, name):
        self.name = name
        self.enabled = True
        self.status = self.STATUS_NORMAL
        self.temperature = 0
        self.humidity = 0
        self.wind = 0

    def toggle(self, enabled):
        self.enabled = enabled
        if not enabled:
            self.status = self.STATUS_OFF

    def update(self, temperature, humidity, wind):
        if not self.enabled:
            return
        self.temperature = temperature
        self.humidity = humidity
        self.wind = wind
        if temperature < -5 and humidity > 80:
            self.status = self.STATUS_ICE
        elif wind > 25:
            self.status = self.STATUS_BREAK
        else:
            self.status = self.STATUS_NORMAL

if "blocks" not in st.session_state:
    st.session_state.blocks = {f"BB{i}": Block(f"BB{i}") for i in range(1, 8)}
if "updated" not in st.session_state:
    st.session_state.updated = False

st.sidebar.title("⚙️ Керування блоками")
for name, blk in st.session_state.blocks.items():
    state = st.sidebar.toggle(f"{name}: {'🟢' if blk.enabled else '🔴'}", value=blk.enabled)
    blk.toggle(state)

col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("### 🖥️ Симуляція мережі")
    if st.button("🔁 Оновити стан"):
        for blk in st.session_state.blocks.values():
            t = round(random.uniform(-15, 10), 1)
            h = round(random.uniform(50, 100), 1)
            w = round(random.uniform(0, 40), 1)
            blk.update(t, h, w)
        st.session_state.updated = True
with col2:
    st.markdown(f"<p style='text-align:right;'>Поточний час:<br><b>{datetime.now().strftime('%H:%M:%S')}</b></p>", unsafe_allow_html=True)

st.markdown("""
<style>
    .overlay-container {
        position: relative;
        width: 100%;
        max-width: 960px;
        margin: auto;
    }
    .network-image {
        width: 100%;
    }
    .indicator {
        position: absolute;
        font-size: 20px;
    }
    .BB1 { top: 100px; left: 200px; }
    .BB2 { top: 100px; left: 370px; }
    .BB3 { top: 100px; left: 490px; }
    .BB4 { top: 270px; left: 200px; }
    .BB5 { top: 270px; left: 310px; }
    .BB6 { top: 180px; left: 280px; }
    .BB7 { top: 180px; left: 570px; }
</style>
""", unsafe_allow_html=True)

indicators_html = '''
<div class="overlay-container">
    <img src="https://raw.githubusercontent.com/m3t4lray/gpt-assets/main/schematic.png" class="network-image">
    {}
</div>
'''.format("\n".join(
    f'<div class="indicator BB{i}">{("🟢" if blk.status=="Норма" else "🔴")}</div>'
    for i, blk in enumerate(st.session_state.blocks.values(), start=1)
))

st.components.v1.html(indicators_html, height=560)

st.markdown("### 📋 Деталі блоків")
for blk in st.session_state.blocks.values():
    with st.expander(f"{blk.name} — Статус: {blk.status}"):
        if blk.status != blk.STATUS_OFF:
            st.write(f"🌡 Температура: {blk.temperature} °C")
            st.write(f"💧 Вологість: {blk.humidity} %")
            st.write(f"💨 Вітер: {blk.wind} м/с")
        else:
            st.info("Блок вимкнено.")


# -------------------------------
# 📊 Візуалізація графіків нижче
# -------------------------------
st.markdown("## 📈 Показники ТП за останній замір")

data = {
    "Блок": [],
    "Температура": [],
    "Вологість": [],
    "Вітер": []
}
for blk in st.session_state.blocks.values():
    if blk.status != blk.STATUS_OFF:
        data["Блок"].append(blk.name)
        data["Температура"].append(blk.temperature)
        data["Вологість"].append(blk.humidity)
        data["Вітер"].append(blk.wind)

df_chart = pd.DataFrame(data)

if not df_chart.empty:
    st.line_chart(df_chart.set_index("Блок")[["Температура"]])
    st.line_chart(df_chart.set_index("Блок")[["Вологість"]])
    st.line_chart(df_chart.set_index("Блок")[["Вітер"]])
else:
    st.info("Немає активних блоків для побудови графіків.")


import csv
import os

# -------------------------------
# 🗂 Логування подій у CSV
# -------------------------------
event_file = "events.csv"
new_entries = []

for blk in st.session_state.blocks.values():
    if blk.status != blk.STATUS_OFF:
        new_entries.append({
            "Час": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Блок": blk.name,
            "Статус": blk.status,
            "Температура": blk.temperature,
            "Вологість": blk.humidity,
            "Вітер": blk.wind
        })

if new_entries:
    file_exists = os.path.isfile(event_file)
    with open(event_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_entries[0].keys())
        if not file_exists:
            writer.writeheader()
        writer.writerows(new_entries)

# -------------------------------
# 📈 Додаткові графіки
# -------------------------------
st.markdown("## 📊 Діаграми")

# Стан кожного блока — bar chart
status_counts = {}
for blk in st.session_state.blocks.values():
    status_counts[blk.status] = status_counts.get(blk.status, 0) + 1

st.bar_chart(pd.DataFrame.from_dict(status_counts, orient="index", columns=["Кількість"]))

# Темп vs Вологість (scatter)
scatter_data = pd.DataFrame([
    {
        "Температура": blk.temperature,
        "Вологість": blk.humidity,
        "Блок": blk.name
    }
    for blk in st.session_state.blocks.values()
    if blk.status != blk.STATUS_OFF
])

if not scatter_data.empty:
    st.markdown("### 🌡️ Діаграма розсіювання: Темп vs Вологість")
    st.altair_chart(
        alt.Chart(scatter_data).mark_circle(size=80).encode(
            x="Температура",
            y="Вологість",
            color="Блок",
            tooltip=["Блок", "Температура", "Вологість"]
        ).interactive(),
        use_container_width=True
    )
