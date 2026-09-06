######### BLOCKCHAIN FROM SCRATCH #########

lista_menu = [      # Opções do menu
    "Nova transação", 
    "Mostrar transações pendentes",
    "Criar bloco", 
    "Mostrar blockchain"]
transacoes_pendentes = []       # ainda não entraram em bloco
blockchain = []     #blocos já registrados

while True:
    # Menu de navegação
    print( "====== MINI BLOCKCHAIN ====== \n" 

    "1 - Nova transação \n"
    "2 - Mostrar transações pendentes \n"
    "3 - Criar bloco \n"
    "4 - Mostrar blockchain \n"
    "5 - Sair")
                    
    menu = int(input("Digite como deseja navegar pelo menu: "))
    
    if menu == 5:       # Encerrar programa
        print("finalizando...")
        break
    elif menu == 1:     
        print("Entrando em Nova transação...")
        # bloco de nova transação
        if menu == 1:
            remetente = input("Remetente: ")
            destinatario = input("Destinatário: ")
            valor = float(input("Valor: "))
            if remetente == "" or destinatario == "":
                print("Remetente e destinatário não podem estar vazios.")

            elif remetente == destinatario:
                print("Remetente e destinatário não podem ser iguais.")

            elif valor <= 0:
                print("O valor da transação deve ser maior que zero.")

            else: 
                transacao = (remetente, destinatario, valor)
                transacoes_pendentes.append(transacao)
                print(
                        f"Transação adicionada: "
                        f"{remetente} -> {destinatario}: {valor:.2f}"
                    )
    elif menu == 2:
        print("Entrando em Mostrar transações pendentes...")
        if len(transacoes_pendentes) == 0:
            print("Não há transações pendentes.")
        else:
            print(f"As transações pendentes são: ")
            for x in transacoes_pendentes:
                print(x)
    elif menu == 3:
        print("Entrando em Criar bloco...")

        if len(transacoes_pendentes) == 0:
            print("Não há transações pendentes para criar um bloco.")

        else:
            transacoes_bloco = []

            while len(transacoes_bloco) < 3 and len(transacoes_pendentes) > 0:
                transacao = transacoes_pendentes.pop(0)
                transacoes_bloco.append(transacao)

            if blockchain == []:
                referencia_anterior = "GENESIS"
            else:
                referencia_anterior = f"BLOCO {len(blockchain) - 1}"

            bloco = (
                len(blockchain),
                tuple(transacoes_bloco),
                referencia_anterior
            )

            blockchain.append(bloco)

            print(
                f"BLOCO {len(blockchain) - 1} criado com sucesso "
                f"com {len(transacoes_bloco)} transações."
            )
    elif menu == 4:
        print("Entrando em Mostrar blockchain...") 
        if blockchain == []:
            print("A blockchain ainda está vazia!!")
        else:
            print("\n========== BLOCKCHAIN ==========")
            for bloco in blockchain:
                print(f"\nBLOCO {bloco[0]}")
                print(f"Referência anterior: {bloco[2]}")
                print("Transações:")
                
                for transacao in bloco[1]:
                    print(
                        f"{transacao[0]} -> "
                        f"{transacao[1]}: "
                        f"{transacao[2]:.2f}"
                    )

                print("-------------------------------")
    else:       # Opção inválida
        print("Opção inválida. Digite um número entre 1 e 5.")
