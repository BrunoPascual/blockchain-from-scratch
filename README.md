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
- linking blocks with SHA-256 hashes (v0.2);
- validating the chain and simulating tampering (v0.3);
- mining blocks with a simplified Proof of Work and a configurable difficulty (v0.4).

The next version (v1.0) will polish the simulator into a complete educational blockchain.

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

Each block stores transactions, the SHA-256 hash of the previous block (which links the blocks together) and a nonce found by mining.

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

Since v0.4, a block is a tuple:

```text
(index, transactions, previous_hash, nonce, block_hash)
```

- `index`: position of the block in the chain, starting at 0;
- `transactions`: a tuple with up to three transactions;
- `previous_hash`: the hash of the previous block (the first block uses 64 zeros);
- `nonce`: the number found by mining (see Proof of Work);
- `block_hash`: the SHA-256 hash of this block's own content, which must start with the required number of zeros.

The hash is calculated from `index`, `transactions`, `previous_hash` and `nonce`. These values are serialized to compact JSON (`json.dumps` with `separators=(",", ":")` and `ensure_ascii=False`), encoded as UTF-8 and hashed with SHA-256. The result is 64 lowercase hex characters. There is no timestamp, so the same block content (including the nonce) always produces the same hash, and mining the same block twice finds the same nonce.

The first block (genesis) uses `"0" * 64` as its previous hash. Every later block stores the hash of the block before it.

This is what the program prints (option 4) for a chain with two blocks, mined at the default difficulty of 4 (the labels are in Portuguese: "Dificuldade" is the difficulty, "Hash anterior" is the previous hash, "Transações" are the transactions):

```text
========== BLOCKCHAIN ==========
Dificuldade: 4 (o hash deve começar com 4 zeros)

BLOCO 0
Hash anterior: 0000000000000000000000000000000000000000000000000000000000000000
Nonce: 35429
Hash: 0000edcb1910bfd98b532dc1b8326036b72454cb04310a9a4e7684e26dbbcaf8
Transações:
Alice -> Bruno: 10.00
Bruno -> Carlos: 5.00
-------------------------------

BLOCO 1
Hash anterior: 0000edcb1910bfd98b532dc1b8326036b72454cb04310a9a4e7684e26dbbcaf8
Nonce: 125866
Hash: 00007cbaf9645a4eece150dad6b37903720cc8ad320e9602562dca391becf575
Transações:
Carlos -> Diego: 3.00
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
7 - Alterar dificuldade
8 - Sair
Digite como deseja navegar pelo menu: 1
Entrando em Nova transação...
Remetente: Alice
Destinatário: Bruno
Valor: 10
Transação adicionada: Alice -> Bruno: 10.00
(menu is shown again)
Digite como deseja navegar pelo menu: 3
Entrando em Criar bloco...
Minerando bloco com dificuldade 4...
BLOCO 0 criado com sucesso com 1 transações.
Nonce encontrado: 120317 (120318 tentativas em 0.45 s).
(menu is shown again)
Digite como deseja navegar pelo menu: 4
Entrando em Mostrar blockchain...

========== BLOCKCHAIN ==========
Dificuldade: 4 (o hash deve começar com 4 zeros)

BLOCO 0
Hash anterior: 0000000000000000000000000000000000000000000000000000000000000000
Nonce: 120317
Hash: 0000d0bd363c482ba514c5fb5f5e59f757dbd999774c2cf5ff34a41933c0b0ff
Transações:
Alice -> Bruno: 10.00
-------------------------------
(menu is shown again)
Digite como deseja navegar pelo menu: 5
Entrando em Validar blockchain...
Blockchain válida.
(menu is shown again)
Digite como deseja navegar pelo menu: 7
Entrando em Alterar dificuldade...
A dificuldade só pode ser alterada com a blockchain vazia.
(menu is shown again)
Digite como deseja navegar pelo menu: 8
finalizando...
```

The elapsed time (0.45 s here) depends on the computer and changes from run to run; the nonce and the hash do not, because the same block content always gives the same result.

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
7 - Alterar dificuldade
8 - Sair
Digite como deseja navegar pelo menu:
```

In English: 1 - New transaction, 2 - Show pending transactions, 3 - Create block (mines it), 4 - Show blockchain, 5 - Validate blockchain, 6 - Simulate tampering, 7 - Change difficulty, 8 - Exit.

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

Creating a block also mines it (see Proof of Work).

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
- measuring elapsed time with `time`;
- Proof of Work: a nonce and a mining difficulty;
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

- [x] Add a simplified Proof of Work
- [x] Introduce a nonce
- [x] Define mining difficulty

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
block_hash     = SHA-256 of the block's own index, transactions, previous_hash and nonce
difficulty     = block_hash starts with the required number of zeros (4 by default)
previous_hash  = hash of the previous block (64 zeros for block 0)
```

The check is implemented by `validate_chain(blockchain, difficulty)`, which returns a list of messages. An empty list means the chain is valid.

If the chain is empty, the program prints `A blockchain ainda está vazia!!`. In the example below the chain has three blocks and nothing was changed:

```text
Digite como deseja navegar pelo menu: 5
Entrando em Validar blockchain...
Blockchain válida.
```

When something is wrong, each problem is listed ("hash do bloco não confere" means the block's own hash does not match its content; "hash anterior não confere" means the stored previous hash does not match the previous block's hash). A wrong index is reported as "índice incorreto". A hash that does not start with enough zeros is reported as "hash não atende à dificuldade" (the hash does not meet the difficulty). The next section shows real examples.

## Tampering Simulation

Menu option 6 ("Simular adulteração") plays the role of an attacker. It asks for a block, a transaction inside it and a new amount, and then asks whether the block's hash should be recalculated (recalculating reuses the block's old nonce; it does not mine again). The change is applied to the in-memory chain (a new list is built; the original tuples are not modified). Afterwards, use option 5 to validate the chain and see what was detected.

All scenarios below use the same chain, mined at the default difficulty of 4 and built from these transactions (full hashes are not repeated here):

```text
BLOCO 0: Alice -> Bruno: 10.00, Bruno -> Carlos: 5.00
BLOCO 1: Carlos -> Diego: 3.00
BLOCO 2: Diego -> Alice: 2.00
```

The outputs below are real, captured from the program (the menu that is printed between steps is omitted).

### Scenario 1: change without recalculating the hash

The attacker changes the amount of the first transaction in block 0 (Alice -> Bruno) to 500 and does not recalculate the hash:

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
- Bloco 0: hash não atende à dificuldade (esperado 4 zeros no início).
- Bloco 1: hash anterior não confere.
```

Two things are detected now. The recalculated hash of block 0 is consistent with its content, but it almost certainly does not start with four zeros, because the old nonce no longer fits the changed content (a random hash starts with four zeros only about 1 time in 65,536). And block 1 still stores the old hash of block 0 as its previous hash, so the link is broken.

Before v0.4, recalculating the hash of the last block was enough to hide the change, because no later block stores its hash. Now even that fails the difficulty check, unless the attacker mines a new nonce, which is what Scenario 3 describes.

### Scenario 3: mining every following block (explained only)

The program does not simulate this case. To make a changed chain pass every check, the attacker has to change block 0, mine a new nonce for it, update the previous hash of block 1 and mine block 1 again, and so on up to the last block. Every block from the changed one to the end must be mined again, because each of them stores a hash that depends on the block before it.

Mining is the expensive part. For the chain used in these scenarios, option 3 printed these real outputs at difficulty 4:

```text
Minerando bloco com dificuldade 4...
BLOCO 0 criado com sucesso com 2 transações.
Nonce encontrado: 35429 (35430 tentativas em 0.21 s).
(menu is shown again)
Minerando bloco com dificuldade 4...
BLOCO 1 criado com sucesso com 1 transações.
Nonce encontrado: 125866 (125867 tentativas em 0.60 s).
(menu is shown again)
Minerando bloco com dificuldade 4...
BLOCO 2 criado com sucesso com 1 transações.
Nonce encontrado: 48957 (48958 tentativas em 0.22 s).
```

That is 210,255 attempts in total. An attacker who changes block 0 must do this work again for all three blocks (about 210,000 hash calculations or more, since the new nonces will be different), and one who changes block 1 must redo blocks 1 and 2. On average, difficulty 4 needs about 65,536 attempts per block (16 to the power of 4); this is an estimate, and a single block can take much less or much more, as the counts above show. Honest users pay this cost once per block, while an attacker pays it again for every block they want to rewrite. In a real network the attacker would also have to keep up with the other miners that keep adding blocks, which this simulator does not model.

## Proof of Work

Version 0.4 introduces a simplified mining mechanism.

The program searches for a `nonce` such that the generated hash satisfies a difficulty condition.

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

This provides a simplified introduction to Proof of Work.

### How it works in v0.4

Proof of Work is now implemented. When a block is created (menu option 3), the program mines it: `mine_block` tries `nonce = 0, 1, 2, ...`, hashes the block content together with the nonce, and stops at the first hash that starts with the required number of zeros. The number of attempts is `nonce + 1`. The hash is then stored in the block together with the nonce that produced it.

The difficulty is the number of zeros the hash must start with (in hex digits). The default is 4, so a valid hash looks like `0000edcb...`. Validation (option 5) recalculates every hash and also checks that it meets the difficulty, so anyone can verify a block with one hash calculation, while finding the nonce takes many attempts.

Real output of option 3 at the default difficulty (the menu is omitted):

```text
Digite como deseja navegar pelo menu: 3
Entrando em Criar bloco...
Minerando bloco com dificuldade 4...
BLOCO 0 criado com sucesso com 2 transações.
Nonce encontrado: 35429 (35430 tentativas em 0.15 s).
```

("Minerando bloco" means mining the block, "Nonce encontrado" means nonce found, "tentativas" means attempts.) The time depends on the computer and differs from run to run.

### Changing the difficulty

Menu option 7 ("Alterar dificuldade") sets the difficulty to a number from 0 to 5. It only works while the blockchain is empty, so every block in the chain always has the same difficulty. Difficulty 0 means no Proof of Work: the first nonce (0) is always accepted. Real output, changing the difficulty to 2 on an empty chain, mining a block, and then trying to change it again:

```text
Digite como deseja navegar pelo menu: 7
Entrando em Alterar dificuldade...
Dificuldade atual: 4
Nova dificuldade (0 a 5): 2
Dificuldade alterada para 2.
(menu is shown again)
Digite como deseja navegar pelo menu: 1
Entrando em Nova transação...
Remetente: Alice
Destinatário: Bruno
Valor: 10
Transação adicionada: Alice -> Bruno: 10.00
(menu is shown again)
Digite como deseja navegar pelo menu: 3
Entrando em Criar bloco...
Minerando bloco com dificuldade 2...
BLOCO 0 criado com sucesso com 1 transações.
Nonce encontrado: 126 (127 tentativas em 0.00 s).
(menu is shown again)
Digite como deseja navegar pelo menu: 7
Entrando em Alterar dificuldade...
A dificuldade só pode ser alterada com a blockchain vazia.
```

### How the work grows

Each hex digit has 16 possible values, so a random hash starts with N zeros with probability 1 in 16^N. On average, mining needs about 16^N attempts: roughly 256 for N = 2, 4,096 for N = 3 and 65,536 for N = 4. These are averages (estimates); the real count of one block is random. Every extra zero makes mining about 16 times slower on average, but checking a block still takes one hash. That is why the maximum difficulty is limited to 5 in this simulator.

## Technologies

Current version:

- Python
- `hashlib` (SHA-256)
- `json` (deterministic block serialization)
- `time` (measuring mining time)
- `unittest` (tests)

## Status

Project under development. Version 0.4 is complete: every block is mined with a simplified Proof of Work (a nonce and a configurable difficulty), stores the hash of the previous block, the chain can be validated (including the difficulty), and tampering can be simulated and detected. Version 1.0, a complete educational blockchain simulator, is the next step.

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
Proof of Work (done, v0.4)
    ↓
complete educational simulator (next, v1.0)
```
