import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split

# ============================================================
# CAMINHOS
# ============================================================

PASTA_PREVISAO = os.path.dirname(os.path.abspath(__file__))

PASTA_SITE = os.path.abspath(os.path.join(PASTA_PREVISAO, "..", "site"))

ARQUIVO_EXCEL = os.path.join(PASTA_SITE, "dados_coletados.xlsx")

ARQUIVO_SNAPSHOT = os.path.join(PASTA_PREVISAO, "modelo_snapshot.pkl")


# ============================================================
# CARREGAR E PREPARAR OS DADOS
# ============================================================


def carregar_e_preparar_dados(caminho_excel):

  xls = pd.ExcelFile(caminho_excel)

  dfs = []

  for sheet_name in xls.sheet_names:

    df_sheet = pd.read_excel(xls, sheet_name=sheet_name)

    # Converte Data explicitamente para datetime
    df_sheet["Data"] = pd.to_datetime(df_sheet["Data"])

    # Transforma as colunas 00h, 01h, 02h... em linhas
    df_melted = df_sheet.melt(
        id_vars=["Data"], var_name="Hora", value_name=sheet_name
    )

    # Monta DataHora
    df_melted["DataHora"] = pd.to_datetime(
        df_melted["Data"].dt.strftime("%Y-%m-%d")
        + " "
        + df_melted["Hora"].astype(str).str.replace("h", ":00", regex=False)
    )

    dfs.append(df_melted.drop(columns=["Data", "Hora"]))

  # Junta todas as planilhas pela DataHora
  df_final = dfs[0]

  for df in dfs[1:]:

    df_final = pd.merge(df_final, df, on="DataHora", how="outer")

  # Ordena e preenche valores ausentes
  df_final = df_final.sort_values("DataHora").ffill().bfill().dropna()

  return df_final


# ============================================================
# CRIAR JANELAS DE TREINO (COM DIRECIONAMENTO DIRETO PARA MÉTRICAS)
# ============================================================


def criar_janelas_treino(df, tamanho_janela=24, horizonte=24):

  colunas_features = [c for c in df.columns if c != "DataHora"]

  dados = df[colunas_features].values

  idx_temp = colunas_features.index("Temp. Ins. (C)")
  idx_max = colunas_features.index("Temp. Max. (C)")
  idx_min = colunas_features.index("Temp. Min. (C)")

  X = []
  y_seq = []
  y_media = []
  y_min = []
  y_max = []

  # Passo de amostragem ajustado para simular entradas diárias independentes da hora
  for i in range(len(dados) - tamanho_janela - horizonte + 1):

    janela_x = dados[i : i + tamanho_janela]
    janela_y_temp = dados[
        i + tamanho_janela : i + tamanho_janela + horizonte, idx_temp
    ]
    janela_y_max = dados[
        i + tamanho_janela : i + tamanho_janela + horizonte, idx_max
    ]
    janela_y_min = dados[
        i + tamanho_janela : i + tamanho_janela + horizonte, idx_min
    ]

    X.append(janela_x.flatten())
    y_seq.append(janela_y_temp)
    y_media.append(np.mean(janela_y_temp))
    y_min.append(np.min(janela_y_min))
    y_max.append(np.max(janela_y_max))

  return (
      np.array(X),
      np.array(y_seq),
      np.array(y_media),
      np.array(y_min),
      np.array(y_max),
      colunas_features,
  )


# ============================================================
# EXECUÇÃO DO TREINO
# ============================================================

print("Carregando dados...")
print(f"Arquivo: {ARQUIVO_EXCEL}")

if not os.path.exists(ARQUIVO_EXCEL):
  raise FileNotFoundError(f"Arquivo não encontrado:\n{ARQUIVO_EXCEL}")

df = carregar_e_preparar_dados(ARQUIVO_EXCEL)

print(f"Registros carregados: {len(df)}")

X, y, y_media, y_min, y_max, colunas_features = criar_janelas_treino(df)

print(f"Formato de X: {X.shape}")
print(f"Formato de y: {y.shape}")


# ============================================================
# DIVISÃO DOS DADOS
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.15, random_state=42
)

(
    _,
    _,
    ymed_tr,
    ymed_te,
    ymin_tr,
    ymin_te,
    ymax_tr,
    ymax_te,
) = train_test_split(
    X, y_media, y_min, y_max, test_size=0.15, random_state=42
)


# ============================================================
# TREINAMENTO DE MODELOS ESPECIALIZADOS
# ============================================================

print("Treinando modelos de precisão meteorológica...")

# Modelo 1: Previsão da série horária
modelo = RandomForestRegressor(n_estimators=100, random_state=42)
modelo.fit(X_train, y_train)

# Modelos 2, 3 e 4: Estimadores diretos para Média, Mínima e Máxima
modelo_media = ExtraTreesRegressor(n_estimators=100, random_state=42)
modelo_media.fit(X_train, ymed_tr)

modelo_min = ExtraTreesRegressor(n_estimators=100, random_state=42)
modelo_min.fit(X_train, ymin_tr)

modelo_max = ExtraTreesRegressor(n_estimators=100, random_state=42)
modelo_max.fit(X_train, ymax_tr)


# ============================================================
# SALVAR SNAPSHOT
# ============================================================

snapshot = {
    "modelo": modelo,
    "modelo_media": modelo_media,
    "modelo_min": modelo_min,
    "modelo_max": modelo_max,
    "colunas_features": colunas_features,
}

joblib.dump(snapshot, ARQUIVO_SNAPSHOT)

print()
print("========================================")
print("TREINAMENTO CONCLUÍDO")
print("========================================")
print(f"Snapshot salvo em:")
print(ARQUIVO_SNAPSHOT)
print("========================================")