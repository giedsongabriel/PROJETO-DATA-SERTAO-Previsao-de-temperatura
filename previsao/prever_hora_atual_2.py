import pandas as pd
import numpy as np
import joblib
import os
import requests
from datetime import datetime, timedelta

# 1. Carregar o Snapshot do modelo
snapshot = joblib.load('modelo_snapshot.pkl')
modelo = snapshot['modelo']
colunas_features = snapshot['colunas_features']

# 2. Função para buscar Média, Mínima e Máxima na API Meteorológica Externa (Open-Meteo)
def obter_dados_meteorologicos_api(data_alvo_str, lat=-8.5152, lon=-39.3101):
    """
    Busca média, mínima e máxima diárias de temperatura para uma data na API Open-Meteo.
    Coordenadas configuradas para Cabrobó - PE.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ["temperature_2m_mean", "temperature_2m_min", "temperature_2m_max"],
            "timezone": "America/Recife",
            "start_date": data_alvo_str,
            "end_date": data_alvo_str
        }
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            dados = response.json()
            daily = dados['daily']
            return {
                'media': daily['temperature_2m_mean'][0],
                'min': daily['temperature_2m_min'][0],
                'max': daily['temperature_2m_max'][0]
            }
        return None
    except Exception as e:
        print(f"Aviso: Não foi possível obter dados meteorológicos online. Erro: {e}")
        return None

# 3. Carregar apenas os dados reais da tabela (sem nenhuma imputação)
def obter_dados_ultimo_dia_puro(caminho_excel, colunas_features):
    xls = pd.ExcelFile(caminho_excel)
    dfs = []
    
    for sheet in colunas_features:
        df_sheet = pd.read_excel(xls, sheet_name=sheet)
        df_sheet['Data'] = pd.to_datetime(df_sheet['Data'])
        
        df_melted = df_sheet.melt(id_vars=['Data'], var_name='Hora', value_name=sheet)
        df_melted['DataHora'] = pd.to_datetime(
            df_melted['Data'].dt.strftime('%Y-%m-%d') + ' ' + df_melted['Hora'].astype(str).str.replace('h', ':00')
        )
        dfs.append(df_melted.drop(columns=['Data', 'Hora']))
        
    df_tudo = dfs[0]
    for df in dfs[1:]:
        df_tudo = pd.merge(df_tudo, df, on='DataHora', how='outer')
        
    df_puro = df_tudo.sort_values('DataHora').dropna().reset_index(drop=True)
    df_ultimo_dia = df_puro.tail(24).copy()
    
    data_ultimo_registro = df_ultimo_dia['DataHora'].max()
    vetor_input = df_ultimo_dia[colunas_features].values.flatten()
    return vetor_input.reshape(1, -1), data_ultimo_registro

# 4. Gerar a previsão
input_ultimo_dia, data_ultimo_registro = obter_dados_ultimo_dia_puro('dados_coletados.xlsx', colunas_features)
previsao_proximas_24h = modelo.predict(input_ultimo_dia)[0]

# Métricas Previstas
temp_media_prevista = np.mean(previsao_proximas_24h)
temp_min_prevista = np.min(previsao_proximas_24h)
temp_max_prevista = np.max(previsao_proximas_24h)

data_previsao = (data_ultimo_registro.date() + timedelta(days=1)).strftime('%Y-%m-%d')
data_execucao = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 5. Buscar Dados Meteorológicos na API Externa e calcular as diferenças
dados_api = obter_dados_meteorologicos_api(data_previsao, lat=-8.5152, lon=-39.3101)

if dados_api:
    real_media = dados_api['media']
    real_min = dados_api['min']
    real_max = dados_api['max']
    
    diff_media = temp_media_prevista - real_media
    diff_min = temp_min_prevista - real_min
    diff_max = temp_max_prevista - real_max
else:
    real_media = real_min = real_max = None
    diff_media = diff_min = diff_max = None

# 6. Exibir os resultados no terminal
print("----------------------------------------")
print(f"ÚLTIMA LEITURA REAL NA TABELA: {data_ultimo_registro.strftime('%Y-%m-%d %H:%M')}")
print(f"PREVISÃO PARA O DIA: {data_previsao}")
print(f"Temp. Média Prevista: {temp_media_prevista:.2f} °C")
print(f"Temp. Mínima Prevista: {temp_min_prevista:.2f} °C")
print(f"Temp. Máxima Prevista: {temp_max_prevista:.2f} °C")

if dados_api:
    print("----------------------------------------")
    print("DADOS OBTIDOS DA API METEOROLÓGICA (CABROBÓ - PE):")
    print(f"Temp. Média Externa:   {real_media:.2f} °C (Variação: {diff_media:+.2f} °C)")
    print(f"Temp. Mínima Externa:  {real_min:.2f} °C (Variação: {diff_min:+.2f} °C)")
    print(f"Temp. Máxima Externa:  {real_max:.2f} °C (Variação: {diff_max:+.2f} °C)")
else:
    print("----------------------------------------")
    print("Não foi possível consultar as temperaturas na API externa.")
print("----------------------------------------")

# 7. Salvar/Atualizar no Histórico (CSV)
arquivo_historico = 'historico_previsoes2.csv'

nova_previsao = pd.DataFrame([{
    'Data_Execucao': data_execucao,
    'Data_Ultima_Leitura': data_ultimo_registro.strftime('%Y-%m-%d %H:%M'),
    'Data_Prevista': data_previsao,
    'Temp_Media_Prevista_C': round(temp_media_prevista, 2),
    'Temp_Min_Prevista_C': round(temp_min_prevista, 2),
    'Temp_Max_Prevista_C': round(temp_max_prevista, 2),
    'Temp_Media_API_Externa_C': round(real_media, 2) if real_media is not None else 'N/A',
    'Temp_Min_API_Externa_C': round(real_min, 2) if real_min is not None else 'N/A',
    'Temp_Max_API_Externa_C': round(real_max, 2) if real_max is not None else 'N/A',
    'Diferenca_Media_C': round(diff_media, 2) if diff_media is not None else 'N/A',
    'Diferenca_Min_C': round(diff_min, 2) if diff_min is not None else 'N/A',
    'Diferenca_Max_C': round(diff_max, 2) if diff_max is not None else 'N/A'
}])

try:
    if not os.path.exists(arquivo_historico):
        nova_previsao.to_csv(arquivo_historico, index=False, sep=';', encoding='utf-8-sig')
        print(f"Arquivo '{arquivo_historico}' criado com sucesso!")
    else:
        nova_previsao.to_csv(arquivo_historico, mode='a', header=False, index=False, sep=';', encoding='utf-8-sig')
        print(f"Nova previsão e comparativo salvos em '{arquivo_historico}'!")

except PermissionError:
    print(f"\nERRO DE PERMISSÃO: Feche o arquivo '{arquivo_historico}' no Excel antes de rodar o script!")