######### BLOCKCHAIN FROM SCRATCH #########
import hashlib
import json
import math
import time

MAX_TRANSACTIONS_PER_BLOCK = 3
GENESIS_PREVIOUS_HASH = "0" * 64
DEFAULT_DIFFICULTY = 4
MAX_DIFFICULTY = 5

def calculate_block_hash(index, transactions, previous_hash, nonce):
    """Return the SHA-256 hash (64 hex characters) of a block's content."""
    content = json.dumps(
        [index, [list(t) for t in transactions], previous_hash, nonce],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def mine_block(index, transactions, previous_hash, difficulty):
    """Return (nonce, block_hash) for the first nonce that meets the difficulty.

    Nonces are tried in order starting at 0. The number of attempts is nonce + 1.
    """
    nonce = 0
    target = "0" * difficulty
    while True:
        block_hash = calculate_block_hash(index, transactions, previous_hash, nonce)
        if block_hash.startswith(target):
            return nonce, block_hash
        nonce += 1


def create_block(blockchain, transactions, difficulty):
    """Return a new block (index, transactions, previous_hash, nonce, block_hash).

    The blockchain list is only read, never changed; the caller appends.
    """
    index = len(blockchain)
    if blockchain == []:
        previous_hash = GENESIS_PREVIOUS_HASH
    else:
        previous_hash = blockchain[-1][4]
    block_transactions = tuple(transactions)
    nonce, block_hash = mine_block(
        index, block_transactions, previous_hash, difficulty)
    return (index, block_transactions, previous_hash, nonce, block_hash)


def validate_chain(blockchain, difficulty):
    """Return a list of problem messages (Portuguese); empty means valid."""
    problems = []
    for position, block in enumerate(blockchain):
        index, transactions, previous_hash, nonce, block_hash = block
        if index != position:
            problems.append(
                f"Bloco {position}: índice incorreto "
                f"(esperado {position}, encontrado {index})."
            )
        if block_hash != calculate_block_hash(index, transactions, previous_hash, nonce):
            problems.append(f"Bloco {position}: hash do bloco não confere.")
        if not block_hash.startswith("0" * difficulty):
            problems.append(
                f"Bloco {position}: hash não atende à dificuldade "
                f"(esperado {difficulty} zeros no início)."
            )
        if position == 0:
            expected_previous = GENESIS_PREVIOUS_HASH
        else:
            expected_previous = blockchain[position - 1][4]
        if previous_hash != expected_previous:
            problems.append(f"Bloco {position}: hash anterior não confere.")
    return problems


def tamper_block(blockchain, block_position, transaction_position,
                 new_amount, recalculate_hash):
    """Return a NEW chain with one transaction amount changed.

    Simulates an attacker, so any finite amount is accepted. The input list
    and its tuples are never modified. Positions must already be valid.
    """
    index, transactions, previous_hash, nonce, block_hash = blockchain[block_position]
    sender, receiver, _ = transactions[transaction_position]
    new_transactions = list(transactions)
    new_transactions[transaction_position] = (sender, receiver, float(new_amount))
    new_transactions = tuple(new_transactions)
    if recalculate_hash:
        block_hash = calculate_block_hash(index, new_transactions, previous_hash, nonce)
    result = list(blockchain)
    result[block_position] = (index, new_transactions, previous_hash, nonce, block_hash)
    return result


TITLE_LINE = "=" * 40


def print_title(text):
    """Print a centered title framed by TITLE_LINE."""
    print("")
    print(TITLE_LINE)
    print(text)
    print(TITLE_LINE)


def print_field(label, value):
    """Print a label/value pair with aligned labels."""
    print(f"{label:<13} : {value}")


def print_error(text):
    """Print an error message with the standard prefix."""
    print(f"Erro: {text}")


def format_transaction(transaction):
    """Return a formatted string for a transaction tuple."""
    sender, receiver, amount = transaction
    return f"{sender} -> {receiver}: {amount:.2f}"


def transactions_word(count):
    """Return the correct Portuguese word for the number of transactions."""
    if count == 1:
        return "transação"
    return "transações"


def menu_new_transaction(state):
    """Option 1: read a transaction and add it to the pending list."""
    pending_transactions, blockchain, difficulty = state
    print("Entrando em Nova transação...")
    sender = input("Remetente: ").strip()
    receiver = input("Destinatário: ").strip()
    raw_amount = input("Valor: ")
    try:
        amount = float(raw_amount)
    except ValueError:
        print("Valor inválido. Digite um número.")
        return state

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
    return (pending_transactions, blockchain, difficulty)


def menu_show_pending(state):
    """Option 2: show the transactions waiting for a block."""
    pending_transactions, blockchain, difficulty = state
    print("Entrando em Mostrar transações pendentes...")
    if len(pending_transactions) == 0:
        print("Não há transações pendentes.")
    else:
        print("As transações pendentes são: ")
        for transaction in pending_transactions:
            print(transaction)
    return state


def menu_create_block(state):
    """Option 3: mine a block with the oldest pending transactions."""
    pending_transactions, blockchain, difficulty = state
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

        print(f"Minerando bloco com dificuldade {difficulty}...")
        start = time.perf_counter()
        block = create_block(
            blockchain, block_transactions, difficulty)
        elapsed = time.perf_counter() - start
        nonce = block[3]

        blockchain.append(block)

        print(
            f"BLOCO {len(blockchain) - 1} criado com sucesso "
            f"com {len(block_transactions)} transações."
        )
        print(
            f"Nonce encontrado: {nonce} "
            f"({nonce + 1} tentativas em {elapsed:.2f} s)."
        )
    return (pending_transactions, blockchain, difficulty)


def menu_show_blockchain(state):
    """Option 4: show every block of the chain."""
    pending_transactions, blockchain, difficulty = state
    print("Entrando em Mostrar blockchain...")
    if blockchain == []:
        print("A blockchain ainda está vazia!!")
    else:
        print("\n========== BLOCKCHAIN ==========")
        print(
            f"Dificuldade: {difficulty} "
            f"(o hash deve começar com {difficulty} zeros)"
        )
        for block in blockchain:
            print(f"\nBLOCO {block[0]}")
            print(f"Hash anterior: {block[2]}")
            print(f"Nonce: {block[3]}")
            print(f"Hash: {block[4]}")
            print("Transações:")

            for transaction in block[1]:
                print(
                    f"{transaction[0]} -> "
                    f"{transaction[1]}: "
                    f"{transaction[2]:.2f}"
                )

            print("-------------------------------")
    return state


def menu_validate(state):
    """Option 5: validate the chain and list the problems found."""
    pending_transactions, blockchain, difficulty = state
    print("Entrando em Validar blockchain...")
    if blockchain == []:
        print("A blockchain ainda está vazia!!")
    else:
        problems = validate_chain(blockchain, difficulty)
        if problems == []:
            print("Blockchain válida.")
        else:
            print("Blockchain inválida! Problemas encontrados:")
            for problem in problems:
                print(f"- {problem}")
    return state


def menu_tamper(state):
    """Option 6: change a transaction amount of a block."""
    pending_transactions, blockchain, difficulty = state
    print("Entrando em Simular adulteração...")
    if blockchain == []:
        print("A blockchain ainda está vazia!!")
        return state

    try:
        block_position = int(input("Número do bloco: "))
    except ValueError:
        print("Bloco inválido.")
        return state
    if block_position < 0 or block_position >= len(blockchain):
        print("Bloco inválido.")
        return state

    for number, transaction in enumerate(blockchain[block_position][1], start=1):
        print(
            f"{number} - {transaction[0]} -> "
            f"{transaction[1]}: {transaction[2]:.2f}"
        )

    try:
        transaction_number = int(input("Número da transação: "))
    except ValueError:
        print("Transação inválida.")
        return state
    if (transaction_number < 1
            or transaction_number > len(blockchain[block_position][1])):
        print("Transação inválida.")
        return state

    try:
        new_amount = float(input("Novo valor: "))
    except ValueError:
        print("Valor inválido. Digite um número.")
        return state
    if not math.isfinite(new_amount):
        print("Valor inválido. Digite um número.")
        return state

    answer = input("Recalcular o hash do bloco? (s/n): ")
    recalculate_hash = answer.strip().lower() == "s"

    blockchain = tamper_block(
        blockchain, block_position, transaction_number - 1,
        new_amount, recalculate_hash,
    )
    print(
        f"Bloco {block_position} adulterado. "
        f"Use a opção 5 para validar a blockchain."
    )
    return (pending_transactions, blockchain, difficulty)


def menu_change_difficulty(state):
    """Option 7: change the difficulty (only while the chain is empty)."""
    pending_transactions, blockchain, difficulty = state
    print("Entrando em Alterar dificuldade...")
    if blockchain != []:
        print(
            "A dificuldade só pode ser alterada com a blockchain vazia."
        )
        return state
    print(f"Dificuldade atual: {difficulty}")
    raw_difficulty = input(
        f"Nova dificuldade (0 a {MAX_DIFFICULTY}): ")
    try:
        new_difficulty = int(raw_difficulty)
    except ValueError:
        new_difficulty = None
    if new_difficulty is None or not 0 <= new_difficulty <= MAX_DIFFICULTY:
        print(
            f"Dificuldade inválida. Digite um número entre 0 e "
            f"{MAX_DIFFICULTY}."
        )
        return state
    print(f"Dificuldade alterada para {new_difficulty}.")
    return (pending_transactions, blockchain, new_difficulty)


# Menu: (text, function). Numbered automatically; "Sair" is always the last one.
MENU = [
    ("Nova transação", menu_new_transaction),
    ("Mostrar transações pendentes", menu_show_pending),
    ("Criar bloco", menu_create_block),
    ("Mostrar blockchain", menu_show_blockchain),
    ("Validar blockchain", menu_validate),
    ("Simular adulteração", menu_tamper),
    ("Alterar dificuldade", menu_change_difficulty),
]
EXIT_OPTION = len(MENU) + 1


def main():
    # state = (pending transactions, blockchain, difficulty)
    state = ([], [], DEFAULT_DIFFICULTY)

    try:
        while True:
            # Navigation menu
            print("====== MINI BLOCKCHAIN ======")
            for number, (text, _) in enumerate(MENU, start=1):
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
            elif 1 <= choice < EXIT_OPTION:
                state = MENU[choice - 1][1](state)
            else:      # Invalid option
                print(f"Opção inválida. Digite um número entre 1 e {EXIT_OPTION}.")
    except (KeyboardInterrupt, EOFError):
        print("\nfinalizando...")


if __name__ == "__main__":
    main()
