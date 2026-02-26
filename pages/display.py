# pages/2_Calcul.py

import streamlit as st
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression

st.header("🧮 Calculs & Analyses")

# =============================
# INITIALISATION SESSION STATE
# =============================

if "dataframes" not in st.session_state or not st.session_state.dataframes:
    st.info("Charge d'abord des fichiers CSV ou Excel dans la page Affichage.")
    st.stop()

if "results" not in st.session_state:
    st.session_state.results = {}

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

# =============================
# SELECTION DU FICHIER
# =============================

file_list = list(st.session_state.dataframes.keys())

selected_index = 0
if st.session_state.selected_file in file_list:
    selected_index = file_list.index(st.session_state.selected_file)

file_name = st.selectbox(
    "Choisir un fichier",
    file_list,
    index=selected_index
)

st.session_state.selected_file = file_name
df = st.session_state.dataframes[file_name]

st.subheader("Aperçu du dataset")
st.dataframe(df.head(200), use_container_width=True)

# =============================
# CHOIX OPERATION
# =============================

operation = st.selectbox(
    "Choisir une opération",
    [
        "Calcul simple",
        "Analyse en Composantes Principales (ACP)",
        "Modèle de régression linéaire",
        "Formule personnalisée"
    ]
)

# =============================
# CALCUL SIMPLE
# =============================

if operation == "Calcul simple":

    num = df.select_dtypes(include="number")

    if num.empty:
        st.error("Aucune colonne numérique disponible.")
    else:
        res = num.agg(["sum", "mean", "std"]).T
        res.columns = ["Somme", "Moyenne", "Écart-type"]

        st.subheader("Résultats")
        st.dataframe(res, use_container_width=True)

        st.session_state.results[file_name] = res


# =============================
# ACP
# =============================

elif operation == "Analyse en Composantes Principales (ACP)":

    num = df.select_dtypes(include="number").dropna()

    if num.shape[1] < 2:
        st.error("Il faut au moins deux colonnes numériques pour effectuer une ACP.")
    else:
        n_components = st.slider(
            "Nombre de composantes",
            2,
            min(6, num.shape[1]),
            2
        )

        pca = PCA(n_components=n_components)
        components = pca.fit_transform(num)

        st.subheader("Variance expliquée")
        st.write(pca.explained_variance_ratio_)

        comp_df = pd.DataFrame(
            components,
            columns=[f"PC{i+1}" for i in range(n_components)]
        )

        st.subheader("Composantes principales (aperçu)")
        st.dataframe(comp_df.head(50), use_container_width=True)

        st.session_state.results[file_name] = {
            "variance_expliquee": pca.explained_variance_ratio_,
            "composantes": comp_df
        }


# =============================
# REGRESSION LINEAIRE
# =============================

elif operation == "Modèle de régression linéaire":

    num = df.select_dtypes(include="number").dropna()

    if num.shape[1] < 2:
        st.error("Il faut au moins deux colonnes numériques.")
    else:
        y_col = st.selectbox(
            "Variable cible (Y)",
            num.columns.tolist(),
            index=len(num.columns) - 1
        )

        x_cols = [c for c in num.columns if c != y_col]

        selected_x = st.multiselect(
            "Variables explicatives (X)",
            x_cols,
            default=x_cols[:min(3, len(x_cols))]
        )

        if not selected_x:
            st.warning("Sélectionne au moins une variable X.")
        else:
            X = num[selected_x]
            y = num[y_col]

            model = LinearRegression()
            model.fit(X, y)
            score = model.score(X, y)

            st.subheader("Résultats")
            st.write(f"**R² : {score:.4f}**")

            coef = pd.Series(
                model.coef_,
                index=selected_x,
                name="Coefficient"
            )

            st.dataframe(coef.to_frame(), use_container_width=True)

            st.session_state.results[file_name] = {
                "R2": score,
                "coefficients": coef
            }


# =============================
# FORMULE PERSONNALISEE
# =============================

elif operation == "Formule personnalisée":

    st.caption(
        "Format conseillé : `new_col = `Col A` + `Col B`` "
        "(mettre les colonnes entre backticks si elles contiennent des espaces)"
    )

    formula = st.text_input("Formule")

    if st.button("Appliquer la formule"):

        try:
            if not formula.strip():
                raise ValueError("Veuillez saisir une formule.")

            # Applique directement sur le dataframe partagé
            st.session_state.dataframes[file_name].eval(
                formula,
                inplace=True,
                engine="python"
            )

            st.success("Formule appliquée avec succès.")

            st.dataframe(
                st.session_state.dataframes[file_name].head(200),
                use_container_width=True
            )

        except Exception as e:
            st.error(f"Erreur : {e}")