
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
        st.experimental_rerun()
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
