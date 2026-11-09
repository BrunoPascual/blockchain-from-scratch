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
    ask_tamper_target,
    calculate_block_hash,
    create_block,
    format_transaction,
    main,
    menu_change_difficulty,
    menu_create_block,
    menu_full_attack,
    menu_show_pending,
    menu_tamper,
    mine_block,
    print_error,
    print_field,
    print_title,
    remine_chain,
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


class RemineChainTests(unittest.TestCase):
    def test_remine_from_zero_makes_chain_valid(self):
        chain = build_chain(3, 2)
        tampered = tamper_block(chain, 0, 0, 99.0, True)
        new_chain, attempts = remine_chain(tampered, 0, 2)
        self.assertEqual(validate_chain(new_chain, 2), [])
        self.assertEqual(len(attempts), 3)

    def test_attempts_equal_nonce_plus_one(self):
        chain = build_chain(3, 2)
        tampered = tamper_block(chain, 0, 0, 99.0, True)
        new_chain, attempts = remine_chain(tampered, 0, 2)
        for i, block in enumerate(new_chain):
            self.assertEqual(attempts[i], block[3] + 1)

    def test_remine_from_one_keeps_first_block(self):
        chain = build_chain(3, 2)
        tampered = tamper_block(chain, 1, 0, 99.0, True)
        new_chain, attempts = remine_chain(tampered, 1, 2)
        self.assertIs(new_chain[0], chain[0])
        self.assertEqual(len(attempts), 2)
        self.assertEqual(validate_chain(new_chain, 2), [])

    def test_remine_last_position_only(self):
        chain = build_chain(3, 2)
        tampered = tamper_block(chain, 2, 0, 99.0, True)
        new_chain, attempts = remine_chain(tampered, 2, 2)
        self.assertIs(new_chain[0], chain[0])
        self.assertIs(new_chain[1], chain[1])
        self.assertEqual(len(attempts), 1)
        self.assertEqual(validate_chain(new_chain, 2), [])

    def test_difficulty_zero_attempts_are_one(self):
        chain = build_chain(3, 0)
        tampered = tamper_block(chain, 0, 0, 99.0, True)
        new_chain, attempts = remine_chain(tampered, 0, 0)
        self.assertEqual(attempts, [1, 1, 1])
        self.assertEqual(validate_chain(new_chain, 0), [])

    def test_does_not_modify_input(self):
        chain = build_chain(3, 2)
        tampered = tamper_block(chain, 0, 0, 99.0, True)
        snapshot = list(tampered)
        block_snapshots = [list(block) for block in tampered]
        remine_chain(tampered, 0, 2)
        self.assertEqual(tampered, snapshot)
        for original, snapshot_block in zip(tampered, block_snapshots):
            self.assertEqual(list(original), snapshot_block)

    def test_keeps_index_and_transactions(self):
        chain = build_chain(3, 2)
        tampered = tamper_block(chain, 0, 0, 99.0, True)
        new_chain, _ = remine_chain(tampered, 0, 2)
        for new_block, original_block in zip(new_chain, tampered):
            self.assertEqual(new_block[0], original_block[0])
            self.assertEqual(new_block[1], original_block[1])


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


_TITLE_LINE = "=" * 40
MENU_TEXT = (
    "\n" + _TITLE_LINE + "\nMINI BLOCKCHAIN\n" + _TITLE_LINE + "\n"
    "1 - Nova transação\n"
    "2 - Mostrar transações pendentes\n"
    "3 - Criar bloco\n"
    "4 - Mostrar blockchain\n"
    "5 - Validar blockchain\n"
    "6 - Simular adulteração\n"
    "7 - Simular ataque completo\n"
    "8 - Alterar dificuldade\n"
    "9 - Sair\n"
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
        inputs = ["8", "1",
                  "1", "Ana", "Bob", "10",
                  "1", "Bob", "Cid", "2.5",
                  "1", "Cid", "Ana", "1",
                  "1", "Ana", "Cid", "3",
                  "3", "3", "2", "4", "5",
                  "6", "0", "1", "500", "n",
                  "5", "9"]
        expected = "".join([
            MENU_TEXT + f"\n{_TITLE_LINE}\nAlterar dificuldade\n{_TITLE_LINE}\nDificuldade atual: 4\nDificuldade alterada para 1.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nNova transação\n{_TITLE_LINE}\nTransação adicionada: Ana -> Bob: 10.00\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nNova transação\n{_TITLE_LINE}\nTransação adicionada: Bob -> Cid: 2.50\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nNova transação\n{_TITLE_LINE}\nTransação adicionada: Cid -> Ana: 1.00\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nNova transação\n{_TITLE_LINE}\nTransação adicionada: Ana -> Cid: 3.00\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nCriar bloco\n{_TITLE_LINE}\nMinerando bloco com dificuldade 1...\nBLOCO 0 criado com sucesso com 3 transações.\nNonce encontrado: 48 (49 tentativas em X s).\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nCriar bloco\n{_TITLE_LINE}\nMinerando bloco com dificuldade 1...\nBLOCO 1 criado com sucesso com 1 transação.\nNonce encontrado: 3 (4 tentativas em X s).\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nMostrar transações pendentes\n{_TITLE_LINE}\nNão há transações pendentes.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nMostrar blockchain\n{_TITLE_LINE}\nDificuldade   : 1 (o hash deve começar com 1 zeros)\n\nBLOCO 0\nHash anterior : 0000000000000000000000000000000000000000000000000000000000000000\nNonce         : 48\nHash          : 0c5672ac5ce664ae5aa4d586266c2eb0f99b0928b70dc70630da3fc9c36ab128\nTransações:\n  Ana -> Bob: 10.00\n  Bob -> Cid: 2.50\n  Cid -> Ana: 1.00\n\nBLOCO 1\nHash anterior : 0c5672ac5ce664ae5aa4d586266c2eb0f99b0928b70dc70630da3fc9c36ab128\nNonce         : 3\nHash          : 0991dabad16df13fcb375f69dc7132d72224511da4fcd3b126c867c840aba621\nTransações:\n  Ana -> Cid: 3.00\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nValidar blockchain\n{_TITLE_LINE}\nBlockchain válida.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nSimular adulteração\n{_TITLE_LINE}\n1 - Ana -> Bob: 10.00\n2 - Bob -> Cid: 2.50\n3 - Cid -> Ana: 1.00\nBloco 0 adulterado. Use a opção 5 para validar a blockchain.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nValidar blockchain\n{_TITLE_LINE}\nBlockchain inválida! Problemas encontrados:\n- Bloco 0: hash do bloco não confere.\n",
            MENU_TEXT + "finalizando...\n",
        ])
        self.assertEqual(run_session(inputs), expected)

    def test_session_invalid_inputs(self):
        inputs = ["x", "99",
                  "1", "", "Bob", "5",
                  "1", "Ana", "Bob", "abc",
                  "3", "4", "5", "6",
                  "8", "9", "9"]
        expected = "".join([
            MENU_TEXT + "Erro: Opção inválida. Digite um número entre 1 e 9.\n",
            MENU_TEXT + "Erro: Opção inválida. Digite um número entre 1 e 9.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nNova transação\n{_TITLE_LINE}\nErro: Remetente e destinatário não podem estar vazios.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nNova transação\n{_TITLE_LINE}\nErro: Valor inválido. Digite um número.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nCriar bloco\n{_TITLE_LINE}\nErro: Não há transações pendentes para criar um bloco.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nMostrar blockchain\n{_TITLE_LINE}\nA blockchain ainda está vazia!!\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nValidar blockchain\n{_TITLE_LINE}\nA blockchain ainda está vazia!!\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nSimular adulteração\n{_TITLE_LINE}\nA blockchain ainda está vazia!!\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nAlterar dificuldade\n{_TITLE_LINE}\nDificuldade atual: 4\nErro: Dificuldade inválida. Digite um número entre 0 e 5.\n",
            MENU_TEXT + "finalizando...\n",
        ])
        self.assertEqual(run_session(inputs), expected)

    def test_session_eof_inside_tamper(self):
        inputs = ["8", "1", "1", "Ana", "Bob", "1", "3", "6", "0"]
        expected = "".join([
            MENU_TEXT + f"\n{_TITLE_LINE}\nAlterar dificuldade\n{_TITLE_LINE}\nDificuldade atual: 4\nDificuldade alterada para 1.\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nNova transação\n{_TITLE_LINE}\nTransação adicionada: Ana -> Bob: 1.00\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nCriar bloco\n{_TITLE_LINE}\nMinerando bloco com dificuldade 1...\nBLOCO 0 criado com sucesso com 1 transação.\nNonce encontrado: 15 (16 tentativas em X s).\n",
            MENU_TEXT + f"\n{_TITLE_LINE}\nSimular adulteração\n{_TITLE_LINE}\n1 - Ana -> Bob: 1.00\n\nfinalizando...\n",
        ])
        self.assertEqual(run_session(inputs), expected)

    def test_session_spaces_in_numbers(self):
        out = run_session([" 8 ", " 2 ", "9"])
        self.assertIn("Dificuldade alterada para 2.", out)

    def test_show_pending_transactions(self):
        state = ([("Ana", "Bob", 10.0), ("Bob", "Cid", 2.5)], [], 0)
        _, output = run_menu(menu_show_pending, state, [])
        expected = (
            "\n" + _TITLE_LINE + "\nMostrar transações pendentes\n"
            + _TITLE_LINE + "\nAs transações pendentes são:\n"
            "1 - Ana -> Bob: 10.00\n"
            "2 - Bob -> Cid: 2.50\n"
        )
        self.assertEqual(output, expected)

    def test_create_block_singular_word(self):
        _, output = run_menu(
            menu_create_block, ([("Ana", "Bob", 10.0)], [], 0), [])
        self.assertIn("BLOCO 0 criado com sucesso com 1 transação.", output)

    def test_session_end_to_end(self):
        inputs = [
            "8", "1",
            "1", "Ana", "Bob", "10",
            "1", "Bob", "Cid", "2.5",
            "1", "Cid", "Ana", "1",
            "1", "Ana", "Cid", "3",
            "3", "3",
            "5",
            "6", "0", "1", "500", "n",
            "5",
            "7", "0", "1", "500",
            "5",
            "9",
        ]
        out = run_session(inputs)
        # The first validation (before tampering) must report the chain as valid.
        self.assertIn("Blockchain válida.", out)
        first_valid_index = out.find("Blockchain válida.")
        invalid_index = out.find("Blockchain inválida! Problemas encontrados:")
        self.assertLess(first_valid_index, invalid_index)
        # The final validation following the full attack must be valid.
        last_valid_index = out.rfind("Blockchain válida.")
        last_invalid_index = out.rfind("Blockchain inválida! Problemas encontrados:")
        self.assertGreater(last_valid_index, last_invalid_index)
        self.assertIn("Bloco 0 adulterado. Re-minerando os blocos 0 a 1", out)
        self.assertIn("BLOCO 0 re-minerado: nonce", out)
        self.assertIn("BLOCO 1 re-minerado: nonce", out)
        self.assertIn("Blockchain válida novamente: o ataque funcionou", out)


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

    def _build_two_block_chain(self, difficulty=1):
        pending = []
        blockchain = []
        for amount in [10.0, 2.5]:
            blockchain.append(
                create_block(blockchain, [("Ana", "Bob", amount)], difficulty))
        return pending, blockchain, difficulty

    def test_full_attack_makes_chain_valid(self):
        state = self._build_two_block_chain(1)
        new_state, output = run_menu(
            menu_full_attack, state, ["0", "1", "500"])
        _, chain, difficulty = new_state
        self.assertEqual(validate_chain(chain, difficulty), [])
        self.assertEqual(chain[0][1][0][2], 500.0)
        self.assertIn("BLOCO 0 re-minerado: nonce", output)
        self.assertIn("BLOCO 1 re-minerado: nonce", output)
        self.assertIn(
            "Blockchain válida novamente: o ataque funcionou", output)

    def test_full_attack_on_last_block_remines_one(self):
        state = self._build_two_block_chain(1)
        new_state, output = run_menu(
            menu_full_attack, state, ["1", "1", "500"])
        _, chain, difficulty = new_state
        self.assertEqual(validate_chain(chain, difficulty), [])
        re_minerado_count = output.count("re-minerado")
        self.assertEqual(re_minerado_count, 1)
        self.assertIn(
            "Blockchain válida novamente: o ataque funcionou", output)

    def test_full_attack_empty_chain(self):
        state = ([], [], 1)
        new_state, output = run_menu(menu_full_attack, state, ["0", "1", "500"])
        self.assertEqual(new_state, state)
        self.assertIn("A blockchain ainda está vazia!!", output)

    def test_full_attack_invalid_block(self):
        state = self._build_two_block_chain(1)
        new_state, _ = run_menu(menu_full_attack, state, ["9"])
        self.assertEqual(new_state, state)

    def test_full_attack_invalid_block_error_message(self):
        state = self._build_two_block_chain(1)
        _, output = run_menu(menu_full_attack, state, ["9"])
        self.assertIn("Erro: Bloco inválido.", output)

    def test_full_attack_invalid_transaction(self):
        state = self._build_two_block_chain(1)
        new_state, _ = run_menu(menu_full_attack, state, ["0", "9"])
        self.assertEqual(new_state, state)

    def test_full_attack_invalid_transaction_error_message(self):
        state = self._build_two_block_chain(1)
        _, output = run_menu(menu_full_attack, state, ["0", "9"])
        self.assertIn("Erro: Transação inválida.", output)

    def test_full_attack_invalid_value(self):
        state = self._build_two_block_chain(1)
        new_state, _ = run_menu(menu_full_attack, state, ["0", "1", "abc"])
        self.assertEqual(new_state, state)

    def test_full_attack_invalid_value_error_message(self):
        state = self._build_two_block_chain(1)
        _, output = run_menu(menu_full_attack, state, ["0", "1", "abc"])
        self.assertIn("Erro: Valor inválido. Digite um número.", output)

    def test_full_attack_eof_at_value(self):
        out = run_session([
            "8", "1",
            "1", "Ana", "Bob", "1",
            "3",
            "7", "0", "1",
        ])
        self.assertTrue(out.endswith("finalizando...\n"))


class AskTamperTargetTests(unittest.TestCase):
    def _ask(self, chain, inputs):
        """Call ask_tamper_target capturing its printed prompts."""
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with mock.patch("builtins.input", side_effect=list(inputs)):
                return ask_tamper_target(chain)

    def test_empty_chain_returns_none(self):
        result = self._ask([], [])
        self.assertIsNone(result)

    def test_valid_target_returns_positions_and_amount(self):
        chain = build_chain(2, 0)
        result = self._ask(chain, ["0", "1", "500"])
        self.assertEqual(result, (0, 0, 500.0))

    def test_invalid_block_returns_none(self):
        chain = build_chain(2, 0)
        result = self._ask(chain, ["9"])
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
