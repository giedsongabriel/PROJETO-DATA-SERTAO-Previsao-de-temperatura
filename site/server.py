from flask import Flask, jsonify, send_from_directory, request

import pandas as pd

import os
import sys
import subprocess

from datetime import datetime
from bs4 import BeautifulSoup
import re
import requests


# ==========================================
# CONFIGURAÇÃO
# ==========================================

app = Flask(__name__)

PASTA_SITE = os.path.dirname(
    os.path.abspath(__file__)
)

ARQUIVO = os.path.join(
    PASTA_SITE,
    "dados_coletados.xlsx"
)

PASTA_PREVISAO = os.path.abspath(
    os.path.join(
        PASTA_SITE,
        "..",
        "previsao"
    )
)

SCRIPT_PREVISAO = os.path.join(
    PASTA_PREVISAO,
    "previsao_imputado.py"
)

ARQUIVO_PREVISAO = os.path.join(
    PASTA_SITE,
    "historico_previsoes2.csv"
)


# ==========================================
# PÁGINA PRINCIPAL
# ==========================================

@app.route("/")
def index():

    return send_from_directory(
        PASTA_SITE,
        "index.html"
    )


# ==========================================
# ARQUIVOS DO SITE
# ==========================================

@app.route("/style.css")
def style():

    return send_from_directory(
        PASTA_SITE,
        "style.css"
    )


@app.route("/script.js")
def script():

    return send_from_directory(
        PASTA_SITE,
        "script.js"
    )


@app.route("/animations.js")
def animations():

    return send_from_directory(
        PASTA_SITE,
        "animations.js"
    )


# ==========================================
# IMAGENS E OUTROS ARQUIVOS
# ==========================================

@app.route("/<path:nome_arquivo>")
def arquivo_site(nome_arquivo):

    return send_from_directory(
        PASTA_SITE,
        nome_arquivo
    )


# ==========================================
# CONVERTER VALOR
# ==========================================

def converter_valor(valor):

    if valor is None:
        return None

    try:

        if pd.isna(valor):
            return None

    except (TypeError, ValueError):
        pass

    if isinstance(valor, str):

        valor = valor.strip()

        if valor.lower() in (
            "",
            "null",
            "none",
            "n/a",
            "na",
            "nan",
            "nat"
        ):
            return None

        valor = valor.replace(",", ".")

    try:

        numero = float(valor)

    except (
        ValueError,
        TypeError
    ):

        return None

    if pd.isna(numero):
        return None

    # 9999 é utilizado pelo INMET
    # para representar valores inválidos.
    if numero == 9999:
        return None

    return numero


# ==========================================
# CONVERTER DATA
# ==========================================

def converter_data(valor):

    if valor is None:
        return None

    try:

        data = pd.to_datetime(
            valor,
            dayfirst=True,
            errors="coerce"
        )

        if pd.isna(data):
            return None

        return data

    except Exception:

        return None


# ==========================================
# PEGAR ÚLTIMO VALOR DISPONÍVEL
# ==========================================

def pegar_valor_dataframe(df):

    if "Data" not in df.columns:
        return None

    df = df.copy()

    df["Data"] = pd.to_datetime(
        df["Data"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(
        subset=["Data"]
    )

    if df.empty:
        return None

    # ==========================================
    # PROCURAR O DIA MAIS RECENTE
    # ==========================================

    data_mais_recente = df["Data"].max()

    dados_recentes = df[
        df["Data"] == data_mais_recente
    ]

    if dados_recentes.empty:
        return None

    linha = dados_recentes.iloc[0]

    # ==========================================
    # PROCURAR A ÚLTIMA HORA DISPONÍVEL
    # ==========================================

    for hora in range(23, -1, -1):

        coluna_hora = f"{hora:02d}h"

        if coluna_hora not in df.columns:
            continue

        valor = converter_valor(
            linha[coluna_hora]
        )

        if valor is None:
            continue

        return valor

    return None


# ==========================================
# LER DADOS ATUAIS DA ESTAÇÃO
# ==========================================

def ler_dados_estacao():

    if not os.path.exists(ARQUIVO):
        return None

    arquivo_excel = None

    abas = {

        "temperatura":
            "Temp. Ins. (C)",

        "umidade":
            "Umi. Ins. (%)",

        "pressao":
            "Pressao Ins. (hPa)",

        "vento":
            "Vel. Vento (m-s)",

        "ponto_orvalho":
            "Pto Orvalho Ins. (C)",

        "direcao_vento":
            "Dir. Vento (m-s)",

        "rajada_vento":
            "Raj. Vento (m-s)"
    }

    dados = {}

    try:

        arquivo_excel = pd.ExcelFile(
            ARQUIVO
        )

        for nome, aba in abas.items():

            try:

                if aba not in arquivo_excel.sheet_names:

                    dados[nome] = None

                    continue

                df = pd.read_excel(
                    arquivo_excel,
                    sheet_name=aba
                )

                dados[nome] = pegar_valor_dataframe(
                    df
                )

            except Exception as erro:

                print(
                    f"Erro ao ler aba {aba}: {erro}"
                )

                dados[nome] = None

    except Exception as erro:

        print(
            f"Erro ao abrir planilha: {erro}"
        )

        return None

    finally:

        if arquivo_excel is not None:

            arquivo_excel.close()

    return dados


# ==========================================
# API - DADOS ATUAIS
# ==========================================

@app.route("/api/dados")
def dados():

    if not os.path.exists(ARQUIVO):

        return jsonify({

            "erro":
                "dados_coletados.xlsx não encontrado.",

            "caminho":
                ARQUIVO

        }), 404

    try:

        dados_estacao = ler_dados_estacao()

        if dados_estacao is None:

            return jsonify({

                "erro":
                    "Não foi possível ler a planilha."

            }), 500

        data_atualizacao = datetime.fromtimestamp(
            os.path.getmtime(ARQUIVO)
        )

        ultima_atualizacao = (
            data_atualizacao.strftime(
                "%d/%m/%Y às %H:%M"
            )
        )

        resultado = {

            "temperatura":
                dados_estacao.get(
                    "temperatura"
                ),

            "umidade":
                dados_estacao.get(
                    "umidade"
                ),

            "pressao":
                dados_estacao.get(
                    "pressao"
                ),

            "vento":
                dados_estacao.get(
                    "vento"
                ),

            "ponto_orvalho":
                dados_estacao.get(
                    "ponto_orvalho"
                ),

            "direcao_vento":
                dados_estacao.get(
                    "direcao_vento"
                ),

            "rajada_vento":
                dados_estacao.get(
                    "rajada_vento"
                ),

            "ultima_atualizacao":
                ultima_atualizacao
        }

        return jsonify(
            resultado
        )

    except Exception as erro:

        print(
            f"Erro ao ler dados: {erro}"
        )

        return jsonify({

            "erro":
                str(erro)

        }), 500


# ==========================================
# LER HISTÓRICO DE PREVISÕES
# ==========================================

def ler_historico_previsoes():

    if not os.path.exists(
        ARQUIVO_PREVISAO
    ):
        return None

    try:

        df = pd.read_csv(
            ARQUIVO_PREVISAO,
            sep=";",
            encoding="utf-8"
        )

        if df.empty:
            return None

        # ==========================================
        # LIMPAR NOMES DAS COLUNAS
        # ==========================================

        df.columns = [
            str(coluna).strip()
            for coluna in df.columns
        ]

        # ==========================================
        # CONVERTER DATAS
        # ==========================================

        if "Data_Execucao" in df.columns:

            df["Data_Execucao_Convertida"] = pd.to_datetime(
                df["Data_Execucao"],
                errors="coerce"
            )

        if "Data_Prevista" in df.columns:

            df["Data_Prevista_Convertida"] = pd.to_datetime(
                df["Data_Prevista"],
                errors="coerce"
            )

        return df

    except UnicodeDecodeError:

        try:

            df = pd.read_csv(
                ARQUIVO_PREVISAO,
                sep=";",
                encoding="latin1"
            )

            if df.empty:
                return None

            df.columns = [
                str(coluna).strip()
                for coluna in df.columns
            ]

            if "Data_Execucao" in df.columns:

                df["Data_Execucao_Convertida"] = pd.to_datetime(
                    df["Data_Execucao"],
                    errors="coerce"
                )

            if "Data_Prevista" in df.columns:

                df["Data_Prevista_Convertida"] = pd.to_datetime(
                    df["Data_Prevista"],
                    errors="coerce"
                )

            return df

        except Exception as erro:

            print(
                f"Erro ao ler histórico de previsões: {erro}"
            )

            return None

    except Exception as erro:

        print(
            f"Erro ao ler histórico de previsões: {erro}"
        )

        return None


# ==========================================
# API - PREVISÃO ATUAL
# ==========================================

@app.route("/api/previsao")
def previsao():

    if not os.path.exists(
        ARQUIVO_PREVISAO
    ):

        return jsonify({

            "erro":
                "historico_previsoes2.csv não encontrado.",

            "caminho":
                ARQUIVO_PREVISAO

        }), 404

    try:

        df = ler_historico_previsoes()

        if df is None or df.empty:

            return jsonify({

                "erro":
                    "O histórico de previsões está vazio."

            }), 404

        # ==========================================
        # GARANTIR QUE A ÚLTIMA PREVISÃO SEJA A
        # MAIS RECENTE PELA DATA DE EXECUÇÃO
        # ==========================================

        if "Data_Execucao_Convertida" in df.columns:

            df_validado = df.dropna(
                subset=[
                    "Data_Execucao_Convertida"
                ]
            )

            if not df_validado.empty:

                ultima = df_validado.sort_values(
                    "Data_Execucao_Convertida"
                ).iloc[-1]

            else:

                ultima = df.iloc[-1]

        else:

            ultima = df.iloc[-1]

        # ==========================================
        # RESULTADO
        # ==========================================

        resultado = {

            "data_execucao":
                str(
                    ultima.get(
                        "Data_Execucao",
                        ""
                    )
                ),

            "data_ultima_leitura":
                str(
                    ultima.get(
                        "Data_Ultima_Leitura",
                        ""
                    )
                ),

            "data_prevista":
                str(
                    ultima.get(
                        "Data_Prevista",
                        ""
                    )
                ),

            # ==========================================
            # PREVISÃO DO MODELO
            # ==========================================

            "previsao": {

                "temperatura_media":
                    converter_valor(
                        ultima.get(
                            "Temp_Media_Prevista_C"
                        )
                    ),

                "temperatura_minima":
                    converter_valor(
                        ultima.get(
                            "Temp_Min_Prevista_C"
                        )
                    ),

                "temperatura_maxima":
                    converter_valor(
                        ultima.get(
                            "Temp_Max_Prevista_C"
                        )
                    )
            },

            # ==========================================
            # REFERÊNCIA EXTERNA
            # ==========================================

            "real": {

                "temperatura_media":
                    converter_valor(
                        ultima.get(
                            "Temp_Media_API_Externa_C"
                        )
                    ),

                "temperatura_minima":
                    converter_valor(
                        ultima.get(
                            "Temp_Min_API_Externa_C"
                        )
                    ),

                "temperatura_maxima":
                    converter_valor(
                        ultima.get(
                            "Temp_Max_API_Externa_C"
                        )
                    )
            },

            # ==========================================
            # DIFERENÇAS
            # ==========================================

            "diferenca": {

                "media":
                    converter_valor(
                        ultima.get(
                            "Diferenca_Media_C"
                        )
                    ),

                "minima":
                    converter_valor(
                        ultima.get(
                            "Diferenca_Min_C"
                        )
                    ),

                "maxima":
                    converter_valor(
                        ultima.get(
                            "Diferenca_Max_C"
                        )
                    )
            }
        }

        return jsonify(
            resultado
        )

    except Exception as erro:

        print(
            f"Erro ao ler previsão: {erro}"
        )

        return jsonify({

            "erro":
                str(erro)

        }), 500


# ==========================================
# API - HISTÓRICO DE PREVISÕES
# ==========================================

@app.route("/api/historico-previsoes")
def historico_previsoes():

    try:

        df = ler_historico_previsoes()

        if df is None or df.empty:

            return jsonify({
                "dados": []
            })

        # ==========================================
        # FILTRO DE PERÍODO
        # ==========================================

        periodo = request.args.get(
            "periodo",
            "todos"
        )

        if (
            "Data_Prevista_Convertida"
            in df.columns
        ):

            df = df.dropna(
                subset=[
                    "Data_Prevista_Convertida"
                ]
            )

            if periodo != "todos":

                try:

                    dias = int(periodo)

                    if dias > 0:

                        data_mais_recente = (
                            df[
                                "Data_Prevista_Convertida"
                            ].max()
                        )

                        data_limite = (
                            data_mais_recente
                            -
                            pd.Timedelta(
                                days=dias
                            )
                        )

                        df = df[
                            df[
                                "Data_Prevista_Convertida"
                            ] >= data_limite
                        ]

                except (
                    ValueError,
                    TypeError
                ):

                    pass

            # ==========================================
            # MAIS RECENTE PRIMEIRO
            # ==========================================

            df = df.sort_values(
                "Data_Prevista_Convertida",
                ascending=False
            )

        registros = []

        # ==========================================
        # TRANSFORMAR LINHAS EM JSON
        # ==========================================

        for _, linha in df.iterrows():

            registros.append({

                "data_execucao":
                    str(
                        linha.get(
                            "Data_Execucao",
                            ""
                        )
                    ),

                "data_ultima_leitura":
                    str(
                        linha.get(
                            "Data_Ultima_Leitura",
                            ""
                        )
                    ),

                "data_prevista":
                    str(
                        linha.get(
                            "Data_Prevista",
                            ""
                        )
                    ),

                "previsao": {

                    "media":
                        converter_valor(
                            linha.get(
                                "Temp_Media_Prevista_C"
                            )
                        ),

                    "minima":
                        converter_valor(
                            linha.get(
                                "Temp_Min_Prevista_C"
                            )
                        ),

                    "maxima":
                        converter_valor(
                            linha.get(
                                "Temp_Max_Prevista_C"
                            )
                        )
                },

                "real": {

                    "media":
                        converter_valor(
                            linha.get(
                                "Temp_Media_API_Externa_C"
                            )
                        ),

                    "minima":
                        converter_valor(
                            linha.get(
                                "Temp_Min_API_Externa_C"
                            )
                        ),

                    "maxima":
                        converter_valor(
                            linha.get(
                                "Temp_Max_API_Externa_C"
                            )
                        )
                },

                "diferenca": {

                    "media":
                        converter_valor(
                            linha.get(
                                "Diferenca_Media_C"
                            )
                        ),

                    "minima":
                        converter_valor(
                            linha.get(
                                "Diferenca_Min_C"
                            )
                        ),

                    "maxima":
                        converter_valor(
                            linha.get(
                                "Diferenca_Max_C"
                            )
                        )
                }
            })

        return jsonify({

            "dados":
                registros

        })

    except Exception as erro:

        print(
            f"Erro no histórico de previsões: {erro}"
        )

        return jsonify({

            "erro":
                str(erro)

        }), 500


# ==========================================
# EXECUTAR NOVA COLETA + PREVISÃO
# ==========================================

@app.route(
    "/api/atualizar",
    methods=["POST"]
)
def atualizar():

    try:

        # ==========================================
        # CAMINHO DO SCRIPT DE COLETA
        # ==========================================

        script_coleta = os.path.abspath(
            os.path.join(
                PASTA_SITE,
                "..",
                "coleta de dados",
                "coleta_cabrobo.py"
            )
        )

        # ==========================================
        # VERIFICAR SCRIPT DE COLETA
        # ==========================================

        if not os.path.exists(
            script_coleta
        ):

            return jsonify({

                "sucesso": False,

                "etapa": "coleta",

                "erro":
                    "coleta_cabrobo.py não encontrado.",

                "caminho":
                    script_coleta

            }), 500

        # ==========================================
        # VERIFICAR SCRIPT DE PREVISÃO
        # ==========================================

        if not os.path.exists(
            SCRIPT_PREVISAO
        ):

            return jsonify({

                "sucesso": False,

                "etapa": "previsao",

                "erro":
                    "previsao_imputado.py não encontrado.",

                "caminho":
                    SCRIPT_PREVISAO

            }), 500

        # ==========================================
        # MODIFICAÇÃO ANTERIOR DA PLANILHA
        # ==========================================

        if os.path.exists(ARQUIVO):

            modificacao_anterior = (
                os.path.getmtime(
                    ARQUIVO
                )
            )

        else:

            modificacao_anterior = 0

        # ==========================================
        # INICIAR COLETA
        # ==========================================

        print()
        print(
            "=========================================="
        )
        print(
            " INICIANDO NOVA COLETA"
        )
        print(
            "=========================================="
        )
        print()

        resultado = subprocess.run(

            [
                sys.executable,
                script_coleta
            ],

            capture_output=True,
            text=True,

            cwd=os.path.dirname(
                script_coleta
            ),

            encoding="utf-8",
            errors="replace"
        )

        # ==========================================
        # SAÍDA DA COLETA
        # ==========================================

        print(
            "----- SAÍDA DA COLETA -----"
        )

        if resultado.stdout:

            print(
                resultado.stdout
            )

        if resultado.stderr:

            print(
                "----- ERROS DA COLETA -----"
            )

            print(
                resultado.stderr
            )

        print(
            "----------------------------"
        )

        # ==========================================
        # VERIFICAR COLETA
        # ==========================================

        if resultado.returncode != 0:

            return jsonify({

                "sucesso": False,

                "etapa": "coleta",

                "erro":
                    "A coleta terminou com erro.",

                "detalhes": (
                    resultado.stderr
                    or
                    resultado.stdout
                    or
                    "Nenhuma mensagem de erro foi retornada."
                )

            }), 500

        # ==========================================
        # VERIFICAR PLANILHA
        # ==========================================

        if not os.path.exists(
            ARQUIVO
        ):

            return jsonify({

                "sucesso": False,

                "etapa": "coleta",

                "erro":
                    "A coleta terminou, mas a planilha não foi encontrada.",

                "caminho":
                    ARQUIVO

            }), 500

        # ==========================================
        # VERIFICAR SE A PLANILHA FOI ATUALIZADA
        # ==========================================

        modificacao_nova = os.path.getmtime(
            ARQUIVO
        )

        if (
            modificacao_anterior != 0
            and
            modificacao_nova <= modificacao_anterior
        ):

            return jsonify({

                "sucesso": False,

                "etapa": "coleta",

                "erro":
                    "A coleta terminou, mas a planilha não foi atualizada."

            }), 500

        # ==========================================
        # COLETA CONCLUÍDA
        # ==========================================

        print()
        print(
            "COLETA CONCLUÍDA COM SUCESSO"
        )
        print()

        # ==========================================
        # EXECUTAR MODELO DE PREVISÃO
        # ==========================================

        print(
            "=========================================="
        )
        print(
            " EXECUTANDO MODELO DE PREVISÃO"
        )
        print(
            "=========================================="
        )
        print()

        resultado_previsao = subprocess.run(

            [
                sys.executable,
                SCRIPT_PREVISAO
            ],

            capture_output=True,
            text=True,

            cwd=os.path.dirname(
                SCRIPT_PREVISAO
            ),

            encoding="utf-8",
            errors="replace"
        )

        # ==========================================
        # SAÍDA DO MODELO
        # ==========================================

        print(
            "----- SAÍDA DO MODELO -----"
        )

        if resultado_previsao.stdout:

            print(
                resultado_previsao.stdout
            )

        if resultado_previsao.stderr:

            print(
                "----- ERROS DO MODELO -----"
            )

            print(
                resultado_previsao.stderr
            )

        print(
            "----------------------------"
        )

        # ==========================================
        # VERIFICAR MODELO
        # ==========================================

        if resultado_previsao.returncode != 0:

            return jsonify({

                "sucesso": False,

                "etapa": "previsao",

                "erro":
                    "A planilha foi atualizada, mas o modelo de previsão apresentou um erro.",

                "detalhes": (

                    resultado_previsao.stderr
                    or
                    resultado_previsao.stdout
                    or
                    "Nenhuma mensagem de erro foi retornada."
                )

            }), 500

        # ==========================================
        # VERIFICAR HISTÓRICO
        # ==========================================

        if not os.path.exists(
            ARQUIVO_PREVISAO
        ):

            return jsonify({

                "sucesso": False,

                "etapa": "previsao",

                "erro":
                    "O modelo terminou, mas historico_previsoes2.csv não foi encontrado.",

                "caminho":
                    ARQUIVO_PREVISAO

            }), 500

        # ==========================================
        # SUCESSO
        # ==========================================

        print()
        print(
            "=========================================="
        )
        print(
            " ATUALIZAÇÃO CONCLUÍDA COM SUCESSO"
        )
        print(
            "=========================================="
        )
        print()

        return jsonify({

            "sucesso": True,

            "mensagem":
                "Dados e previsão atualizados com sucesso."

        })

    except Exception as erro:

        print()
        print(
            "=========================================="
        )
        print(
            " ERRO AO EXECUTAR ATUALIZAÇÃO"
        )
        print(
            "=========================================="
        )
        print()

        import traceback

        traceback.print_exc()

        return jsonify({

            "sucesso": False,

            "etapa": "servidor",

            "erro":
                str(erro)

        }), 500


# ==========================================
# DADOS DO GRÁFICO
# ==========================================

@app.route("/api/grafico")
def grafico():

    metrica = request.args.get(
        "metrica",
        "temperatura"
    )

    # ==========================================
    # RELAÇÃO MÉTRICA → ABA
    # ==========================================

    abas = {

        "temperatura":
            "Temp. Ins. (C)",

        "umidade":
            "Umi. Ins. (%)",

        "pressao":
            "Pressao Ins. (hPa)",

        "vento":
            "Vel. Vento (m-s)"
    }

    # ==========================================
    # VALIDAR MÉTRICA
    # ==========================================

    if metrica not in abas:

        return jsonify({

            "erro":
                "Métrica inválida."

        }), 400

    # ==========================================
    # VERIFICAR PLANILHA
    # ==========================================

    if not os.path.exists(
        ARQUIVO
    ):

        return jsonify({

            "erro":
                "Planilha não encontrada."

        }), 404

    try:

        df = pd.read_excel(

            ARQUIVO,

            sheet_name=abas[
                metrica
            ]
        )

        if "Data" not in df.columns:

            return jsonify({

                "erro":
                    "A aba não possui a coluna Data."

            }), 500

        # ==========================================
        # DATA
        # ==========================================

        df["Data"] = pd.to_datetime(

            df["Data"],

            dayfirst=True,

            errors="coerce"
        )

        df = df.dropna(
            subset=["Data"]
        )

        registros = []

        # ==========================================
        # TRANSFORMAR HORAS
        # ==========================================

        for _, linha in df.iterrows():

            data = linha["Data"]

            for hora in range(24):

                coluna = f"{hora:02d}h"

                if coluna not in df.columns:
                    continue

                valor = converter_valor(
                    linha[coluna]
                )

                if valor is None:
                    continue

                data_hora = (
                    data
                    +
                    pd.Timedelta(
                        hours=hora
                    )
                )

                registros.append({

                    "data":
                        data_hora,

                    "valor":
                        valor
                })

        if not registros:

            return jsonify({

                "labels": [],

                "valores": []

            })

        # ==========================================
        # DATAFRAME DOS REGISTROS
        # ==========================================

        registros_df = pd.DataFrame(
            registros
        )

        registros_df = (
            registros_df
            .sort_values("data")
        )

        # ==========================================
        # REMOVER DADOS FUTUROS
        # ==========================================

        agora = pd.Timestamp.now()

        registros_df = registros_df[
            registros_df["data"] <= agora
        ]

        # ==========================================
        # ÚLTIMAS 24 HORAS
        # ==========================================

        registros_df = registros_df.tail(
            24
        )

        # ==========================================
        # RESPOSTA
        # ==========================================

        return jsonify({

            "labels": [

                registro.strftime(
                    "%H:%M"
                )

                for registro
                in registros_df["data"]
            ],

            "valores": [

                float(valor)

                for valor
                in registros_df["valor"]
            ]

        })

    except Exception as erro:

        print(
            f"Erro ao gerar gráfico: {erro}"
        )

        return jsonify({

            "erro":
                str(erro)

        }), 500


# ==========================================
# HISTÓRICO METEOROLÓGICO
# ==========================================

# ==========================================
# HISTÓRICO METEOROLÓGICO
# ==========================================

@app.route("/api/historico")
def historico():

    periodo = request.args.get(
        "periodo",
        "30"
    )

    # ==========================================
    # VERIFICAR PLANILHA
    # ==========================================

    if not os.path.exists(ARQUIVO):

        return jsonify({
            "erro": "Planilha não encontrada."
        }), 404

    try:

        # ==========================================
        # CARREGAR TEMPERATURA
        # ==========================================

        df = pd.read_excel(
            ARQUIVO,
            sheet_name="Temp. Ins. (C)"
        )

        if "Data" not in df.columns:

            return jsonify({
                "erro": "A aba não possui a coluna Data."
            }), 500

        # ==========================================
        # CONVERTER DATA
        # ==========================================

        df["Data"] = pd.to_datetime(
            df["Data"],
            dayfirst=True,
            errors="coerce"
        )

        df = df.dropna(
            subset=["Data"]
        )

        registros = []

        # ==========================================
        # TRANSFORMAR DADOS HORÁRIOS
        # ==========================================

        for _, linha in df.iterrows():

            data = linha["Data"]

            for hora in range(24):

                coluna = f"{hora:02d}h"

                if coluna not in df.columns:
                    continue

                valor = converter_valor(
                    linha[coluna]
                )

                if valor is None:
                    continue

                registros.append({
                    "data": data + pd.Timedelta(
                        hours=hora
                    ),
                    "valor": valor
                })

        # ==========================================
        # VERIFICAR DADOS
        # ==========================================

        if not registros:

            return jsonify({
                "metrica": "Temperatura",
                "unidade": "°C",
                "dados": []
            })

        historico_df = pd.DataFrame(
            registros
        )

        # ==========================================
        # DATA DO DIA
        # ==========================================

        historico_df["data_dia"] = (
            historico_df["data"].dt.date
        )

        # ==========================================
        # FILTRAR PERÍODO
        # ==========================================

        if periodo != "todos":

            try:

                dias = int(periodo)

                if dias > 0:

                    data_mais_recente = (
                        historico_df["data_dia"].max()
                    )

                    data_limite = (
                        pd.Timestamp(
                            data_mais_recente
                        )
                        -
                        pd.Timedelta(
                            days=dias - 1
                        )
                    ).date()

                    historico_df = (
                        historico_df[
                            historico_df["data_dia"]
                            >=
                            data_limite
                        ]
                    )

            except (
                ValueError,
                TypeError
            ):

                pass

        # ==========================================
        # AGRUPAR POR DIA
        # ==========================================

        historico_diario = (
            historico_df
            .groupby("data_dia")["valor"]
            .agg(
                minima="min",
                media="mean",
                maxima="max"
            )
            .reset_index()
        )

        # ==========================================
        # ORDENAR
        # ==========================================

        historico_diario = (
            historico_diario
            .sort_values(
                "data_dia",
                ascending=True
            )
        )

        # ==========================================
        # MONTAR RESPOSTA
        # ==========================================

        dados = []

        for _, linha in historico_diario.iterrows():

            dados.append({

                "data":
                    linha["data_dia"].strftime(
                        "%d/%m/%Y"
                    ),

                "minima":
                    round(
                        float(
                            linha["minima"]
                        ),
                        2
                    ),

                "media":
                    round(
                        float(
                            linha["media"]
                        ),
                        2
                    ),

                "maxima":
                    round(
                        float(
                            linha["maxima"]
                        ),
                        2
                    ),

                "unidade":
                    "°C"
            })

        # ==========================================
        # MAIS RECENTE PRIMEIRO
        # ==========================================

        dados.reverse()

        return jsonify({

            "metrica":
                "Temperatura",

            "unidade":
                "°C",

            "dados":
                dados
        })

    except Exception as erro:

        print(
            f"Erro ao gerar histórico: {erro}"
        )

        return jsonify({

            "erro":
                str(erro)

        }), 500
@app.route("/api/climatempo")
def api_climatempo():

    url = "https://www.climatempo.com.br/previsao-do-tempo/amanha/cidade/1249/cabrobo-pe"

    try:
        resposta = requests.get(
            url,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/140.0 Safari/537.36"
                )
            },
            timeout=15
        )

        resposta.raise_for_status()

        soup = BeautifulSoup(resposta.text, "html.parser")

        # Procurar a seção de previsão de AMANHÃ
        texto = soup.get_text(" ", strip=True)

        # A página possui os valores de temperatura na previsão:
        # primeiro valor = mínima (azul)
        # segundo valor = máxima (vermelho)

        temperaturas = re.findall(r'(\d{1,2})\s*°', texto)

        if len(temperaturas) < 2:
            return jsonify({
                "sucesso": False,
                "erro": "Não foi possível localizar as temperaturas da Climatempo."
            }), 502

        minima = float(temperaturas[0])
        maxima = float(temperaturas[1])

        return jsonify({
            "sucesso": True,
            "fonte": "Climatempo",
            "data": "amanha",
            "minima": minima,
            "maxima": maxima
        })

    except requests.RequestException as erro:
        return jsonify({
            "sucesso": False,
            "erro": f"Erro ao acessar a Climatempo: {erro}"
        }), 502

    except Exception as erro:
        print(f"Erro na API Climatempo: {erro}")

        return jsonify({
            "sucesso": False,
            "erro": str(erro)
        }), 500
# ==========================================
# INICIAR SERVIDOR
# ==========================================

if __name__ == "__main__":

    print()

    print(
        "=========================================="
    )

    print(
        " SISTEMA DE PREVISÃO METEOROLÓGICA"
    )

    print(
        "=========================================="
    )

    print()

    print(
        "Arquivo:",
        ARQUIVO
    )

    print(
        "Histórico de previsões:",
        ARQUIVO_PREVISAO
    )

    print(
        "Script de previsão:",
        SCRIPT_PREVISAO
    )

    print()

    print(
        "Servidor iniciado!"
    )

    print()

    print(
        "http://127.0.0.1:5000"
    )

    print()

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True,

        use_reloader=False
    )