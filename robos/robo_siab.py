import pandas as pd
import os


def baixar_siab():

    print("\nIniciando coleta SIAB...")

    # Criar pasta se não existir
    os.makedirs("dados_brutos", exist_ok=True)

    # EXEMPLO TEMPORÁRIO
    dados = {
        "Ano": [2020, 2021, 2022],
        "Visitas": [12000, 15000, 18000],
        "Gestantes": [320, 350, 410]
    }

    df = pd.DataFrame(dados)

    caminho = "dados_brutos/siab_exemplo.csv"

    df.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Arquivo salvo em: {caminho}")

    print("\nPrévia:")
    print(df.head())