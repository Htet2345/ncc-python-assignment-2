"""Run this file to start the interactive assignment."""

from bank import Bank, valid_username


def account_menu(bank, username):
    while True:
        balance = bank.accounts[username]['balance']
        print(f'\n--- Account: {username} | Balance: {balance:,.2f} ---')
        print('1. Transfer money\n2. Withdraw money\n3. Update account\n0. Log out')
        choice = input('Choose an option: ').strip()
        try:
            if choice == '1':
                recipient = input('Recipient username: ')
                amount = input('Transfer amount: ')
                bank.transfer(username, recipient, amount)
                print('Transfer successful. Both balances have been saved.')
            elif choice == '2':
                bank.withdraw(username, input('Withdrawal amount: '))
                print('Withdrawal successful.')
            elif choice == '3':
                new_username = input('New username (Enter to keep current): ').strip()
                new_passcode = input('New passcode (Enter to keep current): ')
                if new_passcode and new_passcode != input('Confirm new passcode: '):
                    raise ValueError('Passcodes do not match.')
                new_balance = input('New balance (Enter to keep current): ').strip()
                username = bank.update(username, new_username, new_passcode,
                                       new_balance if new_balance else None)
                print('Account updated and saved.')
            elif choice == '0':
                print('Logged out.')
                return
            else:
                print('Choose 0, 1, 2, or 3.')
        except (ValueError, OSError) as error:
            print(f'Unable to complete operation: {error}')


def main():
    print('=====================================')
    print('       NCC BANKING ASSIGNMENT 2')
    print('=====================================')
    try:
        bank = Bank()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f'Cannot load account data: {error}')
        print('The existing file has been left unchanged. Check userlist.txt before restarting.')
        return

    while True:
        print('\n1. Login\n2. Register\n0. Exit')
        choice = input('Choose an option: ').strip()
        try:
            if choice == '1':
                username = input('Username: ')
                passcode = input('Passcode: ')
                username = bank.login(username, passcode)
                print(f'Welcome, {username}!')
                account_menu(bank, username)
            elif choice == '2':
                username = valid_username(input('Username / name (3-40 characters; spaces allowed): '))
                if username in bank.accounts:
                    raise ValueError('That username is already registered.')
                passcode = input('Passcode (4-12 digits): ')
                if passcode != input('Confirm passcode: '):
                    raise ValueError('Passcodes do not match.')
                amount = input('Starting balance: ')
                bank.register(username, passcode, amount)
                print('Registration successful. Choose Login to access your account.')
            elif choice == '0':
                print('Goodbye! Your account data is saved.')
                return
            else:
                print('Choose 0, 1, or 2.')
        except (ValueError, OSError) as error:
            print(f'Unable to complete operation: {error}')


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nProgram closed. Completed operations are already saved.')
