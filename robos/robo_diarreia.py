import pandas as pd
import os

PASTA_DADOS = "dados/dados_brutos"

def baixar_diarreia():

    print("\nIniciando coleta de diarreia...")

    dados = {
        "Ano": [2020, 2021, 2022],
        "Casos_Diarreia": [5000, 6200, 7100],
        "Internacoes": [300, 410, 530]
    }

    df = pd.DataFrame(dados)

    os.makedirs(PASTA_DADOS, exist_ok=True)

    caminho = f"{PASTA_DADOS}/diarreia.csv"

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Arquivo salvo em: {caminho}")
    print(df.head())