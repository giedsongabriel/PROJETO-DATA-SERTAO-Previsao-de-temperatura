from playwright.sync_api import sync_playwright
from datetime import date, timedelta
import pandas as pd
import os


# ========================================================
# CONFIGURAÇÕES
# ========================================================

DATA_FIM = pd.Timestamp(date.today())
DATA_INICIO = DATA_FIM - pd.Timedelta(days=1)

ESTADO = "Pernambuco"
ESTACAO = "CABROBO (A329)"

ARQUIVO_SAIDA = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "site",
        "dados_coletados.xlsx"
    )
)


# ========================================================
# COLETA DOS DADOS
# ========================================================

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=True,
        executable_path=r"C:\Users\Administrator\AppData\Local\ms-playwright\chromium-1234\chrome-win64\chrome.exe"
    )

    page = browser.new_page()

    print("Abrindo INMET...")

    page.goto(
        "https://tempo.inmet.gov.br/",
        wait_until="domcontentloaded",
        timeout=60000
    )

    # ====================================================
    # ESCOLHE O TIPO DE CONSULTA
    # ====================================================

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

    # ====================================================
    # LOCALIZA OS CAMPOS DO FORMULÁRIO
    # ====================================================

    inputs = page.locator("input.search")

    inputs.nth(1).wait_for(
        state="visible",
        timeout=30000
    )

    # ====================================================
    # SELECIONA O ESTADO
    # ====================================================

    print("Selecionando Pernambuco...")

    estado = inputs.nth(1)

    estado.click()

    page.wait_for_timeout(300)

    page.get_by_text(
        ESTADO,
        exact=True
    ).click()

    # ====================================================
    # SELECIONA A ESTAÇÃO
    # ====================================================

    print("Selecionando Cabrobó...")

    estacao = inputs.nth(2)

    estacao.click()

    page.wait_for_timeout(300)

    page.get_by_text(
        ESTACAO,
        exact=True
    ).click()

    # ====================================================
    # DEFINE O PERÍODO DA COLETA
    #
    # SOMENTE ONTEM E HOJE
    # ====================================================

    datas = page.locator(
        'input[type="date"]'
    )

    datas.nth(0).fill(
        DATA_INICIO.strftime("%Y-%m-%d")
    )

    datas.nth(1).fill(
        DATA_FIM.strftime("%Y-%m-%d")
    )

    print(
        f"Periodo da coleta: "
        f"{DATA_INICIO.strftime('%d/%m/%Y')} ate "
        f"{DATA_FIM.strftime('%d/%m/%Y')}"
    )

    # ====================================================
    # GERA A TABELA NO INMET
    # ====================================================

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

    tabela = page.locator(
        "table"
    ).first

    tabela.wait_for(
        state="visible",
        timeout=60000
    )

    print("Tabela gerada!")

    # ====================================================
    # LÊ OS DADOS DA TABELA
    # ====================================================

    print("Lendo dados da tabela...")

    dados = tabela.locator(
        "tbody tr"
    ).evaluate_all(
        """
        rows => rows.map(row =>
            Array.from(
                row.querySelectorAll("td")
            ).map(
                cell => cell.innerText.trim()
            )
        )
        """
    )

    print("Dados coletados.")

    # ========================================================
    # DATAFRAME
    # ========================================================

    df_novo = pd.DataFrame(dados)

    # ========================================================
    # NOMES DAS COLUNAS
    # ========================================================

    df_novo.columns = [
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

    print(
        f"Registros coletados: {len(df_novo)}"
    )

    # ========================================================
    # REMOVER RADIAÇÃO E CHUVA
    # ========================================================

    df_novo = df_novo.drop(
        columns=[
            "Radiacao",
            "Chuva"
        ]
    )

    # ========================================================
    # CORREÇÃO DE HORÁRIO
    #
    # INMET → UTC
    # UTC → UTC-3
    # ========================================================

    print(
        "Corrigindo horario UTC para UTC-3..."
    )

    df_novo["DataHora_UTC"] = pd.to_datetime(
        df_novo["Data"].astype(str).str.strip()
        + " "
        + df_novo["Hora"].astype(str).str.strip().str.zfill(4),
        format="%d/%m/%Y %H%M",
        errors="coerce"
    )

    df_novo = df_novo.dropna(
        subset=["DataHora_UTC"]
    ).copy()

    df_novo["DataHora"] = (
        df_novo["DataHora_UTC"]
        - pd.Timedelta(hours=3)
    )

    # ========================================================
    # REMOVER DIAS EXTRAS
    # ========================================================

    print(
        "Removendo registros fora do periodo..."
    )

    inicio = DATA_INICIO.normalize()

    fim = (
        DATA_FIM.normalize()
        + pd.Timedelta(days=1)
    )

    df_novo = df_novo[
        (df_novo["DataHora"] >= inicio)
        &
        (df_novo["DataHora"] < fim)
    ].copy()

    # ========================================================
    # ORDENAR
    # ========================================================

    df_novo = (
        df_novo
        .sort_values("DataHora")
        .reset_index(drop=True)
    )

    # ========================================================
    # RECRIAR DATA E HORA
    # ========================================================

    df_novo["Data"] = (
        df_novo["DataHora"]
        .dt.date
    )

    df_novo["Hora"] = (
        df_novo["DataHora"]
        .dt.time
    )

    # ========================================================
    # REMOVER COLUNAS AUXILIARES
    # ========================================================

    df_novo = df_novo.drop(
        columns=[
            "DataHora_UTC",
            "DataHora"
        ]
    )

    # ========================================================
    # CONVERTER DADOS NUMÉRICOS
    # ========================================================

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

        df_novo[coluna] = (
            df_novo[coluna]
            .astype(str)
            .str.strip()
            .str.replace(
                ",",
                ".",
                regex=False
            )
            .replace(
                "",
                pd.NA
            )
        )

        df_novo[coluna] = pd.to_numeric(
            df_novo[coluna],
            errors="coerce"
        )

    # ========================================================
    # REMOVER HORAS SEM NENHUM DADO
    # ========================================================

    print(
        "Removendo horas sem nenhuma leitura..."
    )

    linhas_totalmente_vazias = (
        df_novo[colunas_imputacao]
        .isna()
        .all(axis=1)
    )

    df_novo = df_novo[
        ~linhas_totalmente_vazias
    ].copy()

    # ========================================================
    # IMPUTAÇÃO
    # ========================================================

    print(
        "Imputando dados faltosos..."
    )

    for coluna in colunas_imputacao:

        faltantes = df_novo[coluna].isna()

        media_dia = (
            df_novo.groupby("Data")[coluna]
            .transform("mean")
            .round(2)
        )

        df_novo.loc[
            faltantes,
            coluna
        ] = media_dia[
            faltantes
        ]

    # ========================================================
    # ========================================================
    # ATUALIZAÇÃO DO ARQUIVO EXISTENTE
    # ========================================================
    # ========================================================

    print()
    print("Atualizando dados_coletados.xlsx...")

    # ========================================================
    # LÊ O ARQUIVO EXISTENTE
    # ========================================================

    if os.path.exists(ARQUIVO_SAIDA):

        xls = pd.ExcelFile(
            ARQUIVO_SAIDA
        )

        # Usa a primeira aba para recuperar
        # todas as datas já existentes.
        df_existente = pd.read_excel(
            ARQUIVO_SAIDA,
            sheet_name=xls.sheet_names[0]
        )

        # ====================================================
        # REMOVE DO HISTÓRICO AS DATAS QUE SERÃO ATUALIZADAS
        # ====================================================

        df_existente["Data"] = pd.to_datetime(
            df_existente["Data"],
            errors="coerce"
        ).dt.date

        datas_atualizadas = {
            DATA_INICIO.date(),
            DATA_FIM.date()
        }

        df_existente = df_existente[
            ~df_existente["Data"].isin(
                datas_atualizadas
            )
        ].copy()

        # ====================================================
        # RECUPERA OS DADOS BRUTOS DO ARQUIVO EXISTENTE
        #
        # As abas possuem somente uma variável, então usamos
        # a aba de temperatura instantânea como referência
        # para preservar o histórico de datas.
        # ====================================================

        # O histórico das variáveis será reconstruído
        # posteriormente a partir das abas existentes.

        dfs_existentes = {}

        for nome_aba in xls.sheet_names:

            tabela = pd.read_excel(
                ARQUIVO_SAIDA,
                sheet_name=nome_aba
            )

            tabela["Data"] = pd.to_datetime(
                tabela["Data"],
                errors="coerce"
            ).dt.date

            tabela = tabela[
                ~tabela["Data"].isin(
                    datas_atualizadas
                )
            ].copy()

            dfs_existentes[nome_aba] = tabela

    else:

        dfs_existentes = {}

    # ========================================================
    # REESTRUTURAÇÃO POR HORA
    # ========================================================

    print(
        "Reestruturando dados por hora..."
    )

    df_novo["Hora_Texto"] = (
        pd.to_datetime(
            df_novo["Hora"].astype(str),
            format="%H:%M:%S",
            errors="coerce"
        )
        .dt.strftime("%Hh")
    )

    # ========================================================
    # VARIÁVEIS
    # ========================================================

    variaveis = [
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

    # ========================================================
    # NOMES DAS ABAS
    # ========================================================

    nomes_abas = {
        "Temperatura_Inst": "Temp. Ins. (C)",
        "Temperatura_Max": "Temp. Max. (C)",
        "Temperatura_Min": "Temp. Min. (C)",
        "Umidade_Inst": "Umi. Ins. (%)",
        "Umidade_Max": "Umi. Max. (%)",
        "Umidade_Min": "Umi. Min. (%)",
        "Ponto_Orvalho_Inst": "Pto Orvalho Ins. (C)",
        "Ponto_Orvalho_Max": "Pto Orvalho Max. (C)",
        "Ponto_Orvalho_Min": "Pto Orvalho Min. (C)",
        "Pressao_Inst": "Pressao Ins. (hPa)",
        "Pressao_Max": "Pressao Max. (hPa)",
        "Pressao_Min": "Pressao Min. (hPa)",
        "Vento_Velocidade": "Vel. Vento (m-s)",
        "Vento_Direcao": "Dir. Vento (m-s)",
        "Vento_Rajada": "Raj. Vento (m-s)"
    }

    # ========================================================
    # CRIA O EXCEL FINAL
    # ========================================================

    with pd.ExcelWriter(
        ARQUIVO_SAIDA,
        engine="openpyxl"
    ) as writer:

        for variavel in variaveis:

            # -----------------------------------------------
            # NOVOS DADOS
            # -----------------------------------------------

            tabela_nova = (
                df_novo
                .pivot_table(
                    index="Data",
                    columns="Hora_Texto",
                    values=variavel,
                    aggfunc="first"
                )
                .reset_index()
            )

            # -----------------------------------------------
            # 24 HORAS
            # -----------------------------------------------

            horas = [
                f"{i:02d}h"
                for i in range(24)
            ]

            tabela_nova = tabela_nova.reindex(
                columns=[
                    "Data"
                ] + horas
            )

            tabela_nova["Data"] = pd.to_datetime(
                tabela_nova["Data"]
            ).dt.date

            # -----------------------------------------------
            # DADOS ANTIGOS
            # -----------------------------------------------

            nome_aba = nomes_abas[variavel]
            nome_aba = nome_aba[:31]

            if nome_aba in dfs_existentes:

                tabela_antiga = dfs_existentes[nome_aba].copy()

                tabela_antiga["Data"] = pd.to_datetime(
                    tabela_antiga["Data"],
                    errors="coerce"
                ).dt.date

                # Garante as mesmas colunas
                tabela_antiga = tabela_antiga.reindex(
                    columns=[
                        "Data"
                    ] + horas
                )

                tabela_final = pd.concat(
                    [
                        tabela_antiga,
                        tabela_nova
                    ],
                    ignore_index=True
                )

            else:

                tabela_final = tabela_nova

            # -----------------------------------------------
            # ORDENA POR DATA
            # -----------------------------------------------

            tabela_final = (
                tabela_final
                .sort_values("Data")
                .reset_index(drop=True)
            )

            # -----------------------------------------------
            # SALVA
            # -----------------------------------------------

            tabela_final.to_excel(
                writer,
                sheet_name=nome_aba,
                index=False
            )

            # -----------------------------------------------
            # FORMATA DATA
            # -----------------------------------------------

            planilha = writer.sheets[nome_aba]

            total_linhas = len(tabela_final)

            for linha in range(
                2,
                total_linhas + 2
            ):

                celula = planilha.cell(
                    row=linha,
                    column=1
                )

                celula.number_format = "DD/MM/YYYY"

    # ========================================================
    # CONFERÊNCIA FINAL
    # ========================================================

    print()
    print("==========================================")
    print("ATUALIZACAO CONCLUIDA")
    print("==========================================")

    print(
        f"Periodo atualizado: "
        f"{DATA_INICIO.strftime('%d/%m/%Y')} ate "
        f"{DATA_FIM.strftime('%d/%m/%Y')}"
    )

    print(
        "Novos registros:",
        len(df_novo)
    )

    print()
    print("==========================================")
    print("ARQUIVO ATUALIZADO")
    print("==========================================")

    print(ARQUIVO_SAIDA)

    browser.close()