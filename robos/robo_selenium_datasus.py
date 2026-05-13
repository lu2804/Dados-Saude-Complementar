from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def acessar_datasus():

    url = "https://ftp.datasus.gov.br/dissemin/publicos/SIAB/200801_/Dados/"

    options = webdriver.ChromeOptions()

    options.binary_location = "/usr/bin/google-chrome"

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")

    print("\nAbrindo navegador...")

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options
    )

    driver.get(url)

    print("\nPágina carregada!\n")

    print(driver.title)

    print("\nHTML da página:\n")

    print(driver.page_source[:3000])

    driver.quit()