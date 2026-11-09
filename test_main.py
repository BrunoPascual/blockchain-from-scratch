import hashlib
import json
import unittest

from main import GENESIS_PREVIOUS_HASH, calculate_block_hash

TRANSACTIONS = (("Ana", "Bob", 10.0), ("Bob", "Cid", 2.5))


class CalculateBlockHashTests(unittest.TestCase):
    def test_genesis_constant(self):
        self.assertEqual(GENESIS_PREVIOUS_HASH, "0" * 64)

    def test_hash_has_64_hex_characters(self):
        result = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH)
        self.assertEqual(len(result), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in result))

    def test_same_input_same_hash(self):
        first = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH)
        second = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH)
        self.assertEqual(first, second)

    def test_changing_index_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH)
        self.assertNotEqual(
            base, calculate_block_hash(1, TRANSACTIONS, GENESIS_PREVIOUS_HASH))

    def test_changing_sender_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH)
        changed = (("Ann", "Bob", 10.0), ("Bob", "Cid", 2.5))
        self.assertNotEqual(
            base, calculate_block_hash(0, changed, GENESIS_PREVIOUS_HASH))

    def test_changing_receiver_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH)
        changed = (("Ana", "Bobby", 10.0), ("Bob", "Cid", 2.5))
        self.assertNotEqual(
            base, calculate_block_hash(0, changed, GENESIS_PREVIOUS_HASH))

    def test_changing_amount_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH)
        changed = (("Ana", "Bob", 10.01), ("Bob", "Cid", 2.5))
        self.assertNotEqual(
            base, calculate_block_hash(0, changed, GENESIS_PREVIOUS_HASH))

    def test_changing_previous_hash_changes_hash(self):
        base = calculate_block_hash(0, TRANSACTIONS, GENESIS_PREVIOUS_HASH)
        self.assertNotEqual(
            base, calculate_block_hash(0, TRANSACTIONS, "1" * 64))

    def test_matches_documented_serialization(self):
        serialized = json.dumps(
            [3, [["Ana", "Bob", 10.0], ["Bob", "Cid", 2.5]], "ab" * 32],
            separators=(",", ":"),
            ensure_ascii=False,
        )
        expected = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.assertEqual(
            calculate_block_hash(3, TRANSACTIONS, "ab" * 32), expected)

    def test_non_ascii_names_use_utf8(self):
        transactions = (("José", "Zoë", 1.0),)
        serialized = '[0,[["José","Zoë",1.0]],"%s"]' % GENESIS_PREVIOUS_HASH
        expected = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        self.assertEqual(
            calculate_block_hash(0, transactions, GENESIS_PREVIOUS_HASH),
            expected)


if __name__ == "__main__":
    unittest.main()
