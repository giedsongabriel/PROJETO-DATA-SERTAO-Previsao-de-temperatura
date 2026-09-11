
import argparse
import json
from datetime import timedelta, datetime, timezone

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

HOUR_COLS = [f"{h:02d}h" for h in range(24)]

SHEET_AGG = {
    "Temp. Ins. (C)": ("temp_media", "mean"),
    "Temp. Max. (C)": ("temp_maxima", "max"),
    "Temp. Min. (C)": ("temp_minima", "min"),
    "Umi. Ins. (%)": ("umidade_media", "mean"),
    "Umi. Max. (%)": ("umidade_maxima", "max"),
    "Umi. Min. (%)": ("umidade_minima", "min"),
    "Pto Orvalho Ins. (C)": ("orvalho_medio", "mean"),
    "Pto Orvalho Max. (C)": ("orvalho_maximo", "max"),
    "Pto Orvalho Min. (C)": ("orvalho_minimo", "min"),
    "Pressao Ins. (hPa)": ("pressao_media", "mean"),
    "Pressao Max. (hPa)": ("pressao_maxima", "max"),
    "Pressao Min. (hPa)": ("pressao_minima", "min"),
    "Vel. Vento (m-s)": ("vento_vel_media", "mean"),
    "Dir. Vento (m-s)": ("vento_dir_media", "mean"),
    "Raj. Vento (m-s)": ("rajada_maxima", "max"),
}

# variaveis que ganham versoes "ontem", "media 3 dias" e "media 7 dias"
BASE_FEATS_TENDENCIA = [
    "temp_media", "temp_maxima", "temp_minima",
    "umidade_media", "pressao_media", "orvalho_medio",
]

TARGETS = ["temp_media", "temp_maxima", "temp_minima"]

RF_PARAMS = dict(n_estimators=15, max_depth=8, min_samples_leaf=2, random_state=42)

NOMES_LEGIVEIS = {
    "temp_media": "Temperatura media de hoje",
    "temp_maxima": "Temperatura maxima de hoje",
    "temp_minima": "Temperatura minima de hoje",
    "umidade_media": "Umidade media de hoje",
    "umidade_maxima": "Umidade maxima de hoje",
    "umidade_minima": "Umidade minima de hoje",
    "orvalho_medio": "Ponto de orvalho medio de hoje",
    "orvalho_maximo": "Ponto de orvalho maximo de hoje",
    "orvalho_minimo": "Ponto de orvalho minimo de hoje",
    "pressao_media": "Pressao media de hoje",
    "pressao_maxima": "Pressao maxima de hoje",
    "pressao_minima": "Pressao minima de hoje",
    "vento_vel_media": "Velocidade media do vento hoje",
    "vento_dir_media": "Direcao media do vento hoje",
    "rajada_maxima": "Rajada maxima de vento hoje",
    "dia_ano_sin": "Epoca do ano (componente sazonal 1)",
    "dia_ano_cos": "Epoca do ano (componente sazonal 2)",
}
for f in BASE_FEATS_TENDENCIA:
    nome_base = NOMES_LEGIVEIS[f].replace(" de hoje", "")
    NOMES_LEGIVEIS[f"{f}_ontem"] = f"{nome_base} de ontem"
    NOMES_LEGIVEIS[f"{f}_media3d"] = f"{nome_base} - media dos ultimos 3 dias"
    NOMES_LEGIVEIS[f"{f}_media7d"] = f"{nome_base} - media dos ultimos 7 dias"


def carregar_e_imputar(caminho):
    """Le todas as abas e imputa horarios faltantes com a media historica daquele horario."""
    xl = pd.ExcelFile(caminho)
    dados = {}
    resumo_imputacao = {}
    for aba in SHEET_AGG:
        df = xl.parse(aba).sort_values("Data").reset_index(drop=True)
        faltando_antes = int(df[HOUR_COLS].isna().sum().sum())
        media_por_horario = df[HOUR_COLS].mean(skipna=True)  # media de cada Xh entre todos os dias
        for col in HOUR_COLS:
            df[col] = df[col].fillna(media_por_horario[col])
        dados[aba] = df
        if faltando_antes:
            resumo_imputacao[aba] = faltando_antes
    return dados, resumo_imputacao


def montar_tabela_diaria(dados):
    """Resume cada dia (24 colunas de hora) em 1 numero por variavel."""
    datas = dados["Temp. Ins. (C)"]["Data"]
    diario = pd.DataFrame({"Data": datas})
    for aba, (nome_feat, agg) in SHEET_AGG.items():
        df = dados[aba]
        if agg == "mean":
            diario[nome_feat] = df[HOUR_COLS].mean(axis=1)
        elif agg == "max":
            diario[nome_feat] = df[HOUR_COLS].max(axis=1)
        elif agg == "min":
            diario[nome_feat] = df[HOUR_COLS].min(axis=1)
    return diario


def adicionar_features(diario):
    """Adiciona sazonalidade (epoca do ano) e features de tendencia (ontem, media 3d, media 7d)."""
    d = diario.copy()
    dia_do_ano = d["Data"].dt.dayofyear
    d["dia_ano_sin"] = np.sin(2 * np.pi * dia_do_ano / 365.25)
    d["dia_ano_cos"] = np.cos(2 * np.pi * dia_do_ano / 365.25)

    for f in BASE_FEATS_TENDENCIA:
        d[f"{f}_ontem"] = d[f].shift(1)
        d[f"{f}_media3d"] = d[f].rolling(3).mean()
        d[f"{f}_media7d"] = d[f].rolling(7).mean()

    return d


def validar_time_series(d, feature_cols, target_col, n_splits=6, min_treino=60):
    """Validacao cruzada respeitando a ordem do tempo (nunca treina com o futuro)."""
    d = d.dropna(subset=feature_cols + [target_col]).reset_index(drop=True)
    n = len(d)
    tamanho_fold = max((n - min_treino) // n_splits, 1)
    maes = []
    for i in range(n_splits):
        fim_treino = min_treino + i * tamanho_fold
        fim_teste = min(fim_treino + tamanho_fold, n)
        if fim_teste <= fim_treino or fim_treino >= n:
            continue
        X_treino = d.loc[:fim_treino - 1, feature_cols]
        y_treino = d.loc[:fim_treino - 1, target_col]
        X_teste = d.loc[fim_treino:fim_teste - 1, feature_cols]
        y_teste = d.loc[fim_treino:fim_teste - 1, target_col]
        if len(X_teste) == 0:
            continue
        modelo = RandomForestRegressor(**RF_PARAMS)
        modelo.fit(X_treino, y_treino)
        pred = modelo.predict(X_teste)
        maes.append(mean_absolute_error(y_teste, pred))
    return float(np.mean(maes)) if maes else None


def treinar_e_prever(diario_com_features):
    """Treina 1 Random Forest por alvo e preve o dia seguinte a partir da ultima linha (hoje)."""
    feature_cols = [c for c in diario_com_features.columns if c != "Data"]

    hoje = diario_com_features.iloc[[-1]].copy()  # ultima linha = hoje (ja imputada)
    data_hoje = hoje["Data"].iloc[0]
    data_amanha = data_hoje + timedelta(days=1)

    resultado = {}
    for alvo in TARGETS:
        d = diario_com_features.copy()
        d[f"y_{alvo}"] = d[alvo].shift(-1)  # y = valor do dia seguinte

        # linhas utilizaveis para treino: tem features completas e y valido
        treino = d.dropna(subset=feature_cols + [f"y_{alvo}"]).reset_index(drop=True)

        mae_validacao = validar_time_series(d, feature_cols, f"y_{alvo}")

        X = treino[feature_cols]
        y = treino[f"y_{alvo}"]
        modelo = RandomForestRegressor(**RF_PARAMS)
        modelo.fit(X, y)

        pred_amanha = float(modelo.predict(hoje[feature_cols])[0])

        importancias = pd.Series(modelo.feature_importances_, index=feature_cols)
        top5 = importancias.sort_values(ascending=False).head(5)
        top5_legivel = {
            NOMES_LEGIVEIS.get(feat, feat): round(float(val), 4)
            for feat, val in top5.items()
        }

        resultado[alvo] = {
            "previsao": round(pred_amanha, 1),
            "erro_medio_esperado_mae": round(mae_validacao, 2) if mae_validacao is not None else None,
            "dias_usados_no_treino": int(len(treino)),
            "importancia_variaveis": top5_legivel,
        }

    return data_amanha, resultado, hoje


def main():
    parser = argparse.ArgumentParser(description="Preve temperatura de amanha com Random Forest.")
    parser.add_argument("--input", default="site/dados_coletados.xlsx", help="Caminho da planilha de entrada")
    parser.add_argument("--output", default="site/previsao.json", help="Caminho do JSON de saida")
    args = parser.parse_args()

    dados, resumo_imputacao = carregar_e_imputar(args.input)
    diario = montar_tabela_diaria(dados)
    diario_features = adicionar_features(diario)

    data_amanha, resultado, hoje = treinar_e_prever(diario_features)

    saida = {
        "gerado_em": datetime.now(timezone.utc).isoformat(),
        "data_referencia_hoje": hoje["Data"].iloc[0].strftime("%Y-%m-%d"),
        "data_previsao": data_amanha.strftime("%Y-%m-%d"),
        "horarios_imputados_hoje": {
            aba: int(qtd) for aba, qtd in resumo_imputacao.items()
        },
        "previsao": {
            "temperatura_media": resultado["temp_media"]["previsao"],
            "temperatura_maxima": resultado["temp_maxima"]["previsao"],
            "temperatura_minima": resultado["temp_minima"]["previsao"],
        },
        "detalhes_modelo": {
            "algoritmo": "Random Forest Regressor (scikit-learn)",
            "parametros": RF_PARAMS,
            "temp_media": resultado["temp_media"],
            "temp_maxima": resultado["temp_maxima"],
            "temp_minima": resultado["temp_minima"],
        },
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"Previsao para {data_amanha.strftime('%d/%m/%Y')} salva em {args.output}")
    print(json.dumps(saida["previsao"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()