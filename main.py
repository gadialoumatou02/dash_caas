# main.py
import streamlit as st

# init state (optionnel mais utile)
st.session_state.setdefault("dataframes", {})
st.session_state.setdefault("current_file", None)
st.session_state.setdefault("graphs", [])
st.session_state.setdefault("results", {})
st.session_state.setdefault("selected_file", None)

home = st.Page("pages/home.py", title="Home", icon="🏠")
display = st.Page("pages/display.py", title="Affichage", icon="📊")
analyse = st.Page("pages/calcul.py", title="Analyse", icon="🧮")

st.navigation([home, display, analyse]).run()