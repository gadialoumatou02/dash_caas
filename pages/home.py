# pages/0_Home.py
import streamlit as st

st.title("🏠 Home")
st.write("Bienvenue sur MyDash.")
st.write(f"Fichiers chargés: {len(st.session_state.get('dataframes', {}))}")