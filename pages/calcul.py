# pages/2_Calcul.py

import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression



st.header("🧮 Calcul & Analyse")

# =============================
# INIT SESSION STATE
# =============================
if "dataframes" not in st.session_state or not st.session_state.dataframes:
    st.info("Charge d'abord des fichiers CSV/Excel dans la page Affichage.")
    st.stop()

if "results" not in st.session_state:
    st.session_state.results = {}

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

# =============================
# SELECT FILE
# =============================
file_list = list(st.session_state.dataframes.keys())
selected_index = file_list.index(st.session_state.selected_file) if st.session_state.selected_file in file_list else 0

file_name = st.selectbox("Choisir un fichier", file_list, index=selected_index, key="file_select_calc")
st.session_state.selected_file = file_name

df = st.session_state.dataframes[file_name]

st.subheader("Aperçu dataset")
st.dataframe(df.head(200), use_container_width=True)

# =============================
# OPERATION
# =============================
operation = st.selectbox(
    "Choisir une opération",
    [
        "Calcul simple",
        "Analyse en Composantes Principales (ACP)",
        "Modèle de régression linéaire",
        "Formule personnalisée",
    ],
    key="operation_calc",
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
# ACP + GRAPHIQUES AUTO
# =============================
elif operation == "Analyse en Composantes Principales (ACP)":
    num = df.select_dtypes(include="number").dropna()
    if num.shape[1] < 2:
        st.error("Il faut au moins deux colonnes numériques pour l'ACP.")
    else:
        n_components = st.slider("Nombre de composantes", 2, min(6, num.shape[1]), 2, key="pca_ncomp")
        pca = PCA(n_components=n_components)
        components = pca.fit_transform(num)

        st.subheader("Variance expliquée")
        var = pca.explained_variance_ratio_
        var_df = pd.DataFrame({"Composante": [f"PC{i+1}" for i in range(len(var))], "Variance": var})
        st.plotly_chart(px.bar(var_df, x="Composante", y="Variance"), use_container_width=True)

        if components.shape[1] >= 2:
            comp2 = pd.DataFrame(components[:, :2], columns=["PC1", "PC2"])
            st.subheader("Projection ACP (PC1 vs PC2)")
            st.plotly_chart(px.scatter(comp2, x="PC1", y="PC2"), use_container_width=True)

        comp_df = pd.DataFrame(components, columns=[f"PC{i+1}" for i in range(n_components)])
        st.subheader("Composantes principales (aperçu)")
        st.dataframe(comp_df.head(50), use_container_width=True)

        st.session_state.results[file_name] = {"variance": var, "components": comp_df}

# =============================
# REGRESSION + PREDICTION LIVE
# =============================
elif operation == "Modèle de régression linéaire":
    num = df.select_dtypes(include="number").dropna()
    if num.shape[1] < 2:
        st.error("Il faut au moins deux colonnes numériques.")
    else:
        y_col = st.selectbox("Variable cible (Y)", num.columns.tolist(), index=len(num.columns) - 1, key="reg_y")
        x_cols = [c for c in num.columns if c != y_col]
        selected_x = st.multiselect(
            "Variables explicatives (X)",
            x_cols,
            default=x_cols[: min(3, len(x_cols))],
            key="reg_x",
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

            coef = pd.Series(model.coef_, index=selected_x, name="Coefficient")
            st.dataframe(coef.to_frame(), use_container_width=True)

            # --- Prediction live ---
            st.subheader("📈 Prédiction live")
            input_row = {}
            for col in selected_x:
                col_min = float(X[col].min())
                col_max = float(X[col].max())
                default_val = float(X[col].median())
                input_row[col] = st.slider(col, col_min, col_max, default_val, key=f"pred_{col}")

            X_new = pd.DataFrame([input_row])
            y_pred = model.predict(X_new)[0]
            st.metric("Prédiction", f"{y_pred:,.4f}".replace(",", " ").replace(".", ","))

            st.session_state.results[file_name] = {"R2": score, "coef": coef, "pred_example": input_row, "pred": y_pred}

# =============================
# FORMULE PERSONNALISEE
# =============================
elif operation == "Formule personnalisée":

    st.caption("Format conseillé : new_col = colA + colB")

    formula = st.text_input("Formule")

    if st.button("Appliquer la formule"):

        try:
            if not formula.strip():
                raise ValueError("Veuillez saisir une formule.")

            df_original = st.session_state.dataframes[file_name]

            # =============================
            # 1️⃣ Création noms sécurisés
            # =============================

            safe_columns = {}
            for col in df_original.columns:
                safe_col = (
                    col.replace(" ", "_")
                        .replace("-", "_")
                        .replace("/", "_")
                        .replace(".", "_")
                        .replace("(", "")
                        .replace(")", "")
                )

                # Si commence par chiffre → préfixer
                if safe_col[0].isdigit():
                    safe_col = "col_" + safe_col

                safe_columns[col] = safe_col

            # =============================
            # 2️⃣ Copie temporaire
            # =============================

            df_safe = df_original.rename(columns=safe_columns).copy()

            # Adapter la formule
            safe_formula = formula
            for original, safe in safe_columns.items():
                safe_formula = safe_formula.replace(original, safe)

            # =============================
            # 3️⃣ Eval sécurisé
            # =============================

            df_safe.eval(safe_formula, inplace=True, engine="python")

            # =============================
            # 4️⃣ Restaurer noms originaux
            # =============================

            reverse_mapping = {v: k for k, v in safe_columns.items()}
            df_safe.rename(columns=reverse_mapping, inplace=True)

            # Mise à jour session_state
            st.session_state.dataframes[file_name] = df_safe

            st.success("Formule appliquée avec succès.")
            st.dataframe(df_safe.head(200), use_container_width=True)

        except Exception as e:
            st.error(f"Erreur : {e}")