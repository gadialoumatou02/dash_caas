# app.py
import streamlit as st

# ⚠️ set_page_config DOIT être appelé une seule fois et tout en haut
st.set_page_config(page_title="MyDash", layout="wide")

# -----------------------------
# Etat partagé (session_state)
# -----------------------------
if "dataframes" not in st.session_state:
    st.session_state["dataframes"] = {}   # dict: filename -> pd.DataFrame
if "current_file" not in st.session_state:
    st.session_state["current_file"] = None
if "graphs" not in st.session_state:
    st.session_state["graphs"] = []       # liste de configs graph (max 4)
if "results" not in st.session_state:
    st.session_state["results"] = {}      # résultats calcul/ACP/régression
if "selected_file" not in st.session_state:
    st.session_state["selected_file"] = None

# -----------------------------
# Navigation PRO (Streamlit >= 1.32)
# -----------------------------
home_page = st.Page("app.py", title="Home", icon="🏠")                 # cette page (home)
display_page = st.Page("pages/1_Affichage.py", title="Affichage", icon="📊")
analyse_page = st.Page("pages/2_Calcul.py", title="Analyse", icon="🧮")

pg = st.navigation([home_page, display_page, analyse_page])
pg.run()

# -----------------------------
# Contenu HOME (affiché seulement si Home)
# -----------------------------
# Quand on est sur une autre page, pg.run() exécute cette autre page
# et le code ci-dessous ne sera pas affiché si tu mets un "guard".
if pg.title == "Home":
    st.title("🏠 Home")
    st.write("Bienvenue sur **MyDash**.")
    st.write("Utilise le menu à gauche pour naviguer : **Affichage** / **Analyse**.")

    st.divider()
    st.subheader("État actuel")
    st.write(f"Fichiers chargés : **{len(st.session_state['dataframes'])}**")
    if st.session_state["dataframes"]:
        st.write(list(st.session_state["dataframes"].keys())[:10])