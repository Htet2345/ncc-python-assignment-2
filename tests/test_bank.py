import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from bank import Bank, money
from main import main


class BankTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent)
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / 'userlist.txt'
        self.bank = Bank(self.path)
        self.bank.register('alice', '1234', '1000')
        self.bank.register('bob', '5678', '200')

    def test_full_flow_persists_after_restart(self):
        self.assertEqual(self.bank.login('ALICE', '1234'), 'alice')
        self.bank.transfer('alice', 'bob', '150')
        self.bank.withdraw('alice', '50')
        self.bank.update('alice', 'alice_new', '9876')
        restored = Bank(self.path)
        self.assertEqual(restored.login('alice_new', '9876'), 'alice_new')
        self.assertEqual(restored.accounts['alice_new']['balance'], Decimal('800.00'))
        self.assertEqual(restored.accounts['bob']['balance'], Decimal('350.00'))
        with self.assertRaises(ValueError):
            restored.login('alice', '1234')
        with self.assertRaises(ValueError):
            restored.login('alice_new', '1234')

    def test_invalid_transfers_do_not_change_file(self):
        original = self.path.read_bytes()
        for recipient, amount in [('bob', '-1'), ('bob', '0'), ('bob', '1001'), ('alice', '10'), ('missing', '10')]:
            with self.subTest(recipient=recipient, amount=amount):
                with self.assertRaises(ValueError):
                    self.bank.transfer('alice', recipient, amount)
                self.assertEqual(self.path.read_bytes(), original)

    def test_decimal_arithmetic_and_validation(self):
        self.bank.withdraw('alice', '0.10')
        self.bank.withdraw('alice', '0.20')
        self.assertEqual(Bank(self.path).accounts['alice']['balance'], Decimal('999.70'))
        for amount in ['NaN', 'Infinity', '-2', 'abc', '0.001', '9999999999999999']:
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                money(amount)

    def test_duplicate_and_invalid_updates_preserve_accounts(self):
        original = self.path.read_bytes()
        for action in [lambda: self.bank.register('ALICE', '1234', '10'),
                       lambda: self.bank.update('alice', 'bob'),
                       lambda: self.bank.update('alice', 'new_alice', 'bad')]:
            with self.assertRaises(ValueError):
                action()
            self.assertEqual(self.path.read_bytes(), original)
            self.assertEqual(self.bank.login('alice', '1234'), 'alice')

    def test_failed_save_preserves_memory_and_file(self):
        original = self.path.read_bytes()
        with patch.object(Path, 'replace', side_effect=OSError('Simulated disk error')):
            with self.assertRaises(OSError):
                self.bank.transfer('alice', 'bob', '10')
        self.assertEqual(self.bank.accounts['alice']['balance'], Decimal('1000.00'))
        self.assertEqual(self.path.read_bytes(), original)

    def test_corrupt_file_is_not_overwritten(self):
        self.path.write_text('invalid file', encoding='utf-8')
        with self.assertRaises(ValueError):
            Bank(self.path)
        self.assertEqual(self.path.read_text(encoding='utf-8'), 'invalid file')

    def test_terminal_menus(self):
        answers = ['1', 'alice', '1234', '1', 'bob', '150', '2', '50', '3', 'alice_new', '9876', '9876', '', '0', '0']
        with patch('main.Bank', return_value=self.bank), \
             patch('builtins.input', side_effect=answers), \
             patch('builtins.print') as output:
            main()
        messages = ' '.join(str(call.args) for call in output.call_args_list)
        self.assertNotIn('File handling practice', messages)
        self.assertNotIn('View balance', messages)
        restored = Bank(self.path)
        self.assertEqual(restored.login('alice_new', '9876'), 'alice_new')
        self.assertEqual(restored.accounts['alice_new']['balance'], Decimal('800.00'))
        self.assertEqual(restored.accounts['bob']['balance'], Decimal('350.00'))

    def test_name_with_spaces_and_balance_update_persist(self):
        username = self.bank.register('Htet Myet Zaw', '23456', '10000')
        self.assertEqual(username, 'htet myet zaw')
        self.bank.update(username, new_balance='12000')
        restored = Bank(self.path)
        self.assertEqual(restored.login('  HTET  Myet Zaw  ', '23456'), username)
        self.assertEqual(restored.accounts[username]['balance'], Decimal('12000.00'))
        original = self.path.read_bytes()
        with self.assertRaises(ValueError):
            self.bank.update(username, new_balance='-1')
        self.assertEqual(self.path.read_bytes(), original)

    def test_register_login_update_through_terminal(self):
        answers = ['2', 'Htet Myet Zaw', '23456', '23456', '10000',
                   '1', 'Htet Myet Zaw', '23456',
                   '3', 'Htet Zaw', '34567', '34567', '9500', '0', '0']
        with patch('main.Bank', return_value=self.bank), \
             patch('builtins.input', side_effect=answers), patch('builtins.print'):
            main()
        restored = Bank(self.path)
        username = restored.login('Htet Zaw', '34567')
        self.assertEqual(restored.accounts[username]['balance'], Decimal('9500.00'))


if __name__ == '__main__':
    unittest.main()
