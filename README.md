# Blockchain From Scratch

A simple blockchain simulator built from scratch in Python to explore transactions, blocks, hashing and chain validation!

## Objective

This project aims to build a simplified blockchain step by step using basic Python concepts.

The initial version focuses on:

- creating transactions;
- storing pending transactions;
- grouping transactions into blocks;
- storing blocks in a blockchain;
- displaying the blockchain structure.

Future versions will introduce hashing, chain validation and Proof of Work.

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

Each block stores transactions and a reference to the previous block.

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

In the initial version, a block contains:

```text
index
transactions
previous block reference
```

Conceptually:

```text
BLOCK #0

Previous reference: GENESIS

Transactions:
Alice -> Bruno: 10
Bruno -> Carlos: 5
Carlos -> Diego: 3
```

The first block uses `GENESIS` as its previous reference.

Future versions will replace this reference with the cryptographic hash of the previous block.

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
5 - Sair
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
Referência anterior: GENESIS
Transações:
Alice -> Bruno: 10.00
-------------------------------
(menu is shown again)
Digite como deseja navegar pelo menu: 5
finalizando...
```

## Program Menu

The initial version uses a terminal menu. The program's interface is in Portuguese, so the text below is exactly what it prints:

```text
====== MINI BLOCKCHAIN ======
1 - Nova transação
2 - Mostrar transações pendentes
3 - Criar bloco
4 - Mostrar blockchain
5 - Sair
Digite como deseja navegar pelo menu:
```

In English: 1 - New transaction, 2 - Show pending transactions, 3 - Create block, 4 - Show blockchain, 5 - Exit.

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
- immutable data structures;
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

- [ ] Add SHA-256 hashing
- [ ] Generate a hash for each block
- [ ] Store the previous block hash

### Version 0.3

- [ ] Validate the blockchain
- [ ] Detect modified blocks
- [ ] Simulate blockchain tampering

### Version 0.4

- [ ] Add a simplified Proof of Work
- [ ] Introduce a nonce
- [ ] Define mining difficulty

### Version 1.0

- [ ] Complete educational blockchain simulator
- [ ] Improve output formatting
- [ ] Add more test cases
- [ ] Document the full blockchain flow

## Future Cryptography

The project will later use SHA-256 through Python's `hashlib` library.

The simplified idea is:

```text
block data
   ↓
SHA-256
   ↓
cryptographic hash
```

A small change in the block data should generate a different hash.

## Chain Validation

Each block will eventually store the hash of the previous block.

Conceptually:

```text
Block 0
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

A valid blockchain must satisfy:

```text
previous_hash(Block i) = hash(Block i - 1)
```

for every block after the genesis block.

This mechanism will allow the program to detect modifications in previous blocks.

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

Future additions:

- `hashlib`

## Status

Project under development.

Current focus:

```text
transactions
    ↓
pending transactions
    ↓
blocks
    ↓
blockchain
```

The cryptographic layer will be added after the basic data structure is working correctly.
