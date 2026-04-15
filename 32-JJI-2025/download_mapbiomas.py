# %%
# Vamos baixar cada imagem disponível no link, trocando
# apenas o ano no final (1985-2024). Assim que baixado,
# vamos usar um shapefile para recortar a área, e depois
# mantemos apenas o raster cortado. Link:
# https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_10/lulc/coverage/brazil_coverage_2024.tif

import geopandas as gpd

regiao = gpd.read_file("C:\\Users\\mateu\\OneDrive\\Projetos\\arapressao\\4-augm_arima\\sig\\vetoriais\\limites_uf_brasil\\uf_brasil.shp")
regiao = regiao[regiao["Nome"] == "São Paulo"]

saida = "C:\\Users\\mateu\\OneDrive\\Projetos\\arapressao\\4-augm_arima\\resultados\\mapbiomas_sp"

anos_disponiveis = list(range(1985, 2025))

def baixar_e_cortar(ano):
    url = f"https://storage.googleapis.com/mapbiomas-public/initiatives/brasil/collection_10/lulc/coverage/brazil_coverage_{ano}.tif"
    arquivo = f"{saida}\\brazil_coverage_{ano}.tif"
    gpd.read_file(url).clip(regiao.geometry).to_file(arquivo)

    print(f"Arquivo salvo em: {arquivo}")

# Teste
baixar_e_cortar(2024)