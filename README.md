# Blockchain From Scratch

A simple blockchain simulator built from scratch in Python to explore transactions, blocks, hashing and chain validation!

## Objective

This project aims to build a simplified blockchain step by step using basic Python concepts.

The project focuses on:

- creating transactions;
- storing pending transactions;
- grouping transactions into blocks;
- storing blocks in a blockchain;
- displaying the blockchain structure;
- linking blocks with SHA-256 hashes (v0.2).

Future versions will introduce chain validation and Proof of Work.

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
Hash anterior: 0000000000000000000000000000000000000000000000000000000000000000
Hash: <64-character SHA-256 hash of block 0>
Transações:
Alice -> Bruno: 10.00
-------------------------------
(menu is shown again)
Digite como deseja navegar pelo menu: 5
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

Each block stores the hash of the previous block, so the blocks are already linked.

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

A valid blockchain must satisfy:

```text
previous_hash(Block i) = hash(Block i - 1)
```

for every block after the genesis block.

The program does not check this yet. Validating the chain and detecting modified blocks is planned for v0.3.

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

Project under development. Version 0.2 is complete: every block now has a SHA-256 hash and stores the hash of the previous block.

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
chain validation (next, v0.3)
```
