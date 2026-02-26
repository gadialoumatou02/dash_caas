# main.py
import streamlit as st


# Etat partagé
if "dataframes" not in st.session_state:
    st.session_state["dataframes"] = {}
if "current_file" not in st.session_state:
    st.session_state["current_file"] = None
if "graphs" not in st.session_state:
    st.session_state["graphs"] = []
if "results" not in st.session_state:
    st.session_state["results"] = {}
if "selected_file" not in st.session_state:
    st.session_state["selected_file"] = None

# Navigation PRO
home_page = st.Page("main.py", title="Home", icon="🏠")                 # cette page (home)
display_page = st.Page("pages/display.py", title="Affichage", icon="📊")
analyse_page = st.Page("pages/calcul.py", title="Analyse", icon="🧮")

pg = st.navigation([home_page, display_page, analyse_page])
pg.run()    


