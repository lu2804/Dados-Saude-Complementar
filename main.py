from robos.robo_siab import baixar_siab
from robos.robo_diarreia import baixar_diarreia
from robos.robo_imunizacao import baixar_imunizacao

print("===================================")
print(" ROBÔ DE DADOS DO DATASUS")
print("===================================")

while True:
    print("\nEscolha uma opção:")
    print("1 - Baixar dados SIAB")
    print("2 - Baixar dados de Diarreia")
    print("3 - Baixar dados de Imunização")
    print("0 - Sair")

    opcao = input("Digite a opção: ")

    if opcao == "1":
        baixar_siab()

    elif opcao == "2":
        baixar_diarreia()

    elif opcao == "3":
        baixar_imunizacao()

    elif opcao == "0":
        print("Encerrando robô...")
        break

    else:
        print("Opção inválida.")