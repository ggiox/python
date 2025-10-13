# Programa principal que exibe um menu para o usuário escolher entre 
# ver a versão do Python ou listar os pacotes instalados.

import sys
import subprocess

def mostrar_versao_python():
    """Exibe a versão atual do Python."""
    print(f"\nVersão do Python: \n\n{sys.version}\n")

def listar_pacotes_instalados():
    """Lista todos os pacotes Python instalados."""
    print("\nPacotes instalados:\n")
    subprocess.run(["pip", "list"])
    print()  # linha em branco no final

def menu_principal():
    """Exibe o menu e gerencia as escolhas do usuário."""
    while True:
        print("=== MENU PRINCIPAL ===")
        print("1 - Exibir versão do Python")
        print("2 - Listar pacotes instalados")
        print("0 - Sair")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            mostrar_versao_python()
        elif opcao == "2":
            listar_pacotes_instalados()
        elif opcao == "0":
            print("\nSaindo... até logo!")
            break
        else:
            print("\nOpção inválida. Tente novamente.\n")

if __name__ == "__main__":
    menu_principal()
