# app.py
import streamlit as st



st.set_page_config(page_title="MyDash", layout="wide")

# Etat partagé (équivalent controller.shared_data)
if "dataframes" not in st.session_state:
    st.session_state["dataframes"] = {}   # dict: filename -> pd.DataFrame
if "current_file" not in st.session_state:
    st.session_state["current_file"] = None
if "graphs" not in st.session_state:
    st.session_state["graphs"] = []       # liste de configs graph (max 4)

st.title("MyDash")
st.write("Utilise le menu à gauche pour naviguer : **Affichage** / **Calcul**.")
