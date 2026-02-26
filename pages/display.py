# pages/1_Affichage.py

import streamlit as st
import pandas as pd
import plotly.express as px
import io



st.header("Affichage")

# =============================
# INIT SESSION STATE
# =============================
if "dataframes" not in st.session_state:
    st.session_state.dataframes = {}

if "current_file" not in st.session_state:
    st.session_state.current_file = None

if "kpi_meta_prev" not in st.session_state:
    st.session_state.kpi_meta_prev = {}

# =============================
# HELPERS
# =============================
def _pct_delta(new, old):
    if old is None:
        return None
    try:
        old = float(old)
        new = float(new)
        if old == 0:
            return None
        return (new - old) / abs(old) * 100.0
    except Exception:
        return None

def kpi_row_cards(df_filtered: pd.DataFrame, key_prefix: str = "meta_kpi"):
    """Cards: lignes, colonnes, colonnes clés. Flèches + % pour lignes/colonnes."""
    prev = st.session_state.kpi_meta_prev

    n_rows = int(df_filtered.shape[0])
    n_cols = int(df_filtered.shape[1])

    all_cols = df_filtered.columns.tolist()
    default_keys = all_cols[: min(3, len(all_cols))]

    key_cols = st.multiselect(
        "Colonnes clés (affichées dans l’indicateur)",
        options=all_cols,
        default=default_keys,
        key=f"{key_prefix}_keycols",
    )
    key_cols_str = ", ".join(key_cols) if key_cols else "—"

    rows_pct = _pct_delta(n_rows, prev.get("rows"))
    cols_pct = _pct_delta(n_cols, prev.get("cols"))

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:
        st.metric(
            "Lignes",
            f"{n_rows:,}".replace(",", " "),
            None if rows_pct is None else f"{rows_pct:+.2f}%",
        )

    with c2:
        st.metric(
            "Colonnes",
            f"{n_cols:,}".replace(",", " "),
            None if cols_pct is None else f"{cols_pct:+.2f}%",
        )

    with c3:
        st.markdown(
            f"""
            <div style="padding:12px;border:1px solid rgba(255,255,255,0.15);
                        border-radius:12px;">
                <div style="font-size:0.85rem;opacity:0.8;">Colonnes clés</div>
                <div style="font-size:1.05rem;font-weight:600;white-space:nowrap;
                            overflow:hidden;text-overflow:ellipsis;">
                {key_cols_str}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    prev["rows"] = n_rows
    prev["cols"] = n_cols

# =============================
# SIDEBAR - IMPORT
# =============================
with st.sidebar:
    st.title("📂 Data Manager")

    uploaded_files = st.file_uploader(
        "Importer CSV ou Excel",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        key="upload_files_display",
    )

    if uploaded_files:
        for f in uploaded_files:
            try:
                if f.name.lower().endswith(".csv"):
                    df = pd.read_csv(f)
                else:
                    df = pd.read_excel(f)  # nécessite openpyxl en local/cloud

                st.session_state.dataframes[f.name] = df
                st.success(f"{f.name} chargé.")
            except Exception as e:
                st.error(f"Erreur {f.name}: {e}")

# =============================
# NO DATA
# =============================
if not st.session_state.dataframes:
    st.info("Importe un fichier CSV/Excel pour commencer.")
    st.stop()

# =============================
# SELECT FILE
# =============================
file_list = list(st.session_state.dataframes.keys())
st.session_state.current_file = st.selectbox("Sélectionner un fichier", file_list, key="file_select_display")

df = st.session_state.dataframes[st.session_state.current_file]
df_filtered = df.copy()

# =============================
# FILTERS
# =============================
st.sidebar.markdown("## 🎛 Filtres")

# reset filtres
if st.sidebar.button("Réinitialiser les filtres", key="reset_filters_display"):
    for col in df.columns:
        k = f"filter_{col}"
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()

for col in df.columns:
    if df[col].dtype == "object" or df[col].nunique(dropna=True) < 20:
        values = st.sidebar.multiselect(
            f"{col}",
            df[col].dropna().unique(),
            key=f"filter_{col}",
        )
        if values:
            df_filtered = df_filtered[df_filtered[col].isin(values)]

# =============================
# KPI META CARDS
# =============================
st.subheader("📌 Indicateurs clés")
kpi_row_cards(df_filtered)

# =============================
# TABLE
# =============================
st.divider()
st.subheader("📋 Données (filtrées)")
st.dataframe(df_filtered, use_container_width=True, height=420)

# =============================
# VISUALIZATION
# =============================
st.divider()
st.subheader("📈 Visualisation")

all_cols = df_filtered.columns.tolist()
num_cols = df_filtered.select_dtypes(include="number").columns.tolist()

c1, c2, c3 = st.columns(3)

with c1:
    chart_type = st.selectbox("Type graphique", ["Courbe", "Barres", "Scatter", "Circulaire"], key="chart_type_display")
with c2:
    x_axis = st.selectbox("Axe X", all_cols, key="x_axis_display")
with c3:
    y_axis = st.selectbox("Axe Y", num_cols if num_cols else all_cols, key="y_axis_display")

fig = None
if chart_type == "Courbe":
    fig = px.line(df_filtered, x=x_axis, y=y_axis)
elif chart_type == "Barres":
    fig = px.bar(df_filtered, x=x_axis, y=y_axis)
elif chart_type == "Scatter":
    fig = px.scatter(df_filtered, x=x_axis, y=y_axis)
elif chart_type == "Circulaire":
    try:
        agg = df_filtered.groupby(x_axis, dropna=False)[y_axis].sum().reset_index()
        fig = px.pie(agg, names=x_axis, values=y_axis)
    except Exception as e:
        st.error(f"Camembert impossible: {e}")

if fig:
    st.plotly_chart(fig, use_container_width=True)

# =============================
# EXPORT CSV
# =============================
st.divider()
st.subheader("📥 Export CSV")

csv_data = df_filtered.to_csv(index=False, sep=";").encode("utf-8")

st.download_button(
    "Télécharger les données filtrées (CSV)",
    data=csv_data,
    file_name="export_dashboard.csv",
    mime="text/csv",
    key="download_csv_display",
)