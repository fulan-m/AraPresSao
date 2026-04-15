# %% - Carregamentos
# Estamos tentando ressucitar o código que produzia essa tabela. Não vai ser fácil.
import os
import numpy as np
import pandas as pd
import geopandas as gpd

diretorio_chuva = "C:/Users/mateu/OneDrive/Projetos/arapressao/0-dados_globais/dados_processados/tabelas/daee-chuva_diaria-arapressao"
# O nome do arquivo corresponde ao código da estação (B6-001.csv)
# Padrão das tabelas
# DATE,VALUES
# 1936-02-01,0.0

diretorio_usos = "C:/Users/mateu/OneDrive/Projetos/arapressao/0-dados_globais/dados_brutos/tabelas/mapbi-usos_estacoes"
# O nome do arquivo corresponde ao tamanho do buffer (BUFFER_SIZE) - mapbi-usos_estacoes-12.5km.csv
# Padrão das tabelas
# area;class;st_numerat;record_year
# 25.26948264;3;199;1985

dicionario_classes = pd.read_json("C:/Users/mateu/OneDrive/Projetos/arapressao/0-dados_globais/dados_brutos/json-dicionarios/mapbi-class_dictionary.json")
# [
#     {
#         "code": "1",
#         "class_name": "Forest"
#     },

dicionario_numerat = pd.read_json("C:/Users/mateu/OneDrive/Projetos/arapressao/0-dados_globais/dados_brutos/json-dicionarios/daee-station_dictionary.json")
# [
#     {
#         "st_numerat":1,
#         "st_code":"A6-001"
#     },

shapefile_arapressao = gpd.read_file("C:/Users/mateu/OneDrive/Projetos/arapressao/1-chirps_daee-clusters_e_sem/sig/vetoriais/limiites_arapressao/limites_arapressao.shp")
#   CD_RGINT               NM_RGINT SIGLA_UF   AREA_KM2  \
# 0     3505    Presidente Prudente       SP  24846.934   
# 1     3506              Araçatuba       SP  18785.618   
# 2     3507  São José do Rio Preto       SP  26089.301   

shapefile_estacoes = gpd.read_file("C:/Users/mateu/OneDrive/Projetos/arapressao/1-chirps_daee-clusters_e_sem/sig/vetoriais/estacoes_daee-filtradas/estacoes_daee-filtradas.shp")
#      ST_NUMERAT ST_CODE               ST_NAME                      ST_MUN  \
# 0           116  B6-001                  ICEM                        ICEM   
# 1           117  B6-002              MIRASSOL                    MIRASSOL   
# 2           118  B6-003              CASTORES                  ONDA VERDE   
# 3           121  B6-006          BADY BASSITT                 BADY BASSIT   
# 4           125  B6-009               TABAPUA                     TABAPUA   
# ..          ...     ...                   ...                         ...   
# 106        1120  D9-004     EUCLIDES DA CUNHA  EUCLIDES DA CUNHA PAULISTA   
# 107        1122  D9-006       CUIABA PAULISTA     MIRANTE DO PARANAPANEMA   
# 108        1123  D9-014      FAZENDA ROSANELA             TEODORO SAMPAIO   
# 109        1129  D9-020                PONTAL             TEODORO SAMPAIO   
# 110        1131  D9-022  FAZENDA PONTE BRANCA  EUCLIDES DA CUNHA PAULISTA   


# %% - Usos
# Vamos ler todos os diretorios em diretorio_usos
# e colocar a parte final como uma nova coluna
# chamada BUFFER_SIZE (mapbi-usos_estacoes-12.5km.csv)
def read_usos(diretorio):
    usos = []
    for file in os.listdir(diretorio):
        if file.endswith(".csv"):
            buffer_size = file.split('-')[-1].replace('.csv', '')
            df = pd.read_csv(os.path.join(diretorio, file), sep=';')
            df['BUFFER_SIZE'] = buffer_size
            usos.append(df)
    return pd.concat(usos, ignore_index=True)
usos_df = read_usos(diretorio_usos)

# Agora usamos o dicionario para traduzir 'class'
usos_df = usos_df.merge(dicionario_classes, left_on='class', right_on='code', how='left')
usos_df = usos_df.merge(dicionario_numerat, left_on='st_numerat', right_on='st_numerat', how='left')

# Rearrange it
usos_df = usos_df[["st_code", "class_name", "record_year", "area", "BUFFER_SIZE"]]
#        st_code             class_name  record_year        area BUFFER_SIZE
# 0       B7-053       Forest Formation         1985   25.269483      12.5km

# %% - Chuva
# Aqui precisamos recortar shapefile_estacoes com shapefile_arapressao, criando
# uma lista para cada "NM_RGINT" no shape arapressao.

presidente_prudente = shapefile_arapressao[shapefile_arapressao['NM_RGINT'] == 'Presidente Prudente']
sao_jose_do_rio_preto = shapefile_arapressao[shapefile_arapressao['NM_RGINT'] == 'São José do Rio Preto']
aracatuba = shapefile_arapressao[shapefile_arapressao['NM_RGINT'] == 'Araçatuba']

# Recortamos as estações usando as 3 regiões
estacoes_pp = gpd.clip(shapefile_estacoes, presidente_prudente)
estacoes_sjrp = gpd.clip(shapefile_estacoes, sao_jose_do_rio_preto)
estacoes_ara = gpd.clip(shapefile_estacoes, aracatuba)

# Agora criamos uma lista com os ST_CODE dentro de cada região
lista_pp = estacoes_pp['ST_CODE'].tolist()
lista_sjrp = estacoes_sjrp['ST_CODE'].tolist()
lista_ara = estacoes_ara['ST_CODE'].tolist()

# %%
# A partir do diretório, vamos pegar cada arquivo, calcular
# a chuva acumulada por mês, e criamos uma tabela matriz disso
# A tabela é assim:
# DATE,VALUES
# 1936-02-01,0.0
# E sabemos que o nome dos arquivos correspondem ao st_code

# %%
# Initialize an empty list to collect all DataFrames
output = []

for filename in os.listdir(diretorio_chuva):
    if filename.endswith(".csv"):
        # Read each CSV file
        df = pd.read_csv(os.path.join(diretorio_chuva, filename), sep=',')
        
        # Clean data
        df["VALUES"] = df["VALUES"].replace(-99, np.nan)
        
        # Extract date components
        df["YEAR"] = pd.to_datetime(df["DATE"]).dt.year
        df["MONTH"] = pd.to_datetime(df["DATE"]).dt.month
        
        # Group by year and month to get monthly sums
        group_df = df.groupby(['YEAR', 'MONTH']).agg({'VALUES': 'sum'}).reset_index()
        
        # Extract station code from filename (without .csv extension)
        st_code = filename.split('.')[0]
        group_df["ST_CODE"] = st_code
        
        # Append to output list
        output.append(group_df)

# Combine all DataFrames in the output list
final_output = pd.concat(output, ignore_index=True)

# %%
# Colunas da Tabela Matriz:
# YEAR_MONTH: Data no formato "YYYY-MM" (ex: "2010-01")
# ARAPRESSAO: Nome da região (ex: 'Araçatuba', 'Presidente Prudente', 'São José do Rio Preto')
# BUFFER_SIZE: Tamanho do buffer (o código filtra apenas '20KM')
# ST_CODE: Código da estação meteorológica
# CLASS: Tipo de cobertura do solo (o código filtra apenas 'Pasture')
# MONTHLY_PREC: Precipitação mensal (variável principal analisada)
# YEAR: Extraído da coluna YEAR_MONTH (não estava presente no original)
# MONTH: Extraído da coluna YEAR_MONTH (não estava presente no original)

# Agora, vamos juntar tudo
merged_df = final_output.merge(usos_df, left_on=['ST_CODE', 'YEAR'], right_on=['st_code', 'record_year'], how='right')
print(merged_df)

# Finalmente, utilizamos as listas de arapressao para adicionar
# a "ARAPRESSAO" correspondente a cada ST_CODE

merged_df.loc[merged_df['ST_CODE'].isin(lista_pp), 'ARAPRESSAO'] = 'Presidente Prudente'
merged_df.loc[merged_df['ST_CODE'].isin(lista_sjrp), 'ARAPRESSAO'] = 'São José do Rio Preto'
merged_df.loc[merged_df['ST_CODE'].isin(lista_ara), 'ARAPRESSAO'] = 'Araçatuba'

merged_df["YEAR_MONTH"] = merged_df["YEAR"].astype(str) + "-" + merged_df["MONTH"].astype(str).str.zfill(2)
print(merged_df)


# %%
# Agora, vamos renomear as colunas para bater com a tabela matriz
# Primeiro renomeamos as colunas
merged_df = merged_df.rename(columns={
    "class_name": "CLASS",
    "VALUES": "MONTHLY_PREC"
})
merged_df = merged_df[[
    "YEAR_MONTH", "ARAPRESSAO", "BUFFER_SIZE", "ST_CODE", "CLASS", "area", "MONTHLY_PREC", "YEAR", "MONTH"]]

merged_df.to_csv("C:\\Users\\mateu\\OneDrive\\Projetos\\arapressao\\4-augm_arima\\resultados\\usos_chuva_matriz.csv", index=False)