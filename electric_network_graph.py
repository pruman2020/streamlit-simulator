
import streamlit as st
from pyvis.network import Network
import networkx as nx
import pandas as pd
import tempfile
import os

st.set_page_config(layout="wide")
st.title("🔌 Граф електромережі з симуляцією подій")

# -------------------------------
# Побудова графа
# -------------------------------
G = nx.Graph()

nodes = {
    "Диспетчер": {"group": "control"},
    "GSM": {"group": "comm"},
    "TP1": {"group": "tp"},
    "TP2": {"group": "tp"},
    "TP3": {"group": "tp"},
    "TP4": {"group": "tp"},
}

edges = [
    ("Диспетчер", "GSM"),
    ("GSM", "TP1"),
    ("GSM", "TP2"),
    ("TP2", "TP3"),
    ("TP2", "TP4"),
]

for node, data in nodes.items():
    G.add_node(node, group=data["group"])

G.add_edges_from(edges)

# -------------------------------
# Симуляція події
# -------------------------------
selected_node = st.selectbox("Оберіть вузол для симуляції події", list(nodes.keys()))
event_type = st.selectbox("Тип події", ["Норма", "Ожеледь", "КЗ", "Обрив", "Вимкнено"])

status_colors = {
    "Норма": "green",
    "Ожеледь": "lightblue",
    "КЗ": "red",
    "Обрив": "orange",
    "Вимкнено": "gray"
}

# -------------------------------
# Візуалізація графа через PyVis
# -------------------------------
net = Network(height="600px", width="100%", directed=False)
for node in G.nodes():
    color = status_colors[event_type] if node == selected_node else "#dddddd"
    net.add_node(node, label=node, color=color)

for edge in G.edges():
    net.add_edge(edge[0], edge[1])

tmp_dir = tempfile.gettempdir()
path = os.path.join(tmp_dir, "graph.html")
net.show(path)

# Показуємо у Streamlit
with open(path, "r", encoding="utf-8") as f:
    html = f.read()
st.components.v1.html(html, height=640, scrolling=True)
