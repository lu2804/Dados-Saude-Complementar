import pandas as pd
import os

PASTA_DADOS = "dados/dados_brutos"

def baixar_imunizacao():

    print("\nIniciando coleta de imunização...")

    dados = {
        "Ano": [2020, 2021, 2022],
        "Vacinas_Aplicadas": [100000, 150000, 180000],
        "Cobertura": [75, 82, 91]
    }

    df = pd.DataFrame(dados)

    os.makedirs(PASTA_DADOS, exist_ok=True)

    caminho = f"{PASTA_DADOS}/imunizacao.csv"

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Arquivo salvo em: {caminho}")
    print(df.head())