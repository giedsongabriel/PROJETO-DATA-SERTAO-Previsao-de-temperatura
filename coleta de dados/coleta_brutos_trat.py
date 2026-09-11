from playwright.sync_api import sync_playwright
from datetime import date
import pandas as pd
import os


with sync_playwright() as p:

    # ==========================================
    # ABRIR INMET
    # ==========================================

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Abrindo INMET...")

    page.goto(
        "https://tempo.inmet.gov.br/",
        wait_until="domcontentloaded"
    )

    # ==========================================
    # PRODUTO
    # ==========================================

    page.get_by_text(
        "Selecione",
        exact=True
    ).wait_for(
        state="visible",
        timeout=30000
    )

    page.get_by_text(
        "Selecione",
        exact=True
    ).click()

    page.get_by_text(
        "Tabela de Dados das Estações",
        exact=True
    ).click()

    # ==========================================
    # CAMPOS
    # ==========================================

    inputs = page.locator("input.search")

    inputs.nth(1).wait_for(
        state="visible",
        timeout=30000
    )

    # ==========================================
    # ESTADO
    # ==========================================

    print("Selecionando Pernambuco...")

    estado = inputs.nth(1)
    estado.click()

    page.wait_for_timeout(300)

    page.get_by_text(
        "Pernambuco",
        exact=True
    ).click()

    # ==========================================
    # ESTAÇÃO
    # ==========================================

    print("Selecionando Cabrobó...")

    estacao = inputs.nth(2)
    estacao.click()

    page.wait_for_timeout(300)

    page.get_by_text(
        "CABROBO (A329)",
        exact=True
    ).click()

    # ==========================================
    # DATAS DA COLETA
    # ==========================================

    data_inicio = pd.Timestamp("2026-03-01")
    data_fim = pd.Timestamp(date.today())

    datas = page.locator('input[type="date"]')

    datas.nth(0).fill(
        data_inicio.strftime("%Y-%m-%d")
    )

    datas.nth(1).fill(
        data_fim.strftime("%Y-%m-%d")
    )

    print(
        f"Período da coleta: "
        f"{data_inicio.strftime('%d/%m/%Y')} até "
        f"{data_fim.strftime('%d/%m/%Y')}"
    )

    # ==========================================
    # GERAR TABELA
    # ==========================================

    print("Gerando tabela...")

    botao_gerar = page.get_by_text(
        "Gerar Tabela",
        exact=True
    )

    botao_gerar.wait_for(
        state="visible",
        timeout=30000
    )

    botao_gerar.click()

    # Espera a tabela aparecer
    tabela = page.locator("table").first

    tabela.wait_for(
        state="visible",
        timeout=60000
    )

    print("Tabela gerada!")

    # ==========================================
    # LER TABELA
    # ==========================================

    print("Lendo dados da tabela...")

    dados = tabela.locator(
        "tbody tr"
    ).evaluate_all("""
        rows => rows.map(row =>
            Array.from(row.querySelectorAll("td"))
                .map(cell => cell.innerText.trim())
        )
    """)

    print("Dados coletados.")

    # ==========================================
    # CRIAR DATAFRAME
    # ==========================================

    df = pd.DataFrame(dados)

    # ==========================================
    # NOMEAR COLUNAS
    # ==========================================

    df.columns = [
        "Data",
        "Hora",
        "Temperatura_Inst",
        "Temperatura_Max",
        "Temperatura_Min",
        "Umidade_Inst",
        "Umidade_Max",
        "Umidade_Min",
        "Ponto_Orvalho_Inst",
        "Ponto_Orvalho_Max",
        "Ponto_Orvalho_Min",
        "Pressao_Inst",
        "Pressao_Max",
        "Pressao_Min",
        "Vento_Velocidade",
        "Vento_Direcao",
        "Vento_Rajada",
        "Radiacao",
        "Chuva"
    ]

    print(f"Registros coletados: {len(df)}")

    # ==========================================
    # CORREÇÃO DO HORÁRIO
    # UTC → UTC-3
    # ==========================================

    print("Corrigindo horário UTC → UTC-3...")

    # Cria uma coluna com a data e hora original do INMET
    df["DataHora_UTC"] = pd.to_datetime(
        df["Data"].astype(str)
        + " "
        + df["Hora"].astype(str).str.zfill(4),
        format="%d/%m/%Y %H%M",
        errors="coerce"
    )

    # Subtrai 3 horas
    df["DataHora"] = (
        df["DataHora_UTC"]
        - pd.Timedelta(hours=3)
    )

    # ==========================================
    # REMOVER DIAS FORA DO PERÍODO
    # ==========================================

    print("Removendo registros fora do período...")

    df = df[
        (df["DataHora"] >= data_inicio) &
        (df["DataHora"] < data_fim + pd.Timedelta(days=1))
    ].copy()

    # ==========================================
    # RECRIAR DATA E HORA
    # ==========================================

    df["Data"] = df["DataHora"].dt.strftime(
        "%d/%m/%Y"
    )

    df["Hora"] = df["DataHora"].dt.time

    # ==========================================
    # ORDENAR
    # ==========================================

    df = df.sort_values(
        "DataHora"
    ).reset_index(drop=True)

    # ==========================================
    # CONFERÊNCIA
    # ==========================================

    print("\n==========================================")
    print("TRATAMENTO DE HORÁRIO CONCLUÍDO")
    print("==========================================")

    print(
        "Primeiro registro:",
        df["DataHora"].iloc[0]
    )

    print(
        "Último registro:",
        df["DataHora"].iloc[-1]
    )

    print(
        "Total de registros após tratamento:",
        len(df)
    )

    print("\nPrimeiros registros:")

    print(
        df[
            [
                "Data",
                "Hora",
                "Temperatura_Inst"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )
    # ==========================================
    # REMOVER COLUNAS AUXILIARES
    # ==========================================

    df = df.drop(
        columns=["DataHora_UTC", "DataHora"]
    )
    
    # ==========================================
    # CONVERTER DADOS NUMÉRICOS
    # ==========================================

    colunas_imputacao = [
        "Temperatura_Inst",
        "Temperatura_Max",
        "Temperatura_Min",
        "Umidade_Inst",
        "Umidade_Max",
        "Umidade_Min",
        "Ponto_Orvalho_Inst",
        "Ponto_Orvalho_Max",
        "Ponto_Orvalho_Min",
        "Pressao_Inst",
        "Pressao_Max",
        "Pressao_Min",
        "Vento_Velocidade",
        "Vento_Direcao",
        "Vento_Rajada"
    ]

    for coluna in colunas_imputacao:
        df[coluna] = (
            df[coluna]
            .astype(str)
            .str.replace(",", ".", regex=False)
            .replace("", pd.NA)
        )

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )
    #IMPUTADOR PRO MAX
    
    colunas_imputacao = [
    "Temperatura_Inst",
    "Temperatura_Max",
    "Temperatura_Min",
    "Umidade_Inst",
    "Umidade_Max",
    "Umidade_Min",
    "Ponto_Orvalho_Inst",
    "Ponto_Orvalho_Max",
    "Ponto_Orvalho_Min",
    "Pressao_Inst",
    "Pressao_Max",
    "Pressao_Min",
    "Vento_Velocidade",
    "Vento_Direcao",
    "Vento_Rajada"
    ]
    print("Imputando dados faltosos")
    for coluna in colunas_imputacao:

        valores_faltantes = df[coluna].isnull()

        media_dia = (
            df.groupby("Data")[coluna]
            .transform("mean")
            .round(2)
        )

        df.loc[valores_faltantes, coluna] = (
            media_dia[valores_faltantes]
        )
    # ==========================================
    # SALVAR DADOS TRATADOS
    # ==========================================

    caminho = os.path.abspath(
        "dados_brutos_tratados.xlsx"
    )

    df.to_excel(
        caminho,
        index=False
    )

    print("\n==========================================")
    print("ARQUIVO SALVO!")
    print("==========================================")
    print(caminho)

    input("\nPressione ENTER para fechar...")

    browser.close()