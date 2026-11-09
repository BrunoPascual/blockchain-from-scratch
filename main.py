######### BLOCKCHAIN FROM SCRATCH #########
import hashlib
import json
import math

MAX_TRANSACTIONS_PER_BLOCK = 3
GENESIS_PREVIOUS_HASH = "0" * 64

# Menu options (numbered automatically; "Sair" is always the last one)
MENU_OPTIONS = [
    "Nova transação",
    "Mostrar transações pendentes",
    "Criar bloco",
    "Mostrar blockchain",
]
EXIT_OPTION = len(MENU_OPTIONS) + 1


def calculate_block_hash(index, transactions, previous_hash):
    """Return the SHA-256 hash (64 hex characters) of a block's content."""
    content = json.dumps(
        [index, [list(t) for t in transactions], previous_hash],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def main():
    pending_transactions = []       # not yet included in a block
    blockchain = []                 # blocks already registered

    try:
        while True:
            # Navigation menu
            print("====== MINI BLOCKCHAIN ======")
            for number, text in enumerate(MENU_OPTIONS, start=1):
                print(f"{number} - {text}")
            print(f"{EXIT_OPTION} - Sair")

            raw_choice = input("Digite como deseja navegar pelo menu: ")
            try:
                choice = int(raw_choice)
            except ValueError:
                print(f"Opção inválida. Digite um número entre 1 e {EXIT_OPTION}.")
                continue

            if choice == EXIT_OPTION:       # Quit program
                print("finalizando...")
                break
            elif choice == 1:
                print("Entrando em Nova transação...")
                sender = input("Remetente: ").strip()
                receiver = input("Destinatário: ").strip()
                raw_amount = input("Valor: ")
                try:
                    amount = float(raw_amount)
                except ValueError:
                    print("Valor inválido. Digite um número.")
                    continue

                if sender == "" or receiver == "":
                    print("Remetente e destinatário não podem estar vazios.")

                elif sender == receiver:
                    print("Remetente e destinatário não podem ser iguais.")

                elif not math.isfinite(amount):
                    print("Valor inválido. Digite um número.")

                elif amount <= 0:
                    print("O valor da transação deve ser maior que zero.")

                else:
                    transaction = (sender, receiver, amount)
                    pending_transactions.append(transaction)
                    print(
                        f"Transação adicionada: "
                        f"{sender} -> {receiver}: {amount:.2f}"
                    )
            elif choice == 2:
                print("Entrando em Mostrar transações pendentes...")
                if len(pending_transactions) == 0:
                    print("Não há transações pendentes.")
                else:
                    print("As transações pendentes são: ")
                    for transaction in pending_transactions:
                        print(transaction)
            elif choice == 3:
                print("Entrando em Criar bloco...")

                if len(pending_transactions) == 0:
                    print("Não há transações pendentes para criar um bloco.")

                else:
                    block_transactions = []

                    while (
                        len(block_transactions) < MAX_TRANSACTIONS_PER_BLOCK
                        and len(pending_transactions) > 0
                    ):
                        transaction = pending_transactions.pop(0)
                        block_transactions.append(transaction)

                    if blockchain == []:
                        previous_reference = "GENESIS"
                    else:
                        previous_reference = f"BLOCO {len(blockchain) - 1}"

                    block = (
                        len(blockchain),
                        tuple(block_transactions),
                        previous_reference
                    )

                    blockchain.append(block)

                    print(
                        f"BLOCO {len(blockchain) - 1} criado com sucesso "
                        f"com {len(block_transactions)} transações."
                    )
            elif choice == 4:
                print("Entrando em Mostrar blockchain...")
                if blockchain == []:
                    print("A blockchain ainda está vazia!!")
                else:
                    print("\n========== BLOCKCHAIN ==========")
                    for block in blockchain:
                        print(f"\nBLOCO {block[0]}")
                        print(f"Referência anterior: {block[2]}")
                        print("Transações:")

                        for transaction in block[1]:
                            print(
                                f"{transaction[0]} -> "
                                f"{transaction[1]}: "
                                f"{transaction[2]:.2f}"
                            )

                        print("-------------------------------")
            else:       # Invalid option
                print(f"Opção inválida. Digite um número entre 1 e {EXIT_OPTION}.")
    except (KeyboardInterrupt, EOFError):
        print("\nfinalizando...")


if __name__ == "__main__":
    main()
