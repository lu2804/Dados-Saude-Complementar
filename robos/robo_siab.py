import pandas as pd
import os

PASTA_DADOS = "dados/dados_brutos"

def baixar_siab():

    print("\nIniciando coleta SIAB...")

    dados = {
        "Ano": [2020, 2021, 2022],
        "Visitas": [12000, 15000, 18000],
        "Gestantes": [320, 350, 410]
    }

    df = pd.DataFrame(dados)

    os.makedirs(PASTA_DADOS, exist_ok=True)

    caminho = f"{PASTA_DADOS}/siab_exemplo.csv"

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Arquivo salvo em: {caminho}")
    print(df.head())