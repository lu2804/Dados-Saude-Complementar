import requests
import os

PASTA_DADOS = "dados/dados_brutos"

def baixar_arquivo(url, nome_arquivo):

    print("\nBaixando arquivo do DATASUS...")

    os.makedirs(PASTA_DADOS, exist_ok=True)

    caminho = os.path.join(PASTA_DADOS, nome_arquivo)

    try:

        resposta = requests.get(
            url,
            timeout=30
        )

        if resposta.status_code == 200:

            with open(caminho, "wb") as arquivo:
                arquivo.write(resposta.content)

            print(f"Arquivo salvo em: {caminho}")

        else:
            print(f"Erro HTTP: {resposta.status_code}")

    except Exception as erro:
        print(f"Erro no download: {erro}")