from playwright.sync_api import sync_playwright
from datetime import date
import pandas as pd
import os


# Configurações

DATA_INICIO = pd.Timestamp("2026-03-01")
DATA_FIM = pd.Timestamp(date.today())

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


# Coleta dos dados

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


    # Escolhe o tipo de consulta

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


    # Localiza os campos do formulário

    inputs = page.locator("input.search")

    inputs.nth(1).wait_for(
        state="visible",
        timeout=30000
    )


    # Seleciona o estado

    print("Selecionando Pernambuco...")

    estado = inputs.nth(1)

    estado.click()

    page.wait_for_timeout(300)

    page.get_by_text(
        ESTADO,
        exact=True
    ).click()


    # Seleciona a estação

    print("Selecionando Cabrobó...")

    estacao = inputs.nth(2)

    estacao.click()

    page.wait_for_timeout(300)

    page.get_by_text(
        ESTACAO,
        exact=True
    ).click()


    # Define o período da coleta

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


    # Gera a tabela no INMET

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


    # Lê os dados da tabela

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

    df = pd.DataFrame(dados)


    # ========================================================
    # NOMES DAS COLUNAS
    # ========================================================

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

    print(
        f"Registros coletados: {len(df)}"
    )


    # ========================================================
    # REMOVER RADIAÇÃO E CHUVA
    # ========================================================

    df = df.drop(
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

    # Primeiro interpreta exatamente o horário recebido do INMET.
    df["DataHora_UTC"] = pd.to_datetime(
        df["Data"].astype(str).str.strip()
        + " "
        + df["Hora"].astype(str).str.strip().str.zfill(4),
        format="%d/%m/%Y %H%M",
        errors="coerce"
    )


    # Descarta apenas registros com data ou hora inválidas.
    df = df.dropna(
        subset=["DataHora_UTC"]
    ).copy()


    # Converte para o horário local (UTC-3).
    df["DataHora"] = (
        df["DataHora_UTC"]
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

    df = df[
        (df["DataHora"] >= inicio)
        &
        (df["DataHora"] < fim)
    ].copy()


    # ========================================================
    # ORDENAR
    # ========================================================

    df = (
        df
        .sort_values("DataHora")
        .reset_index(drop=True)
    )


    # ========================================================
    # RECRIAR DATA E HORA
    # ========================================================

    # Mantém "Data" como uma data real para o Excel reconhecer,
    # ordenar e filtrar corretamente, sem mostrar a hora.
    df["Data"] = (
        df["DataHora"]
        .dt.date
    )

    df["Hora"] = (
        df["DataHora"]
        .dt.time
    )


    # ========================================================
    # REMOVER COLUNAS AUXILIARES
    # ========================================================

    df = df.drop(
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

        df[coluna] = (
            df[coluna]
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

        df[coluna] = pd.to_numeric(
            df[coluna],
            errors="coerce"
        )


    # ========================================================
    # REMOVER HORAS SEM NENHUM DADO
    #
    # O INMET já lista, no dia atual, linhas para horas que
    # ainda nao aconteceram (a estacao ainda nao reportou
    # nada). Essas linhas vem com TODAS as variaveis vazias.
    #
    # Se nao removermos essas linhas aqui, a imputacao abaixo
    # (que preenche com a media do dia) vai "inventar" dados
    # para horas que ainda nao ocorreram.
    # ========================================================

    print(
        "Removendo horas sem nenhuma leitura "
        "(ainda nao ocorreram)..."
    )

    linhas_totalmente_vazias = (
        df[colunas_imputacao]
        .isna()
        .all(axis=1)
    )

    df = df[
        ~linhas_totalmente_vazias
    ].copy()


    # ========================================================
    # IMPUTAÇÃO
    #
    # IMPORTANTE:
    # SOMENTE VALORES.
    # NÃO CRIA LINHAS.
    # NÃO CRIA HORÁRIOS.
    # NÃO ALTERA DATAS.
    # ========================================================

    print(
        "Imputando dados faltosos..."
    )

    for coluna in colunas_imputacao:

        faltantes = df[coluna].isna()

        media_dia = (
            df.groupby("Data")[coluna]
            .transform("mean")
            .round(2)
        )

        df.loc[
            faltantes,
            coluna
        ] = media_dia[
            faltantes
        ]


    # ========================================================
    # REESTRUTURAÇÃO POR HORA
    # ========================================================

    print(
        "Reestruturando dados por hora..."
    )

    # A hora vira texto apenas enquanto as colunas horárias são montadas.
    df["Hora_Texto"] = (
        pd.to_datetime(
            df["Hora"].astype(str),
            format="%H:%M:%S",
            errors="coerce"
        )
        .dt.strftime("%Hh")
    )


    # ========================================================
    # COLUNAS QUE SERÃO TRANSFORMADAS
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
    #
    # Mesmos nomes/abreviações usados no dados_por_hora.xlsx
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
    # CRIAR ARQUIVO EXCEL FINAL
    # ========================================================

    with pd.ExcelWriter(
        ARQUIVO_SAIDA,
        engine="openpyxl"
    ) as writer:

        for variavel in variaveis:

            tabela_hora = (
                df
                .pivot_table(
                    index="Data",
                    columns="Hora_Texto",
                    values=variavel,
                    aggfunc="first"
                )
                .reset_index()
            )


            # Mantém sempre as 24 horas na ordem correta.
            horas = [
                f"{i:02d}h"
                for i in range(24)
            ]

            tabela_hora = tabela_hora.reindex(
                columns=[
                    "Data"
                ] + horas
            )


            # Usa o mesmo nome de aba do dados_por_hora.xlsx.
            nome_aba = nomes_abas[variavel]


            # O Excel aceita no máximo 31 caracteres no nome da aba.
            nome_aba = nome_aba[:31]


            tabela_hora.to_excel(
                writer,
                sheet_name=nome_aba,
                index=False
            )


            # Formata a coluna "Data" no padrão brasileiro

            planilha = writer.sheets[nome_aba]

            total_linhas = len(tabela_hora)

            for linha in range(2, total_linhas + 2):

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
    print("TRATAMENTO CONCLUIDO")
    print("==========================================")

    if len(df) > 0:

        # Mostra o primeiro e o último registro após o tratamento.
        data_primeiro = df["Data"].iloc[0]
        hora_primeiro = df["Hora"].iloc[0]

        data_ultimo = df["Data"].iloc[-1]
        hora_ultimo = df["Hora"].iloc[-1]

        print(
            "Primeiro registro:",
            data_primeiro,
            hora_primeiro
        )

        print(
            "Ultimo registro:",
            data_ultimo,
            hora_ultimo
        )

    print(
        "Total de registros:",
        len(df)
    )

    print()
    print("==========================================")
    print("ARQUIVO GERADO")
    print("==========================================")
    print(ARQUIVO_SAIDA)

    browser.close()