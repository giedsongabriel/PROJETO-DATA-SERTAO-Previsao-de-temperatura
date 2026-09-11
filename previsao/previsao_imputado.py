import pandas as pd
import numpy as np
import joblib
import os
import requests

from datetime import datetime, timedelta


# ============================================================
# CAMINHOS DO PROJETO
# ============================================================

PASTA_PREVISAO = os.path.dirname(os.path.abspath(__file__))

PASTA_SITE = os.path.abspath(
    os.path.join(PASTA_PREVISAO, "..", "site")
)

# Snapshot do modelo
ARQUIVO_SNAPSHOT = os.path.join(
    PASTA_PREVISAO,
    "modelo_snapshot.pkl"
)

# Arquivo Excel com os dados coletados
ARQUIVO_EXCEL = os.path.join(
    PASTA_SITE,
    "dados_coletados.xlsx"
)

# Histórico das previsões
ARQUIVO_HISTORICO = os.path.join(
    PASTA_SITE,
    "historico_previsoes2.csv"
)


# ============================================================
# 1. CARREGAR O SNAPSHOT DO MODELO
# ============================================================

if not os.path.exists(ARQUIVO_SNAPSHOT):
    raise FileNotFoundError(
        f"Snapshot do modelo não encontrado:\n{ARQUIVO_SNAPSHOT}"
    )

snapshot = joblib.load(ARQUIVO_SNAPSHOT)

modelo = snapshot["modelo"]
colunas_features = snapshot["colunas_features"]


# ============================================================
# 2. BUSCAR DADOS METEOROLÓGICOS NA API OPEN-METEO
# ============================================================

def obter_dados_meteorologicos_api(
    data_alvo_str,
    lat=-8.5152,
    lon=-39.3101
):
    """
    Busca média, mínima e máxima diárias de temperatura
    para uma determinada data na API Open-Meteo.

    Coordenadas configuradas para Cabrobó - PE.
    """

    try:

        url = "https://api.open-meteo.com/v1/forecast"

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_mean",
                "temperature_2m_min",
                "temperature_2m_max"
            ],
            "timezone": "America/Recife",
            "start_date": data_alvo_str,
            "end_date": data_alvo_str
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 200:

            dados = response.json()
            daily = dados["daily"]

            return {
                "media": daily["temperature_2m_mean"][0],
                "min": daily["temperature_2m_min"][0],
                "max": daily["temperature_2m_max"][0]
            }

        return None

    except Exception as e:

        print(
            "Aviso: Não foi possível obter dados "
            f"meteorológicos online. Erro: {e}"
        )

        return None


# ============================================================
# 3. CARREGAR OS DADOS DAS ÚLTIMAS 24 HORAS
# ============================================================

def obter_dados_ultimo_dia(
    caminho_excel,
    colunas_features
):

    xls = pd.ExcelFile(caminho_excel)

    dfs = []

    for sheet in colunas_features:

        df_sheet = pd.read_excel(
            xls,
            sheet_name=sheet
        )

        df_sheet["Data"] = pd.to_datetime(
            df_sheet["Data"]
        )

        df_melted = df_sheet.melt(
            id_vars=["Data"],
            var_name="Hora",
            value_name=sheet
        )

        df_melted["DataHora"] = pd.to_datetime(
            df_melted["Data"].dt.strftime("%Y-%m-%d")
            + " "
            + df_melted["Hora"]
                .astype(str)
                .str.replace(
                    "h",
                    ":00",
                    regex=False
                )
        )

        dfs.append(
            df_melted.drop(
                columns=["Data", "Hora"]
            )
        )

    df_tudo = dfs[0]

    for df in dfs[1:]:

        df_tudo = pd.merge(
            df_tudo,
            df,
            on="DataHora",
            how="outer"
        )

    df_tudo = (
        df_tudo
        .sort_values("DataHora")
        .ffill()
        .bfill()
        .reset_index(drop=True)
    )

    df_ultimo_dia = df_tudo.tail(24).copy()

    data_ultimo_registro = (
        df_ultimo_dia["DataHora"].max()
    )

    vetor_input = (
        df_ultimo_dia[colunas_features]
        .values
        .flatten()
    )

    return (
        vetor_input.reshape(1, -1),
        data_ultimo_registro
    )


# ============================================================
# 4. VERIFICAR O ARQUIVO DE DADOS
# ============================================================

if not os.path.exists(ARQUIVO_EXCEL):
    raise FileNotFoundError(
        f"Arquivo de dados não encontrado:\n{ARQUIVO_EXCEL}"
    )

print("----------------------------------------")
print("CARREGANDO MODELO")
print(f"Snapshot: {ARQUIVO_SNAPSHOT}")
print(f"Dados:    {ARQUIVO_EXCEL}")
print("----------------------------------------")


# ============================================================
# 5. GERAR A PREVISÃO
# ============================================================

input_ultimo_dia, data_ultimo_registro = (
    obter_dados_ultimo_dia(
        ARQUIVO_EXCEL,
        colunas_features
    )
)

previsao_proximas_24h = modelo.predict(
    input_ultimo_dia
)[0]


# ============================================================
# 6. CALCULAR MÉTRICAS PREVISTAS
# ============================================================

temp_media_prevista = np.mean(
    previsao_proximas_24h
)

temp_min_prevista = np.min(
    previsao_proximas_24h
)

temp_max_prevista = np.max(
    previsao_proximas_24h
)

data_previsao = (
    data_ultimo_registro + timedelta(days=1)
).strftime("%Y-%m-%d")

data_execucao = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


# ============================================================
# 7. BUSCAR DADOS DA API EXTERNA
# ============================================================

dados_api = obter_dados_meteorologicos_api(
    data_previsao,
    lat=-8.5152,
    lon=-39.3101
)


if dados_api:

    real_media = dados_api["media"]
    real_min = dados_api["min"]
    real_max = dados_api["max"]

    diff_media = (
        temp_media_prevista - real_media
    )

    diff_min = (
        temp_min_prevista - real_min
    )

    diff_max = (
        temp_max_prevista - real_max
    )

else:

    real_media = None
    real_min = None
    real_max = None

    diff_media = None
    diff_min = None
    diff_max = None


# ============================================================
# 8. EXIBIR RESULTADOS
# ============================================================

print(
    f"ÚLTIMA LEITURA COLETADA: "
    f"{data_ultimo_registro.strftime('%Y-%m-%d %H:%M')}"
)

print(
    f"PREVISÃO PARA O DIA: {data_previsao}"
)

print(
    f"Temp. Média Prevista: "
    f"{temp_media_prevista:.2f} °C"
)

print(
    f"Temp. Mínima Prevista: "
    f"{temp_min_prevista:.2f} °C"
)

print(
    f"Temp. Máxima Prevista: "
    f"{temp_max_prevista:.2f} °C"
)


if dados_api:

    print("----------------------------------------")
    print(
        "DADOS OBTIDOS DA API METEOROLÓGICA "
        "(CABROBÓ - PE):"
    )

    print(
        f"Temp. Média Externa: "
        f"{real_media:.2f} °C "
        f"(Variação: {diff_media:+.2f} °C)"
    )

    print(
        f"Temp. Mínima Externa: "
        f"{real_min:.2f} °C "
        f"(Variação: {diff_min:+.2f} °C)"
    )

    print(
        f"Temp. Máxima Externa: "
        f"{real_max:.2f} °C "
        f"(Variação: {diff_max:+.2f} °C)"
    )

else:

    print("----------------------------------------")
    print(
        "Não foi possível consultar as "
        "temperaturas na API externa."
    )

print("----------------------------------------")


# ============================================================
# 9. SALVAR NO HISTÓRICO
# ============================================================

nova_previsao = pd.DataFrame([
    {
        "Data_Execucao": data_execucao,

        "Data_Ultima_Leitura":
            data_ultimo_registro.strftime(
                "%Y-%m-%d %H:%M"
            ),

        "Data_Prevista": data_previsao,

        "Temp_Media_Prevista_C":
            round(temp_media_prevista, 2),

        "Temp_Min_Prevista_C":
            round(temp_min_prevista, 2),

        "Temp_Max_Prevista_C":
            round(temp_max_prevista, 2),

        "Temp_Media_API_Externa_C":
            round(real_media, 2)
            if real_media is not None
            else "N/A",

        "Temp_Min_API_Externa_C":
            round(real_min, 2)
            if real_min is not None
            else "N/A",

        "Temp_Max_API_Externa_C":
            round(real_max, 2)
            if real_max is not None
            else "N/A",

        "Diferenca_Media_C":
            round(diff_media, 2)
            if diff_media is not None
            else "N/A",

        "Diferenca_Min_C":
            round(diff_min, 2)
            if diff_min is not None
            else "N/A",

        "Diferenca_Max_C":
            round(diff_max, 2)
            if diff_max is not None
            else "N/A"
    }
])


# ============================================================
# 10. CRIAR OU ATUALIZAR O CSV
# ============================================================

try:

    if not os.path.exists(ARQUIVO_HISTORICO):

        nova_previsao.to_csv(
            ARQUIVO_HISTORICO,
            index=False,
            sep=";",
            encoding="utf-8-sig"
        )

        print(
            f"Arquivo de histórico criado:\n"
            f"{ARQUIVO_HISTORICO}"
        )

    else:

        nova_previsao.to_csv(
            ARQUIVO_HISTORICO,
            mode="a",
            header=False,
            index=False,
            sep=";",
            encoding="utf-8-sig"
        )

        print(
            f"Nova previsão adicionada ao histórico:\n"
            f"{ARQUIVO_HISTORICO}"
        )

except PermissionError:

    print(
        "\nERRO DE PERMISSÃO: "
        f"Feche o arquivo '{ARQUIVO_HISTORICO}' "
        "no Excel antes de rodar o script!"
    )

print("----------------------------------------")