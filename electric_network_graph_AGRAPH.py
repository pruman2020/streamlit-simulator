
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

st.set_page_config(layout="wide")
st.title("🔌 Інтерактивний граф електромережі")

# -------------------------------
# Визначення вузлів і ребер
# -------------------------------
nodes = [
    Node(id="Диспетчер", label="Диспетчер", size=25, color="lightgray"),
    Node(id="GSM", label="GSM", size=20, color="lightblue"),
    Node(id="TP1", label="TP1", color="green"),
    Node(id="TP2", label="TP2", color="green"),
    Node(id="TP3", label="TP3", color="green"),
    Node(id="TP4", label="TP4", color="green")
]

edges = [
    Edge(source="Диспетчер", target="GSM"),
    Edge(source="GSM", target="TP1"),
    Edge(source="GSM", target="TP2"),
    Edge(source="TP2", target="TP3"),
    Edge(source="TP2", target="TP4")
]

# -------------------------------
# Симуляція події
# -------------------------------
event_type = st.selectbox("Оберіть подію", ["Норма", "Ожеледь", "КЗ", "Обрив", "Вимкнено"])
target_node = st.selectbox("На який елемент застосувати подію?", ["TP1", "TP2", "TP3", "TP4"])

status_colors = {
    "Норма": "green",
    "Ожеледь": "skyblue",
    "КЗ": "red",
    "Обрив": "orange",
    "Вимкнено": "gray"
}

# Застосування кольору
for node in nodes:
    if node.id == target_node:
        node.color = status_colors.get(event_type, "green")

# -------------------------------
# Конфігурація графа
# -------------------------------
config = Config(width=800,
                height=500,
                directed=False,
                physics=True,
                hierarchical=False)

agraph(nodes=nodes, edges=edges, config=config)
