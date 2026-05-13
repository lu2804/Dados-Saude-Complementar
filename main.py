from robos.robo_siab import baixar_siab
from robos.robo_diarreia import baixar_diarreia
from robos.robo_imunizacao import baixar_imunizacao
from robos.robo_selenium_datasus import acessar_datasus
from robos.robo_ftp_datasus import listar_arquivos_datasus
def exibir_menu():

    print("\n===================================")
    print(" ROBÔ DE DADOS DO DATASUS")
    print("===================================")

    print("\nEscolha uma opção:")
    print("1 - Baixar dados SIAB")
    print("2 - Baixar dados de Diarreia")
    print("3 - Baixar dados de Imunização")
    print("4 - Testar conexão Selenium DATASUS")
    print("5 - Listar arquivos DATASUS")
    print("0 - Sair")


def main():

    while True:

        exibir_menu()

        opcao = input("\nDigite a opção: ")

        if opcao == "1":

            baixar_siab()

        elif opcao == "2":

            baixar_diarreia()

        elif opcao == "3":

            baixar_imunizacao()

        elif opcao == "4":

            acessar_datasus()
        
        elif opcao == "5":

            listar_arquivos_datasus()

        elif opcao == "0":

            print("\nEncerrando robô...")
            break

        else:

            print("\nOpção inválida.")


if __name__ == "__main__":
    main()