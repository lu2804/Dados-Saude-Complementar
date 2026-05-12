import pandas as pd
import os

def baixar_diarreia():

    dados = {
        "Ano": [2020, 2021, 2022],
        "Casos_Diarreia": [5000, 6200, 7100],
        "Internacoes": [300, 410, 530]
    }

    df = pd.DataFrame(dados)

    os.makedirs("dados_brutos", exist_ok=True)

    caminho = "dados_brutos/diarreia.csv"

    df.to_csv(caminho, index=False)

    print("\nDados de diarreia salvos com sucesso!")
    print(df.head())