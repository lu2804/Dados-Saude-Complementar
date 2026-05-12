import pandas as pd
import os

def baixar_imunizacao():

    dados = {
        "Ano": [2020, 2021, 2022],
        "Vacinas_Aplicadas": [100000, 150000, 180000],
        "Cobertura": [75, 82, 91]
    }

    df = pd.DataFrame(dados)

    os.makedirs("dados_brutos", exist_ok=True)

    caminho = "dados_brutos/imunizacao.csv"

    df.to_csv(caminho, index=False)

    print("\nDados de imunização salvos com sucesso!")
    print(df.head())