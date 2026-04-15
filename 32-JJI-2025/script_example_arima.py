# %%
import numpy as np
import matplotlib.pyplot as plt

font = {'family': 'Arial',
        'weight': 'normal',
        'size': 20}

plt.rc('font', **font)

def criar_grafico():
    # Months for x-axis
    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
             'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
    
    # Create smooth sine wave for the model
    x_smooth = np.linspace(0, 12, 100)
    y_smooth = np.sin(x_smooth * 0.45 + 1.95) * 50 + 75  # Senoide suavizada
    
    # Create points with random residuals for the actual data
    x_points = np.arange(12)
    y_base = np.sin(x_points * 0.45 + 1.95) * 50 + 75
    
    # Add random variation (±20) to represent residuals
    np.random.seed(42)  # For reproducible results
    random_variation = np.random.uniform(-20, 20, 12)
    chuva_simulada = y_base + random_variation
    
    # Ensure values stay within reasonable bounds
    chuva_simulada = np.clip(chuva_simulada, 0, 150)

    plt.figure(figsize=(12, 6))
    
    # Plot smooth sine wave (model)
    plt.plot(x_smooth, y_smooth, label='Modelo ARIMA', color='red', linewidth=1)
    
    # Plot points with residuals (actual data)
    plt.scatter(x_points, chuva_simulada, color='blue', s=60, 
                label='Chuva Observada', zorder=5)
    
    # Add vertical lines to show residuals
    for i in range(12):
        plt.plot([x_points[i], x_points[i]], [y_base[i], chuva_simulada[i]], 
                'blue', linestyle='--', alpha=0.7, linewidth=3)
    
    plt.xlim(-0.5, 11.5)
    plt.ylim(0, 150)
    plt.title('')
    plt.xlabel('Meses')
    plt.ylabel('Precipitação (mm)')
    plt.xticks(x_points, meses)
    plt.legend()
    plt.tight_layout()
    plt.show()

criar_grafico()