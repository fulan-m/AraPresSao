# %%
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("C:\\Users\\mateu\\OneDrive\\Projetos\\arapressao\\4-augm_arima\\resultados\\usos_chuva_matriz.csv", sep=",")

df = df[df["BUFFER_SIZE"] == "12.5km"]

df = df[["YEAR", "ARAPRESSAO", "ST_CODE", "CLASS", "area"]]

df = df.groupby(["YEAR", "ARAPRESSAO", "ST_CODE", "CLASS"]).mean().reset_index()

print(df)

# We group by year, arapressao and class, and get the mean 'area'
df_mean = df.groupby(["YEAR", "ARAPRESSAO", "CLASS"]).agg({"area": "mean"}).reset_index()

# Calculate percentage of each CLASS's area within each YEAR and ARAPRESSAO group
def calculate_percentages(df):
    # Create a sum column for each YEAR-ARAPRESSAO group
    df['total_area'] = df.groupby(['YEAR', 'ARAPRESSAO'])['area'].transform('sum')
    
    # Calculate the percentage
    df['percentage'] = (df['area'] / df['total_area']) * 100
    
    # Drop the temporary total_area column
    df = df.drop(columns=['total_area'])
    
    return df

# Apply the percentage calculation to the entire dataframe
df_percentages = calculate_percentages(df_mean)

# Display the results
print(df_percentages)

# # Test if it is doing everything correctly
# def test_percentage(df, year, arapressao):
#     df = df[df["YEAR"] == year]
#     df = df[df["ARAPRESSAO"] == arapressao]

#     print(df["percentage"].sum())

# test_percentage(df_percentages, 1990, "Araçatuba")

# %%
# Vamos preparar os dados para uma apresentação.
# Queremos comparar a porcentagem de cada classe, nos anos de
# início e fim de cada período (1985-1997, 1998-2010 e 2011-2022)

def comparar_periodos(df, arapressao):
    df = df[df["ARAPRESSAO"] == arapressao]

    print("\n\nResultados para " + arapressao)
    df = df[df["CLASS"].isin(["Forest Formation", "Mosaic of Uses", "Sugar cane", "Pasture"])]

    df["CLASS"] = df["CLASS"].replace({
    "Forest Formation": "Formação Florestal",
    "Mosaic of Uses": "Mosaico de Usos",
    "Sugar cane": "Cana-de-açúcar",
    "Pasture": "Pastagem"
    })

    df_inicial = df[df["YEAR"].isin([1985, 1997])]
    df_intermediario = df[df["YEAR"].isin([1998, 2010])]
    df_final = df[df["YEAR"].isin([2011, 2022])]

    print("Período inicial")
    for classe in df_inicial["CLASS"].unique():
        df_inicial_classe = df_inicial[df_inicial["CLASS"] == classe]

        valor_comeco = (df_inicial_classe[df_inicial_classe["YEAR"] == 1985]["percentage"].values).round(2)
        valor_final = (df_inicial_classe[df_inicial_classe["YEAR"] == 1997]["percentage"].values).round(2)

        diff = (valor_final - valor_comeco).round(2)

        print(f"{arapressao} - {classe}: {valor_comeco} -> {valor_final} == {diff}")

    print("\nPeríodo intermediário")
    for classe in df_intermediario["CLASS"].unique():
        df_intermediario_classe = df_intermediario[df_intermediario["CLASS"] == classe]

        valor_comeco = (df_intermediario_classe[df_intermediario_classe["YEAR"] == 1998]["percentage"].values).round(2)
        valor_final = (df_intermediario_classe[df_intermediario_classe["YEAR"] == 2010]["percentage"].values).round(2)

        diff = (valor_final - valor_comeco).round(2)

        print(f"{arapressao} - {classe}: {valor_comeco} -> {valor_final} == {diff}")

    print("\nPeríodo final")
    for classe in df_final["CLASS"].unique():
        df_final_classe = df_final[df_final["CLASS"] == classe]

        valor_comeco = (df_final_classe[df_final_classe["YEAR"] == 2011]["percentage"].values).round(2)
        valor_final = (df_final_classe[df_final_classe["YEAR"] == 2022]["percentage"].values).round(2)

        diff = (valor_final - valor_comeco).round(2)

        print(f"{arapressao} - {classe}: {valor_comeco} -> {valor_final} == {diff}")

comparar_periodos(df_percentages, "Araçatuba")
comparar_periodos(df_percentages, "São José do Rio Preto")
comparar_periodos(df_percentages, "Presidente Prudente")

# %%
df_plot = df_percentages[df_percentages["CLASS"].isin(["Forest Formation", "Mosaic of Uses", "Sugar cane", "Pasture"])]

# Traduz para o português
df_plot["CLASS"] = df_plot["CLASS"].replace({
    "Forest Formation": "Formação Florestal",
    "Mosaic of Uses": "Mosaico de Usos",
    "Sugar cane": "Cana-de-açúcar",
    "Pasture": "Pastagem"
})

df_ara = df_plot[df_plot["ARAPRESSAO"] == "Araçatuba"]
df_sjrp = df_plot[df_plot["ARAPRESSAO"] == "São José do Rio Preto"]
df_pp = df_plot[df_plot["ARAPRESSAO"] == "Presidente Prudente"]

# Now we do a lineplot, where x is YEAR and y is percentage,
# with CLASS as 4 different colors
def plot_land_use(df):
    plt.rcParams.update({'font.size': 18})

    plt.figure(figsize=(12, 6))

    # Colors for classes
    colors = {
        "Formação Florestal": "#006600",
        "Mosaico de Usos": "#a600a6",
        "Cana-de-açúcar": "#00ff7f",
        "Pastagem": "#ffa500"
    }

    for class_name, group in df.groupby("CLASS"):
        plt.plot(
            group["YEAR"], 
            group["percentage"], 
            marker='.', 
            markersize=14,
            label=class_name, 
            color=colors[class_name], 
            linewidth=4
        )

    # Draw a line in X == 1985.5
    plt.axvline(x=1997.5, color='black', linestyle='--')
    plt.axvline(x=2010.5, color='black', linestyle='--')

    plt.title(f"{df['ARAPRESSAO'].iloc[0]}")
    plt.xlabel("Ano")
    plt.ylabel("Ocupação média (%)")
    plt.legend()

    # Plot only the ticks in a list
    plot_ticks = [1985, 1989, 1993, 1997, 2001, 2006, 2010, 2014, 2018, 2022]
    plt.xticks(plot_ticks, rotation=45)

    plt.ylim(-1, 91)
    plt.xlim(df["YEAR"].min() - 0.5, df["YEAR"].max() + 0.5)

    plt.savefig(
        f"C:\\Users\\mateu\\OneDrive\\Projetos\\arapressao\\4-augm_arima\\figuras\\usos_{df['ARAPRESSAO'].iloc[0]}.png", 
        dpi=900)

plot_land_use(df_ara)
plot_land_use(df_sjrp)
plot_land_use(df_pp)