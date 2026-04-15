# %% - Individual tables for each ARAPRESSAO

## >>>>> USAR DADOS DE 2023 OU SEJA, DESCARTAR SÓ O LULC DELAS

import os
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Print out the versions of all libraries
print(f"Using numpy version: {np.__version__}")
print(f"Using pandas version: {pd.__version__}")
print(f"Using seaborn version: {sns.__version__}")

warnings.filterwarnings("ignore")  # Suppress all warnings (not recommended for debugging)

MAIN_DIR = os.path.abspath('').removesuffix('python')
df = pd.read_csv(r"C:\Users\mateu\OneDrive\Projetos\arapressao\4-augm_arima\resultados\usos_chuva_matriz.csv", sep=',')
cmap = plt.colormaps['viridis']  # Updated to use the recommended method

df = df[df['BUFFER_SIZE'] == '20km']

# print(df)

def individual_tables(df, arapressao):
    """
    Create individual tables for each ARAPRESSAO.
    """
    df_arapressao = df[df['ARAPRESSAO'] == arapressao]
    df_arapressao = df_arapressao.drop(columns=['YEAR', 'ARAPRESSAO', 'BUFFER_SIZE'])
    df_arapressao['YEAR'] = df_arapressao['YEAR_MONTH'].str[:4]
    df_arapressao['MONTH'] = df_arapressao['YEAR_MONTH'].str[5:7]
    df_arapressao = df_arapressao.drop(columns=['YEAR_MONTH'])
    
    return df_arapressao

a_df = individual_tables(df, 'Araçatuba')
pp_df = individual_tables(df, 'Presidente Prudente')
sjrp_df = individual_tables(df, 'São José do Rio Preto')

# print(a_df)

def pasture_error_filter(df):
    """
    Filter the DataFrame for 'Pasture' class.
    """
    return df[df['CLASS'] == 'Pasture']

a_df_pasture = pasture_error_filter(a_df).copy()
pp_df_pasture = pasture_error_filter(pp_df).copy()
sjrp_df_pasture = pasture_error_filter(sjrp_df).copy()

print(a_df_pasture)

# Periods are 1985-1997, 1998-2010, 2011-2022. Let's just add
# add a 'PERIOD' column to each DataFrame.
def add_period_column(df):
    """
    Add a 'PERIOD' column to the DataFrame based on the YEAR.
    """
    conditions = [
        (df['YEAR'].astype(int) >= 1985) & (df['YEAR'].astype(int) <= 1997),
        (df['YEAR'].astype(int) >= 1998) & (df['YEAR'].astype(int) <= 2010),
        (df['YEAR'].astype(int) >= 2011)
    ]
    choices = ['1985-1997', '1998-2010', '2011-2022']
    
    df['PERIOD'] = np.select(conditions, choices, default='Unknown')
    return df

a_df_pasture = add_period_column(a_df_pasture)
pp_df_pasture = add_period_column(pp_df_pasture)
sjrp_df_pasture = add_period_column(sjrp_df_pasture)

print(a_df_pasture)
import scipy.stats as stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from scikit_posthocs import posthoc_dunn

def analyze_rainfall_periods(df, region_name):
    """
    Analyze rainfall differences between periods for a given region.
    Now includes Dunn's post-hoc test.
    """
    print(f"\n=== Rainfall Analysis for {region_name} ===")
    
    # 1. Group by ST_CODE and PERIOD to get mean rainfall
    period_stats = df.groupby(['ST_CODE', 'PERIOD'])['MONTHLY_PREC'].mean().unstack()
    
    # 2. Statistical tests
    groups = [period_stats[col].dropna() for col in period_stats.columns]
    
    # Normality check
    normal = all(stats.shapiro(group)[1] > 0.05 for group in groups)
    
    if normal and len(groups) > 1:
        # ANOVA
        f_val, p_val = stats.f_oneway(*groups)
        print(f"One-way ANOVA p-value: {p_val:.4f}")
        if p_val < 0.05:
            # Tukey HSD
            melted = period_stats.melt(value_name='RAINFALL', ignore_index=False).reset_index()
            tukey = pairwise_tukeyhsd(melted['RAINFALL'], melted['PERIOD'])
            print(tukey)
    else:
        # Kruskal-Wallis
        h_val, p_val = stats.kruskal(*groups)
        print(f"Kruskal-Wallis p-value: {p_val:.4f}")
        if p_val < 0.05:
            # Dunn's test
            print("\nPost-hoc Dunn's test results:")
            melted = period_stats.melt(value_name='RAINFALL', var_name='PERIOD', ignore_index=False).reset_index()
            dunn_results = posthoc_dunn(melted, val_col='RAINFALL', group_col='PERIOD', p_adjust='bonferroni')
            print(dunn_results)
    
    return period_stats

# Analyze each region
a_stats = analyze_rainfall_periods(a_df_pasture, 'Araçatuba')
pp_stats = analyze_rainfall_periods(pp_df_pasture, 'Presidente Prudente')
sjrp_stats = analyze_rainfall_periods(sjrp_df_pasture, 'São José do Rio Preto')

from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.stattools import durbin_watson

# Example for Araçatuba (assuming one station for simplicity)
a_df_pasture_st_list = a_df_pasture['ST_CODE'].unique().tolist()
station_data = a_df_pasture[a_df_pasture['ST_CODE'] == a_df_pasture_st_list[0]]

# Plot ACF

# Durbin-Watson test
dw_stat = durbin_watson(station_data['MONTHLY_PREC'])
print(f"Durbin-Watson Statistic: {dw_stat}")  # Values near 2 = no autocorrelation
# Durbin showed autocorrelation, let's use ARIMA

from statsmodels.tsa.arima.model import ARIMA
from scikit_posthocs import posthoc_dunn
import warnings

def analyze_with_arima(df, region_name):
    """
    Fixed version with proper residual handling and period comparison
    """
    print(f"\n=== ARIMA Analysis for {region_name} ===")
    
    # Prepare data - ensure proper datetime and sorting
    df = df.sort_values(['ST_CODE', 'YEAR', 'MONTH']).copy()
    df['DATE'] = pd.to_datetime(df['YEAR'] + '-' + df['MONTH'])
    
    # Store all residuals and period info
    all_residuals = []
    
    # Process each station
    for station in df['ST_CODE'].unique():
        station_data = df[df['ST_CODE'] == station].copy()
        
        try:
            # Require at least 2 years of data
            if len(station_data) < 24:
                continue
                
            # Fit seasonal ARIMA
            model = ARIMA(station_data.set_index('DATE')['MONTHLY_PREC'],
                         order=(0, 0, 0),
                         seasonal_order=(1, 0, 1, 12))
            results = model.fit()
            
            # Get residuals with period info
            residuals = pd.DataFrame({
                'RESIDUAL': results.resid,
                'PERIOD': station_data['PERIOD'].values,
                'STATION': station
            })
            all_residuals.append(residuals)
            
        except Exception as e:
            print(f"Station {station} skipped: {str(e)}")
            continue
    
    if not all_residuals:
        print("No valid station models")
        return pd.DataFrame(), pd.DataFrame()
    
    # Combine all residuals
    residuals_df = pd.concat(all_residuals).dropna()
    
    # --- Period Comparison ---
    print("\n=== Period Effects ===")
    
    # 1. Calculate mean effects
    period_effects = residuals_df.groupby('PERIOD')['RESIDUAL'].mean()
    print("\nMean Rainfall Deviations from Expected:")
    print(period_effects.to_string())
    
    # 2. Statistical tests
    results = []
    try:
        # Kruskal-Wallis test
        groups = [g['RESIDUAL'] for _, g in residuals_df.groupby('PERIOD')]
        h_val, p_val = stats.kruskal(*groups)
        print(f"\nKruskal-Wallis p-value: {p_val:.4f}")
        
        if p_val < 0.05:
            # Dunn's post-hoc
            dunn_results = posthoc_dunn(
                residuals_df, 
                val_col='RESIDUAL',
                group_col='PERIOD',
                p_adjust='bonferroni'
            )
            print("\nPost-hoc Dunn's tests:")
            print(dunn_results)
            
            # Middle period focus
            middle = '1998-2010'
            if middle in dunn_results.index:
                results.append({
                    'Region': region_name,
                    'Middle_Effect': period_effects[middle],
                    'P_vs_Early': dunn_results.loc[middle, '1985-1997'],
                    'P_vs_Late': dunn_results.loc[middle, '2011-2022']
                })
    
    except Exception as e:
        print(f"Stats failed: {str(e)}")
    
    return residuals_df, pd.DataFrame(results)

# Run analysis
final_results = []
for name, data in [('Araçatuba', a_df_pasture),
                   ('Presidente Prudente', pp_df_pasture),
                   ('São José do Rio Preto', sjrp_df_pasture)]:
    
    print("\n" + "="*50)
    try:
        _, res = analyze_with_arima(data, name)
        if not res.empty:
            final_results.append(res)
    except Exception as e:
        print(f"Region {name} failed: {str(e)}")

# Final output
if final_results:
    print("\n=== Significant Results ===")
    print(pd.concat(final_results).to_string(index=False))
else:
    print("\nNo significant period differences found")