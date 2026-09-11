import os

import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


# ============================================================
# CAMINHOS
# ============================================================

PASTA_PREVISAO = os.path.dirname(os.path.abspath(__file__))

PASTA_SITE = os.path.abspath(
    os.path.join(PASTA_PREVISAO, "..", "site")
)

ARQUIVO_EXCEL = os.path.join(
    PASTA_SITE,
    "dados_coletados.xlsx"
)

ARQUIVO_SNAPSHOT = os.path.join(
    PASTA_PREVISAO,
    "modelo_snapshot.pkl"
)


# ============================================================
# CARREGAR E PREPARAR OS DADOS
# ============================================================

def carregar_e_preparar_dados(caminho_excel):

    xls = pd.ExcelFile(caminho_excel)

    dfs = []

    for sheet_name in xls.sheet_names:

        df_sheet = pd.read_excel(
            xls,
            sheet_name=sheet_name
        )

        # Converte Data explicitamente para datetime
        df_sheet["Data"] = pd.to_datetime(
            df_sheet["Data"]
        )

        # Transforma as colunas 00h, 01h, 02h... em linhas
        df_melted = df_sheet.melt(
            id_vars=["Data"],
            var_name="Hora",
            value_name=sheet_name
        )

        # Monta DataHora
        df_melted["DataHora"] = pd.to_datetime(
            df_melted["Data"].dt.strftime("%Y-%m-%d")
            + " "
            + df_melted["Hora"]
                .astype(str)
                .str.replace("h", ":00", regex=False)
        )

        dfs.append(
            df_melted.drop(
                columns=["Data", "Hora"]
            )
        )

    # Junta todas as planilhas pela DataHora
    df_final = dfs[0]

    for df in dfs[1:]:

        df_final = pd.merge(
            df_final,
            df,
            on="DataHora",
            how="outer"
        )

    # Ordena e preenche valores ausentes
    df_final = (
        df_final
        .sort_values("DataHora")
        .ffill()
        .bfill()
        .dropna()
    )

    return df_final


# ============================================================
# CRIAR JANELAS DE TREINO
# ============================================================

def criar_janelas_treino(
    df,
    tamanho_janela=24,
    horizonte=24
):

    # Todas as colunas, exceto DataHora
    colunas_features = [
        c for c in df.columns
        if c != "DataHora"
    ]

    dados = df[colunas_features].values

    # Índice da temperatura
    temp_idx = colunas_features.index(
        "Temp. Ins. (C)"
    )

    X = []
    y = []

    # 24 horas passadas -> 24 horas futuras
    for i in range(
        len(dados)
        - tamanho_janela
        - horizonte
        + 1
    ):

        X.append(
            dados[
                i:i + tamanho_janela
            ].flatten()
        )

        y.append(
            dados[
                i + tamanho_janela:
                i + tamanho_janela + horizonte,
                temp_idx
            ]
        )

    return (
        np.array(X),
        np.array(y),
        colunas_features
    )


# ============================================================
# EXECUÇÃO DO TREINO
# ============================================================

print("Carregando dados...")
print(f"Arquivo: {ARQUIVO_EXCEL}")

if not os.path.exists(ARQUIVO_EXCEL):
    raise FileNotFoundError(
        f"Arquivo não encontrado:\n{ARQUIVO_EXCEL}"
    )

df = carregar_e_preparar_dados(
    ARQUIVO_EXCEL
)

print(f"Registros carregados: {len(df)}")

X, y, colunas_features = criar_janelas_treino(df)

print(f"Formato de X: {X.shape}")
print(f"Formato de y: {y.shape}")


# ============================================================
# DIVISÃO DOS DADOS
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.15,
    random_state=42
)


# ============================================================
# TREINAMENTO
# ============================================================

print("Treinando Random Forest...")

modelo = RandomForestRegressor(
    n_estimators=50,
    random_state=42
)

modelo.fit(
    X_train,
    y_train
)


# ============================================================
# SALVAR SNAPSHOT
# ============================================================

snapshot = {
    "modelo": modelo,
    "colunas_features": colunas_features
}

joblib.dump(
    snapshot,
    ARQUIVO_SNAPSHOT
)

print()
print("========================================")
print("TREINAMENTO CONCLUÍDO")
print("========================================")
print(f"Snapshot salvo em:")
print(ARQUIVO_SNAPSHOT)
print("========================================")