# Blockchain From Scratch

A simple blockchain simulator built from scratch in Python to explore transactions, blocks, hashing and chain validation and tampering!

## Objective

This project aims to build a simplified blockchain step by step using basic Python concepts.

The project focuses on:

- creating transactions;
- storing pending transactions;
- grouping transactions into blocks;
- storing blocks in a blockchain;
- displaying the blockchain structure;
- linking blocks with SHA-256 hashes (v0.2);
- validating the chain and simulating tampering (v0.3).

A future version will introduce Proof of Work.

## Project Structure

The blockchain is represented as a sequence of blocks:

```text
Block 0
   ↓
Block 1
   ↓
Block 2
   ↓
...
```

Each block stores transactions and the SHA-256 hash of the previous block, which links the blocks together.

## Transactions

Each transaction is represented by a tuple:

```python
("Alice", "Bruno", 10)
```

The structure is:

```text
(sender, receiver, amount)
```

Example:

```text
Alice -> Bruno: 10
Bruno -> Carlos: 5
Carlos -> Diego: 3
```

Pending transactions are stored in a list until a new block is created.

Example:

```python
pending_transactions = [
    ("Alice", "Bruno", 10),
    ("Bruno", "Carlos", 5),
    ("Carlos", "Diego", 3)
]
```

## Blocks

Since v0.2, a block is a tuple:

```text
(index, transactions, previous_hash, block_hash)
```

- `index`: position of the block in the chain, starting at 0;
- `transactions`: a tuple with up to three transactions;
- `previous_hash`: the hash of the previous block (the first block uses 64 zeros);
- `block_hash`: the SHA-256 hash of this block's own content.

The hash is calculated from `index`, `transactions` and `previous_hash`. These values are serialized to compact JSON (`json.dumps` with `separators=(",", ":")` and `ensure_ascii=False`), encoded as UTF-8 and hashed with SHA-256. The result is 64 lowercase hex characters. There is no timestamp, so the same block content always produces the same hash.

The first block (genesis) uses `"0" * 64` as its previous hash. Every later block stores the hash of the block before it.

This is what the program prints for a chain with two blocks (the labels are in Portuguese: "Hash anterior" is the previous hash, "Transações" are the transactions):

```text
BLOCO 0
Hash anterior: 0000000000000000000000000000000000000000000000000000000000000000
Hash: 2773ccc05269072939b298b272c339e4eb3f8b1c9a40930dd758349689f21e12
Transações:
Alice -> Bruno: 10.00
Bruno -> Carlos: 5.00
Carlos -> Diego: 3.00
-------------------------------

BLOCO 1
Hash anterior: 2773ccc05269072939b298b272c339e4eb3f8b1c9a40930dd758349689f21e12
Hash: ef7fd3f04998e2ce59c344d24b25c8202a8ba657589f4d722f55687a7b2a10c5
Transações:
Diego -> Alice: 2.00
-------------------------------
```

## Blockchain

The blockchain itself is stored as a list:

```python
blockchain = [
    block_0,
    block_1,
    block_2
]
```

This allows blocks to be added sequentially while preserving their order.

## How to run

Requirements: Python 3.8 or newer. No external dependencies.

```bash
python main.py
```

Example session (input typed by the user follows each prompt; the program's messages are in Portuguese):

```text
====== MINI BLOCKCHAIN ======
1 - Nova transação
2 - Mostrar transações pendentes
3 - Criar bloco
4 - Mostrar blockchain
5 - Validar blockchain
6 - Simular adulteração
7 - Sair
Digite como deseja navegar pelo menu: 1
Entrando em Nova transação...
Remetente: Alice
Destinatário: Bruno
Valor: 10
Transação adicionada: Alice -> Bruno: 10.00
(menu is shown again)
Digite como deseja navegar pelo menu: 3
Entrando em Criar bloco...
BLOCO 0 criado com sucesso com 1 transações.
(menu is shown again)
Digite como deseja navegar pelo menu: 4
Entrando em Mostrar blockchain...

========== BLOCKCHAIN ==========

BLOCO 0
Hash anterior: 0000000000000000000000000000000000000000000000000000000000000000
Hash: <64-character SHA-256 hash of block 0>
Transações:
Alice -> Bruno: 10.00
-------------------------------
(menu is shown again)
Digite como deseja navegar pelo menu: 5
Entrando em Validar blockchain...
Blockchain válida.
(menu is shown again)
Digite como deseja navegar pelo menu: 7
finalizando...
```

The `Hash` line above is abbreviated on purpose; the program prints the full 64 hex characters (see the example in the Blocks section).

## Running the tests

The tests use the standard library `unittest` module, so nothing needs to be installed:

```bash
python -m unittest -v
```

## Program Menu

The program uses a terminal menu. The program's interface is in Portuguese, so the text below is exactly what it prints:

```text
====== MINI BLOCKCHAIN ======
1 - Nova transação
2 - Mostrar transações pendentes
3 - Criar bloco
4 - Mostrar blockchain
5 - Validar blockchain
6 - Simular adulteração
7 - Sair
Digite como deseja navegar pelo menu:
```

In English: 1 - New transaction, 2 - Show pending transactions, 3 - Create block, 4 - Show blockchain, 5 - Validate blockchain, 6 - Simulate tampering, 7 - Exit.

Any other input (including text that is not a number) prints an "invalid option" message and shows the menu again.

The program remains active until the user chooses to exit.

## Transaction Validation

The initial implementation verifies basic conditions before accepting a transaction:

```text
sender and receiver are trimmed (leading/trailing whitespace is removed)
sender must not be empty
receiver must not be empty
sender must be different from receiver
amount must be a valid number
amount must be finite (inf and nan are rejected)
amount must be greater than zero
```

Invalid transactions are rejected.

## Block Creation

Each block can contain up to three transactions.

Example:

```text
Pending transactions:

T1
T2
T3
T4
T5
```

After creating a block:

```text
Block 0:

T1
T2
T3
```

The remaining pending transactions are:

```text
T4
T5
```

## Concepts Explored

This project applies concepts such as:

- Python;
- lists;
- nested lists;
- tuples;
- indexing;
- loops;
- `for`;
- `while`;
- `break`;
- conditionals;
- input validation;
- `append`;
- `pop`;
- `len`;
- immutable data structures (blocks and transactions as tuples; tampering builds a new chain);
- functions;
- `if __name__ == "__main__"`;
- SHA-256 hashing with `hashlib`;
- JSON serialization with `json`;
- unit tests with `unittest`;
- blockchain fundamentals.

## Development Roadmap

### Version 0.1

- [x] Create terminal menu
- [x] Add transactions
- [x] Store pending transactions
- [x] Display pending transactions
- [x] Create blocks
- [x] Add blocks to the blockchain
- [x] Display the blockchain

### Version 0.2

- [x] Add SHA-256 hashing
- [x] Generate a hash for each block
- [x] Store the previous block hash

### Version 0.3

- [x] Validate the blockchain
- [x] Detect modified blocks
- [x] Simulate blockchain tampering

### Version 0.4

- [ ] Add a simplified Proof of Work
- [ ] Introduce a nonce
- [ ] Define mining difficulty

### Version 1.0

- [ ] Complete educational blockchain simulator
- [ ] Improve output formatting
- [ ] Add more test cases
- [ ] Document the full blockchain flow

## Cryptography

Blocks are hashed with SHA-256 through Python's `hashlib` library.

The simplified idea is:

```text
block data
   ↓
SHA-256
   ↓
cryptographic hash
```

A small change in the block data generates a completely different hash.

## Chain Validation

Each block stores the hash of the previous block, so the blocks are linked.

Conceptually:

```text
Block 0
previous_hash = 000...000
hash = AAA
   ↓
Block 1
previous_hash = AAA
hash = BBB
   ↓
Block 2
previous_hash = BBB
hash = CCC
```

Menu option 5 ("Validar blockchain") checks every block, in order, and reports every problem it finds. For each block it verifies:

```text
index          = position of the block in the chain
block_hash     = SHA-256 of the block's own index, transactions and previous_hash
previous_hash  = hash of the previous block (64 zeros for block 0)
```

The check is implemented by `validate_chain(blockchain)`, which returns a list of messages. An empty list means the chain is valid.

If the chain is empty, the program prints `A blockchain ainda está vazia!!`. In the example below the chain has three blocks and nothing was changed:

```text
Digite como deseja navegar pelo menu: 5
Entrando em Validar blockchain...
Blockchain válida.
```

When something is wrong, each problem is listed ("hash do bloco não confere" means the block's own hash does not match its content; "hash anterior não confere" means the stored previous hash does not match the previous block's hash). A wrong index is reported as "índice incorreto". The next section shows real examples.

## Tampering Simulation

Menu option 6 ("Simular adulteração") plays the role of an attacker. It asks for a block, a transaction inside it and a new amount, and then asks whether the block's hash should be recalculated. The change is applied to the in-memory chain (a new list is built; the original tuples are not modified). Afterwards, use option 5 to validate the chain and see what was detected.

All scenarios below use the same chain, built from these transactions (full hashes are not repeated here):

```text
BLOCO 0: Alice -> Bruno: 10.00, Bruno -> Carlos: 5.00
BLOCO 1: Carlos -> Diego: 3.00
BLOCO 2: Diego -> Alice: 2.00
```

The outputs below are real, captured from the program (the menu that is printed between steps is omitted).

### Scenario 1: change without recalculating the hash

The attacker changes the amount of the second transaction in block 0 to 500 and does not recalculate the hash:

```text
Digite como deseja navegar pelo menu: 6
Entrando em Simular adulteração...
Número do bloco: 0
1 - Alice -> Bruno: 10.00
2 - Bruno -> Carlos: 5.00
Número da transação: 1
Novo valor: 500
Recalcular o hash do bloco? (s/n): n
Bloco 0 adulterado. Use a opção 5 para validar a blockchain.
(menu is shown again)
Digite como deseja navegar pelo menu: 5
Entrando em Validar blockchain...
Blockchain inválida! Problemas encontrados:
- Bloco 0: hash do bloco não confere.
```

The stored hash no longer matches the changed content, so block 0 fails its own hash check.

### Scenario 2: change and recalculate the hash

Now the attacker makes the same change and also recalculates the hash of block 0 (answer `s`):

```text
Digite como deseja navegar pelo menu: 6
Entrando em Simular adulteração...
Número do bloco: 0
1 - Alice -> Bruno: 10.00
2 - Bruno -> Carlos: 5.00
Número da transação: 1
Novo valor: 500
Recalcular o hash do bloco? (s/n): s
Bloco 0 adulterado. Use a opção 5 para validar a blockchain.
(menu is shown again)
Digite como deseja navegar pelo menu: 5
Entrando em Validar blockchain...
Blockchain inválida! Problemas encontrados:
- Bloco 1: hash anterior não confere.
```

Block 0 is now consistent with its own (new) hash, but block 1 still stores the old hash of block 0 as its previous hash, so the link is broken.

### Scenario 3: recalculating every following block (explained only)

The program does not simulate this case. An attacker who changes block 0, recalculates its hash, then updates the previous hash of block 1 and recalculates block 1, and so on up to the last block, produces a chain that passes every check, because all hashes and links are consistent again. In this version, validation therefore proves that the chain is internally consistent, not that it is the original one. Making that rewrite expensive is the goal of Proof of Work, planned for v0.4 (it is not implemented yet).

## Proof of Work

A future version will introduce a simplified mining mechanism.

The program will search for a `nonce` such that the generated hash satisfies a difficulty condition.

Example:

```text
0000af83...
```

Conceptually:

```text
nonce = 0

repeat:
    calculate hash
    increase nonce

until hash satisfies difficulty
```

This will provide a simplified introduction to Proof of Work.

## Technologies

Current version:

- Python
- `hashlib` (SHA-256)
- `json` (deterministic block serialization)
- `unittest` (tests)

## Status

Project under development. Version 0.3 is complete: every block has a SHA-256 hash and stores the hash of the previous block, the chain can be validated, and tampering can be simulated and detected. Proof of Work is the next step (v0.4).

Current focus:

```text
transactions
    ↓
pending transactions
    ↓
blocks
    ↓
hashed, linked blocks
    ↓
chain validation and tampering simulation
    ↓
Proof of Work (next, v0.4)
```
