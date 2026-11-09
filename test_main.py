import contextlib
import hashlib
import io
import json
import re
import unittest
from unittest import mock

from main import (
    DEFAULT_DIFFICULTY,
    GENESIS_PREVIOUS_HASH,
    MAX_DIFFICULTY,
    calculate_block_hash,
    create_block,
    format_transaction,
    main,
    menu_change_difficulty,
    menu_create_block,
    mine_block,
    print_error,
    print_field,
    print_title,
    tamper_block,
    transactions_word,
    validate_chain,
)

TRANSACTIONS = (("Ana", "Bob", 10.0), ("Bob", "Cid", 2.5))


class CalculateBlockHashTests(unittest.TestCase):
    def test_genesis_constant(self):
        self.assertEqual(GENESIS_PREVIOUS_HASH, "0" * 64)

    def test_hash_has_64_hex_characters(self):
        result = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in result))

    def test_same_input_same_hash(self):
        first = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        second = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        self.assertEqual(first, second)

    def test_changing_index_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        self.assertNotEqual(
            base, calculate_block_hash(1, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0))

    def test_changing_sender_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        changed = (("Ann", "Bob", 10.0), ("Bob", "Cid", 2.5))
        self.assertNotEqual(
            base, calculate_block_hash(0, changed, GENESIS_PREVIOUS_HASH, 0))

    def test_changing_receiver_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        changed = (("Ana", "Bobby", 10.0), ("Bob", "Cid", 2.5))
        self.assertNotEqual(
            base, calculate_block_hash(0, changed, GENESIS_PREVIOUS_HASH, 0))

    def test_changing_amount_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        changed = (("Ana", "Bob", 10.01), ("Bob", "Cid", 2.5))
        self.assertNotEqual(
            base, calculate_block_hash(0, changed, GENESIS_PREVIOUS_HASH, 0))

    def test_changing_previous_hash_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        self.assertNotEqual(
            base, calculate_block_hash(0, TRANSACTIONS, "1" * 64, 0))

    def test_changing_nonce_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        self.assertNotEqual(
            base, calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 1))

    def test_matches_documented_serialization(self):
        serialized = json.dumps(
            [3, [["Ana", "Bob", 10.0], ["Bob", "Cid", 2.5]], "ab" * 32, 0],
            separators=(",", ":"),
            ensure_ascii=False,
        )
        expected = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.assertEqual(
            calculate_block_hash(3, TRANSACTIONS, "ab" * 32, 0), expected)

    def test_non_ascii_names_use_utf8(self):
        transactions = (("José", "Zoë", 1.0),)
        serialized = '[0,[["José","Zoë",1.0]],"%s",0]' % GENESIS_PREVIOUS_HASH
        expected = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.assertEqual(
            calculate_block_hash(0, transactions, GENESIS_PREVIOUS_HASH, 0),
            expected)

    def test_known_digest_for_fixed_block(self):
        self.assertEqual(
            calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0),
            "80ae9497fc47d78cd0bc6874789fcbf8e44d11d4be1d829d6e2675ace8f0f195")


class MineBlockTests(unittest.TestCase):
    def test_mine_block_meets_difficulty(self):
        nonce, block_hash = mine_block(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 2)
        self.assertTrue(block_hash.startswith("0" * 2))
        self.assertEqual(
            block_hash,
            calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, nonce),
        )

    def test_mine_block_difficulty_zero_returns_nonce_zero(self):
        nonce, block_hash = mine_block(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0)
        self.assertEqual(nonce, 0)
        self.assertEqual(
            block_hash,
            calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 0),
        )

    def test_mine_block_returns_first_valid_nonce(self):
        nonce, block_hash = mine_block(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, 2)
        for n in range(nonce):
            h = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH, n)
            self.assertFalse(h.startswith("0" * 2))
        self.assertTrue(block_hash.startswith("0" * 2))


class CreateBlockTests(unittest.TestCase):
    def test_first_block_uses_genesis_hash(self):
        block = create_block([], [("Ana", "Bob", 1.0)], 0)
        self.assertEqual(block[0], 0)
        self.assertEqual(block[1], (("Ana", "Bob", 1.0),))
        self.assertEqual(block[2], GENESIS_PREVIOUS_HASH)

    def test_returns_tuple_of_five(self):
        block = create_block([], [("Ana", "Bob", 1.0)], 0)
        self.assertIsInstance(block, tuple)
        self.assertIsInstance(block[1], tuple)
        self.assertEqual(len(block), 5)

    def test_previous_hash_links_to_previous_block_hash(self):
        chain = []
        for i in range(3):
            chain.append(create_block(chain, [("Ana", "Bob", float(i + 1))], 0))
        self.assertEqual(chain[1][2], chain[0][4])
        self.assertEqual(chain[2][2], chain[1][4])
        self.assertEqual([b[0] for b in chain], [0, 1, 2])

    def test_block_hash_matches_own_fields(self):
        chain = [create_block([], [("Ana", "Bob", 1.0)], 0)]
        block = create_block(chain, [("Bob", "Cid", 2.0)], 0)
        self.assertEqual(
            block[4], calculate_block_hash(block[0], block[1], block[2], block[3]))

    def test_does_not_change_blockchain(self):
        chain = [create_block([], [("Ana", "Bob", 1.0)], 0)]
        snapshot = list(chain)
        create_block(chain, [("Bob", "Cid", 2.0)], 0)
        self.assertEqual(chain, snapshot)
        self.assertEqual(len(chain), 1)

    def test_create_block_meets_given_difficulty(self):
        block = create_block([], [("Ana", "Bob", 1.0)], 2)
        self.assertEqual(len(block), 5)
        self.assertTrue(block[4].startswith("0" * 2))

    def test_create_block_uses_default_difficulty(self):
        block = create_block([], [("Ana", "Bob", 1.0)], DEFAULT_DIFFICULTY)
        self.assertTrue(block[4].startswith("0000"))


def build_chain(size, difficulty=0):
    chain = []
    for i in range(size):
        chain.append(create_block(chain, [("Ana", "Bob", float(i + 1))], difficulty))
    return chain


class ValidateChainTests(unittest.TestCase):
    def test_empty_chain_is_valid(self):
        self.assertEqual(validate_chain([], 0), [])

    def test_valid_chain_has_no_problems(self):
        self.assertEqual(validate_chain(build_chain(3), 0), [])

    def test_valid_chain_at_difficulty_two_has_no_problems(self):
        self.assertEqual(validate_chain(build_chain(3, 2), 2), [])

    def test_chain_built_at_difficulty_zero_validated_at_two_reports_difficulty(self):
        # Hand-built deterministic chain: nonce 0 never meets difficulty 2.
        transactions0 = (("Ana", "Bob", 1.0),)
        block0 = (0, transactions0, GENESIS_PREVIOUS_HASH,
                  0,
                  calculate_block_hash(0, transactions0, GENESIS_PREVIOUS_HASH, 0))
        transactions1 = (("Ana", "Bob", 2.0),)
        block1 = (1, transactions1, block0[4],
                  0,
                  calculate_block_hash(1, transactions1, block0[4], 0))
        chain = [block0, block1]
        self.assertEqual(
            validate_chain(chain, 2),
            [
                "Bloco 0: hash não atende à dificuldade (esperado 2 zeros no início).",
                "Bloco 1: hash não atende à dificuldade (esperado 2 zeros no início).",
            ])

    def test_tamper_without_recalculating_breaks_block_hash(self):
        chain = build_chain(3)
        tampered = tamper_block(chain, 0, 0, 99.0, False)
        self.assertEqual(
            validate_chain(tampered, 0), ["Bloco 0: hash do bloco não confere."])

    def test_tamper_with_recalculating_breaks_next_link(self):
        chain = build_chain(2)
        tampered = tamper_block(chain, 0, 0, 99.0, True)
        self.assertEqual(
            validate_chain(tampered, 0), ["Bloco 1: hash anterior não confere."])

    def test_tamper_with_recalculating_at_difficulty_two_reports_problems(self):
        chain = build_chain(2, 2)
        tampered = tamper_block(chain, 0, 0, 99.0, True)
        problems = validate_chain(tampered, 2)
        self.assertEqual(problems, [
            "Bloco 0: hash não atende à dificuldade (esperado 2 zeros no início).",
            "Bloco 1: hash anterior não confere.",
        ])

    def test_tamper_without_recalculating_at_difficulty_two_still_breaks_block_hash(self):
        chain = build_chain(2, 2)
        tampered = tamper_block(chain, 0, 0, 99.0, False)
        self.assertEqual(
            validate_chain(tampered, 2),
            ["Bloco 0: hash do bloco não confere."])

    def test_multiple_problems_are_all_reported(self):
        chain = build_chain(3)
        tampered = tamper_block(chain, 0, 0, 99.0, False)
        tampered = tamper_block(tampered, 1, 0, 99.0, False)
        self.assertEqual(
            validate_chain(tampered, 0),
            ["Bloco 0: hash do bloco não confere.",
             "Bloco 1: hash do bloco não confere."])

    def test_wrong_index_message(self):
        transactions = (("Ana", "Bob", 1.0),)
        block = (5, transactions, GENESIS_PREVIOUS_HASH,
                 0,
                 calculate_block_hash(5, transactions, GENESIS_PREVIOUS_HASH, 0))
        self.assertEqual(
            validate_chain([block], 0),
            ["Bloco 0: índice incorreto (esperado 0, encontrado 5)."])

    def test_wrong_genesis_previous_hash(self):
        transactions = (("Ana", "Bob", 1.0),)
        block = (0, transactions, "1" * 64,
                 0,
                 calculate_block_hash(0, transactions, "1" * 64, 0))
        self.assertEqual(
            validate_chain([block], 0), ["Bloco 0: hash anterior não confere."])

    def test_does_not_modify_chain(self):
        chain = build_chain(2)
        snapshot = list(chain)
        validate_chain(chain, 0)
        self.assertEqual(chain, snapshot)


class TamperBlockTests(unittest.TestCase):
    def test_does_not_modify_input(self):
        chain = build_chain(2)
        snapshot = list(chain)
        original = chain[0]
        tamper_block(chain, 0, 0, 99.0, True)
        self.assertEqual(chain, snapshot)
        self.assertIs(chain[0], original)
        self.assertEqual(original[1], (("Ana", "Bob", 1.0),))

    def test_returns_new_list_with_replaced_amount(self):
        chain = build_chain(2)
        result = tamper_block(chain, 0, 0, 99, False)
        self.assertIsNot(result, chain)
        self.assertEqual(result[0][1], (("Ana", "Bob", 99.0),))
        self.assertIsInstance(result[0][1][0][2], float)
        self.assertEqual(result[0][0], chain[0][0])
        self.assertEqual(result[0][2], chain[0][2])
        self.assertEqual(result[0][4], chain[0][4])

    def test_untouched_blocks_are_identical(self):
        chain = build_chain(3)
        result = tamper_block(chain, 1, 0, 5.0, True)
        self.assertIs(result[0], chain[0])
        self.assertIs(result[2], chain[2])
        self.assertIsNot(result[1], chain[1])

    def test_recalculated_hash_matches_fields(self):
        chain = build_chain(2)
        block = tamper_block(chain, 1, 0, 5.0, True)[1]
        self.assertEqual(
            block[4], calculate_block_hash(block[0], block[1], block[2], block[3]))
        self.assertNotEqual(block[4], chain[1][4])


class OutputHelperTests(unittest.TestCase):
    def test_print_title(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_title("Criar bloco")
        expected = "\n" + "=" * 40 + "\nCriar bloco\n" + "=" * 40 + "\n"
        self.assertEqual(buffer.getvalue(), expected)

    def test_print_field_nonce(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_field("Nonce", 42)
        self.assertEqual(buffer.getvalue(), "Nonce         : 42\n")

    def test_print_field_hash_anterior(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_field("Hash anterior", "abc")
        self.assertEqual(buffer.getvalue(), "Hash anterior : abc\n")

    def test_print_error(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_error("Bloco inválido.")
        self.assertEqual(buffer.getvalue(), "Erro: Bloco inválido.\n")

    def test_format_transaction(self):
        self.assertEqual(
            format_transaction(("Ana", "Bob", 10)), "Ana -> Bob: 10.00"
        )

    def test_transactions_word_singular(self):
        self.assertEqual(transactions_word(1), "transação")

    def test_transactions_word_plural_zero(self):
        self.assertEqual(transactions_word(0), "transações")

    def test_transactions_word_plural_three(self):
        self.assertEqual(transactions_word(3), "transações")


MENU_TEXT = (
    "====== MINI BLOCKCHAIN ======\n"
    "1 - Nova transação\n"
    "2 - Mostrar transações pendentes\n"
    "3 - Criar bloco\n"
    "4 - Mostrar blockchain\n"
    "5 - Validar blockchain\n"
    "6 - Simular adulteração\n"
    "7 - Alterar dificuldade\n"
    "8 - Sair\n"
)


def run_session(inputs):
    """Run main() feeding the given inputs; EOF follows the last one."""
    buffer = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(inputs) + [EOFError()]):
        with contextlib.redirect_stdout(buffer):
            main()
    # Mining time varies from run to run, so it is normalized.
    return re.sub(r"em \d+\.\d\d s", "em X s", buffer.getvalue())


def run_menu(function, state, inputs):
    """Run one menu function; return (new_state, printed output)."""
    buffer = io.StringIO()
    with mock.patch("builtins.input", side_effect=list(inputs)):
        with contextlib.redirect_stdout(buffer):
            new_state = function(state)
    return new_state, re.sub(r"em \d+\.\d\d s", "em X s", buffer.getvalue())


class SessionTests(unittest.TestCase):
    def test_session_full_flow(self):
        inputs = ["7", "1",
                  "1", "Ana", "Bob", "10",
                  "1", "Bob", "Cid", "2.5",
                  "1", "Cid", "Ana", "1",
                  "1", "Ana", "Cid", "3",
                  "3", "3", "2", "4", "5",
                  "6", "0", "1", "500", "n",
                  "5", "8"]
        expected = "".join([
            MENU_TEXT + 'Entrando em Alterar dificuldade...\nDificuldade atual: 4\nDificuldade alterada para 1.\n',
            MENU_TEXT + 'Entrando em Nova transação...\nTransação adicionada: Ana -> Bob: 10.00\n',
            MENU_TEXT + 'Entrando em Nova transação...\nTransação adicionada: Bob -> Cid: 2.50\n',
            MENU_TEXT + 'Entrando em Nova transação...\nTransação adicionada: Cid -> Ana: 1.00\n',
            MENU_TEXT + 'Entrando em Nova transação...\nTransação adicionada: Ana -> Cid: 3.00\n',
            MENU_TEXT + 'Entrando em Criar bloco...\nMinerando bloco com dificuldade 1...\nBLOCO 0 criado com sucesso com 3 transações.\nNonce encontrado: 48 (49 tentativas em X s).\n',
            MENU_TEXT + 'Entrando em Criar bloco...\nMinerando bloco com dificuldade 1...\nBLOCO 1 criado com sucesso com 1 transações.\nNonce encontrado: 3 (4 tentativas em X s).\n',
            MENU_TEXT + 'Entrando em Mostrar transações pendentes...\nNão há transações pendentes.\n',
            MENU_TEXT + 'Entrando em Mostrar blockchain...\n\n========== BLOCKCHAIN ==========\nDificuldade: 1 (o hash deve começar com 1 zeros)\n\nBLOCO 0\nHash anterior: 0000000000000000000000000000000000000000000000000000000000000000\nNonce: 48\nHash: 0c5672ac5ce664ae5aa4d586266c2eb0f99b0928b70dc70630da3fc9c36ab128\nTransações:\nAna -> Bob: 10.00\nBob -> Cid: 2.50\nCid -> Ana: 1.00\n-------------------------------\n\nBLOCO 1\nHash anterior: 0c5672ac5ce664ae5aa4d586266c2eb0f99b0928b70dc70630da3fc9c36ab128\nNonce: 3\nHash: 0991dabad16df13fcb375f69dc7132d72224511da4fcd3b126c867c840aba621\nTransações:\nAna -> Cid: 3.00\n-------------------------------\n',
            MENU_TEXT + 'Entrando em Validar blockchain...\nBlockchain válida.\n',
            MENU_TEXT + 'Entrando em Simular adulteração...\n1 - Ana -> Bob: 10.00\n2 - Bob -> Cid: 2.50\n3 - Cid -> Ana: 1.00\nBloco 0 adulterado. Use a opção 5 para validar a blockchain.\n',
            MENU_TEXT + 'Entrando em Validar blockchain...\nBlockchain inválida! Problemas encontrados:\n- Bloco 0: hash do bloco não confere.\n',
            MENU_TEXT + 'finalizando...\n',
        ])
        self.assertEqual(run_session(inputs), expected)

    def test_session_invalid_inputs(self):
        inputs = ["x", "99",
                  "1", "", "Bob", "5",
                  "1", "Ana", "Bob", "abc",
                  "3", "4", "5", "6",
                  "7", "9", "8"]
        expected = "".join([
            MENU_TEXT + 'Opção inválida. Digite um número entre 1 e 8.\n',
            MENU_TEXT + 'Opção inválida. Digite um número entre 1 e 8.\n',
            MENU_TEXT + 'Entrando em Nova transação...\nRemetente e destinatário não podem estar vazios.\n',
            MENU_TEXT + 'Entrando em Nova transação...\nValor inválido. Digite um número.\n',
            MENU_TEXT + 'Entrando em Criar bloco...\nNão há transações pendentes para criar um bloco.\n',
            MENU_TEXT + 'Entrando em Mostrar blockchain...\nA blockchain ainda está vazia!!\n',
            MENU_TEXT + 'Entrando em Validar blockchain...\nA blockchain ainda está vazia!!\n',
            MENU_TEXT + 'Entrando em Simular adulteração...\nA blockchain ainda está vazia!!\n',
            MENU_TEXT + 'Entrando em Alterar dificuldade...\nDificuldade atual: 4\nDificuldade inválida. Digite um número entre 0 e 5.\n',
            MENU_TEXT + 'finalizando...\n',
        ])
        self.assertEqual(run_session(inputs), expected)

    def test_session_eof_inside_tamper(self):
        inputs = ["7", "1", "1", "Ana", "Bob", "1", "3", "6", "0"]
        expected = "".join([
            MENU_TEXT + 'Entrando em Alterar dificuldade...\nDificuldade atual: 4\nDificuldade alterada para 1.\n',
            MENU_TEXT + 'Entrando em Nova transação...\nTransação adicionada: Ana -> Bob: 1.00\n',
            MENU_TEXT + 'Entrando em Criar bloco...\nMinerando bloco com dificuldade 1...\nBLOCO 0 criado com sucesso com 1 transações.\nNonce encontrado: 15 (16 tentativas em X s).\n',
            MENU_TEXT + 'Entrando em Simular adulteração...\n1 - Ana -> Bob: 1.00\n\nfinalizando...\n',
        ])
        self.assertEqual(run_session(inputs), expected)

    def test_session_spaces_in_numbers(self):
        out = run_session([" 7 ", " 2 ", "8"])
        self.assertIn("Dificuldade alterada para 2.", out)


class MenuFunctionTests(unittest.TestCase):
    def test_create_block_takes_three_and_keeps_rest_pending(self):
        pending = [("A", "B", float(n)) for n in range(1, 5)]
        state, _ = run_menu(menu_create_block, (pending, [], 0), [])
        new_pending, chain, difficulty = state
        self.assertEqual(len(new_pending), 1)
        self.assertEqual(len(chain), 1)
        self.assertEqual(len(chain[0][1]), 3)
        self.assertEqual(difficulty, 0)

    def test_change_difficulty_on_empty_chain(self):
        state, _ = run_menu(menu_change_difficulty, ([], [], 4), ["3"])
        self.assertEqual(state, ([], [], 3))

    def test_change_difficulty_on_non_empty_chain_is_unchanged(self):
        chain = [create_block([], [("A", "B", 1.0)], 0)]
        state = ([], chain, 0)
        new_state, output = run_menu(menu_change_difficulty, state, [])
        self.assertEqual(new_state, state)
        self.assertIn("só pode ser alterada", output)


if __name__ == "__main__":
    unittest.main()
