# pages/0_Home.py
import streamlit as st

st.title("🏠 Home")
st.write("Bienvenue sur **MyDash**.")
st.write("Utilise le menu à gauche pour naviguer : **Affichage** / **Analyse**.")

st.divider()
st.subheader("État actuel")
st.write(f"Fichiers chargés : **{len(st.session_state.get('dataframes', {}))}**")

if st.session_state.get("dataframes"):
    st.write(list(st.session_state["dataframes"].keys())[:10])