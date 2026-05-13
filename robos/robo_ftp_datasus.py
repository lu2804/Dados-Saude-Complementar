from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def listar_arquivos_datasus():

    url = "https://ftp.datasus.gov.br/dissemin/publicos/SIAB/200801_/Dados/"

    options = webdriver.ChromeOptions()

    options.binary_location = "/usr/bin/google-chrome"

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    print("\nAbrindo DATASUS...")

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    driver.get(url)

    html = driver.page_source

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    links = soup.find_all("a")

    arquivos = []

    for link in links:

        nome = link.get("href")

        if nome and nome.endswith(".dbc"):

            arquivos.append(nome)

    if len(arquivos) == 0:

        print("\nNenhum arquivo encontrado.")

    else:

        print("\nArquivos encontrados:\n")

        for arquivo in arquivos[:20]:
            print(arquivo)

    driver.quit()