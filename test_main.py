import hashlib
import json
import unittest

from main import (
    DEFAULT_DIFFICULTY,
    GENESIS_PREVIOUS_HASH,
    MAX_DIFFICULTY,
    calculate_block_hash,
    create_block,
    mine_block,
    tamper_block,
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
        self.assertTrue(block[4].startswith("0" * DEFAULT_DIFFICULTY))


def build_chain(size, difficulty=0):
    chain = []
    for i in range(size):
        chain.append(create_block(chain, [("Ana", "Bob", float(i + 1))], difficulty))
    return chain


class ValidateChainTests(unittest.TestCase):
    def test_empty_chain_is_valid(self):
        self.assertEqual(validate_chain([]), [])

    def test_valid_chain_has_no_problems(self):
        self.assertEqual(validate_chain(build_chain(3)), [])

    def test_tamper_without_recalculating_breaks_block_hash(self):
        chain = build_chain(3)
        tampered = tamper_block(chain, 0, 0, 99.0, False)
        self.assertEqual(
            validate_chain(tampered), ["Bloco 0: hash do bloco não confere."])

    def test_tamper_with_recalculating_breaks_next_link(self):
        chain = build_chain(2)
        tampered = tamper_block(chain, 0, 0, 99.0, True)
        self.assertEqual(
            validate_chain(tampered), ["Bloco 1: hash anterior não confere."])

    def test_multiple_problems_are_all_reported(self):
        chain = build_chain(3)
        tampered = tamper_block(chain, 0, 0, 99.0, False)
        tampered = tamper_block(tampered, 1, 0, 99.0, False)
        self.assertEqual(
            validate_chain(tampered),
            ["Bloco 0: hash do bloco não confere.",
             "Bloco 1: hash do bloco não confere."])

    def test_wrong_index_message(self):
        transactions = (("Ana", "Bob", 1.0),)
        block = (5, transactions, GENESIS_PREVIOUS_HASH,
                 0,
                 calculate_block_hash(5, transactions, GENESIS_PREVIOUS_HASH, 0))
        self.assertEqual(
            validate_chain([block]),
            ["Bloco 0: índice incorreto (esperado 0, encontrado 5)."])

    def test_wrong_genesis_previous_hash(self):
        transactions = (("Ana", "Bob", 1.0),)
        block = (0, transactions, "1" * 64,
                 0,
                 calculate_block_hash(0, transactions, "1" * 64, 0))
        self.assertEqual(
            validate_chain([block]), ["Bloco 0: hash anterior não confere."])

    def test_does_not_modify_chain(self):
        chain = build_chain(2)
        snapshot = list(chain)
        validate_chain(chain)
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


if __name__ == "__main__":
    unittest.main()
