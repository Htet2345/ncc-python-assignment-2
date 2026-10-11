"""Banking assignment: account operations and persistent text-file storage."""

import csv
import hashlib
import hmac
import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent / 'userlist.txt'
FIELDS = ['username', 'salt', 'passcode_hash', 'balance']


def money(value, allow_zero=False):
    """Validate money without the rounding errors of floating-point numbers."""
    try:
        amount = Decimal(str(value))
    except InvalidOperation:
        raise ValueError('Enter a valid amount, for example 1000 or 25.50.') from None
    if not amount.is_finite() or amount < 0 or (amount == 0 and not allow_zero):
        raise ValueError('Amount must be positive.' if not allow_zero else 'Amount cannot be negative.')
    if amount > Decimal('999999999999.99'):
        raise ValueError('Amount is too large.')
    if amount != amount.quantize(Decimal('0.01')):
        raise ValueError('Use at most two decimal places.')
    return amount.quantize(Decimal('0.01'))


def valid_username(value):
    username = ' '.join(value.split()).casefold()
    if not 3 <= len(username) <= 40 or not all(character.isalnum() or character in ' _' for character in username):
        raise ValueError('Username must contain 3-40 letters, numbers, spaces, or underscores.')
    return username


def hash_passcode(passcode, salt):
    return hashlib.pbkdf2_hmac('sha256', passcode.encode(), bytes.fromhex(salt), 100000).hex()


def passcode_fields(passcode):
    if not re.fullmatch(r'[0-9]{4,12}', passcode):
        raise ValueError('Passcode must contain 4-12 digits.')
    salt = os.urandom(16).hex()
    return salt, hash_passcode(passcode, salt)


class Bank:
    """Load file records into a dictionary, then save after each change."""

    def __init__(self, path=DATA_FILE):
        self.path = Path(path)
        self.accounts = self.load()

    def load(self):
        if not self.path.exists():
            return {}
        accounts = {}
        with self.path.open('r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            if reader.fieldnames != FIELDS:
                raise ValueError('userlist.txt has an invalid header. Restore a valid backup.')
            for row in reader:
                if set(row) != set(FIELDS) or any(value is None for value in row.values()):
                    raise ValueError('userlist.txt contains an incomplete or invalid record.')
                username = valid_username(row['username'])
                if username in accounts or row['username'] != username:
                    raise ValueError('userlist.txt contains duplicate or invalid usernames.')
                if not re.fullmatch(r'[0-9a-f]{32}', row.get('salt') or ''):
                    raise ValueError('userlist.txt contains an invalid passcode salt.')
                if not re.fullmatch(r'[0-9a-f]{64}', row.get('passcode_hash') or ''):
                    raise ValueError('userlist.txt contains an invalid passcode hash.')
                row['balance'] = money(row['balance'], allow_zero=True)
                accounts[username] = row
        return accounts

    def save(self, accounts):
        # Replace the file only after every record is written successfully.
        temporary = self.path.with_name(self.path.name + '.tmp')
        try:
            with temporary.open('w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=FIELDS)
                writer.writeheader()
                for username in sorted(accounts):
                    writer.writerow(accounts[username])
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)
        self.accounts = accounts

    def copy_accounts(self):
        # Work on a copy so a failed save leaves memory and the file consistent.
        return {username: record.copy() for username, record in self.accounts.items()}

    def register(self, username, passcode, balance):
        username = valid_username(username)
        if username in self.accounts:
            raise ValueError('That username is already registered.')
        balance = money(balance, allow_zero=True)
        salt, hashed = passcode_fields(passcode)
        accounts = self.copy_accounts()
        accounts[username] = dict(username=username, salt=salt, passcode_hash=hashed, balance=balance)
        self.save(accounts)
        return username

    def login(self, username, passcode):
        username = valid_username(username)
        record = self.accounts.get(username)
        if not record or not hmac.compare_digest(hash_passcode(passcode, record['salt']), record['passcode_hash']):
            raise ValueError('Incorrect username or passcode.')
        return username

    def withdraw(self, username, amount):
        amount = money(amount)
        if amount > self.accounts[username]['balance']:
            raise ValueError('Insufficient balance.')
        accounts = self.copy_accounts()
        accounts[username]['balance'] -= amount
        self.save(accounts)

    def transfer(self, username, recipient, amount):
        recipient = valid_username(recipient)
        if recipient not in self.accounts:
            raise ValueError('Recipient account does not exist.')
        if recipient == username:
            raise ValueError('Choose another account to transfer to.')
        amount = money(amount)
        if amount > self.accounts[username]['balance']:
            raise ValueError('Insufficient balance.')
        accounts = self.copy_accounts()
        accounts[username]['balance'] -= amount
        accounts[recipient]['balance'] += amount
        money(accounts[recipient]['balance'], allow_zero=True)
        self.save(accounts)

    def update(self, username, new_username='', new_passcode='', new_balance=None):
        new_username = valid_username(new_username) if new_username else username
        if new_username != username and new_username in self.accounts:
            raise ValueError('That username is already registered.')
        accounts = self.copy_accounts()
        record = accounts.pop(username)
        record['username'] = new_username
        if new_passcode:
            record['salt'], record['passcode_hash'] = passcode_fields(new_passcode)
        if new_balance is not None:
            record['balance'] = money(new_balance, allow_zero=True)
        accounts[new_username] = record
        self.save(accounts)
        return new_username
