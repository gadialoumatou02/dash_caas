# pages/1_Affichage.py

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io

st.header("📊 Dashboard - Affichage des données")

# =============================
# INITIALISATION SESSION STATE
# =============================

if "dataframes" not in st.session_state:
    st.session_state.dataframes = {}

if "current_file" not in st.session_state:
    st.session_state.current_file = None

if "graphs" not in st.session_state:
    st.session_state.graphs = []

# =============================
# SIDEBAR - IMPORT DATA
# =============================

with st.sidebar:
    st.title("📂 Data Manager")

    uploaded_files = st.file_uploader(
        "Importer CSV ou Excel",
        type=["csv", "xlsx"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for file in uploaded_files:
            try:
                if file.name.endswith(".csv"):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)

                st.session_state.dataframes[file.name] = df
                st.success(f"{file.name} chargé.")
            except Exception as e:
                st.error(f"Erreur avec {file.name}: {e}")

    if st.session_state.dataframes:
        st.markdown("### 📁 Fichiers disponibles")
        st.write(list(st.session_state.dataframes.keys()))

# =============================
# AUCUNE DONNÉE
# =============================

if not st.session_state.dataframes:
    st.info("Importe un fichier CSV ou Excel pour commencer.")
    st.stop()

# =============================
# SELECTION FICHIER
# =============================

file_list = list(st.session_state.dataframes.keys())

st.session_state.current_file = st.selectbox(
    "Sélectionner un fichier",
    file_list
)

df = st.session_state.dataframes[st.session_state.current_file]
df_filtered = df.copy()

# =============================
# FILTRES TYPE POWER BI
# =============================

st.sidebar.markdown("## 🎛 Filtres")

for col in df.columns:
    if df[col].dtype == "object" or df[col].nunique() < 20:
        values = st.sidebar.multiselect(
            f"{col}",
            df[col].dropna().unique()
        )
        if values:
            df_filtered = df_filtered[df_filtered[col].isin(values)]

    # elif pd.api.types.is_numeric_dtype(df[col]):
    #     min_val = float(df[col].min())
    #     max_val = float(df[col].max())
    #     slider = st.sidebar.slider(
    #         f"{col}",
    #         min_val,
    #         max_val,
    #         (min_val, max_val)
    #     )
    #     df_filtered = df_filtered[
    #         (df_filtered[col] >= slider[0]) &
    #         (df_filtered[col] <= slider[1])
    #     ]
# =============================
# TABLE DONNÉES
# =============================

st.divider()
st.subheader("📋 Données")

st.dataframe(df_filtered, use_container_width=True)

# =============================
# KPI CARDS
# =============================

st.subheader("📌 Indicateurs Clés")

num_cols = df_filtered.select_dtypes(include="number").columns

if len(num_cols) > 0:
    kpi_cols = st.columns(min(4, len(num_cols)))

    for i, col in enumerate(num_cols[:4]):
        with kpi_cols[i]:
            st.metric(
                label=col,
                value=f"{df_filtered[col].sum():,.2f}"
            )

# =============================
# ZONE GRAPHIQUE
# =============================

st.divider()
st.subheader("📈 Visualisation")

all_cols = df_filtered.columns.tolist()
num_cols = df_filtered.select_dtypes(include="number").columns.tolist()

col1, col2, col3 = st.columns(3)

with col1:
    chart_type = st.selectbox(
        "Type graphique",
        ["Courbe", "Barres", "Scatter", "Circulaire"]
    )

with col2:
    x_axis = st.selectbox("Axe X", all_cols)

with col3:
    y_axis = st.selectbox("Axe Y", num_cols if num_cols else all_cols)

# Création graphique dynamique

fig = None

if chart_type == "Courbe":
    fig = px.line(df_filtered, x=x_axis, y=y_axis)

elif chart_type == "Barres":
    fig = px.bar(df_filtered, x=x_axis, y=y_axis)

elif chart_type == "Scatter":
    fig = px.scatter(df_filtered, x=x_axis, y=y_axis)

elif chart_type == "Circulaire":
    agg = df_filtered.groupby(x_axis)[y_axis].sum().reset_index()
    fig = px.pie(agg, names=x_axis, values=y_axis)

if fig:
    st.plotly_chart(fig, use_container_width=True)



# =============================
# EXPORT EXCEL
# =============================

st.divider()
st.subheader("📥 Export CSV")

csv_data = df_filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Télécharger les données filtrées (CSV)",
    data=csv_data,
    file_name="export_dashboard.csv",
    mime="text/csv",
    key="download_csv"
)