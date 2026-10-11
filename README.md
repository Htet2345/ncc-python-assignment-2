# NCC Python Assignment 2 - Banking

A terminal banking assignment with registration, login, transfer, withdrawal, updating the username/passcode/balance, persistent accounts in `userlist.txt`, and restoring saved accounts when the program starts.

## Run in VS Code on Windows

1. Double-click `setup.bat` in this folder. It reuses a working `.venv` or creates one using your installed Python, then checks the assignment imports. Python 3.10 or newer is required; no pip packages are needed. `requirements.txt` documents that the application has no third-party dependencies.
2. Open VS Code and choose **File > Open Folder**, then select `D:\ncc python assignment-2`.
3. Open Extensions (`Ctrl+Shift+X`) and install **Python** and **Python Debugger**, both published by Microsoft. They are also listed as workspace recommendations.
4. Press `Ctrl+Shift+P`, choose **Python: Select Interpreter**, and select `.venv\Scripts\python.exe`. If it is missing from the list, choose **Enter interpreter path** and browse to that file.
5. Press **F5** and select **Run banking assignment** if prompted. Answer prompts in the integrated Terminal. Passcodes are visible while you type; press Enter after typing.

After setup, you can also double-click `run.bat`, or run this in a VS Code PowerShell terminal:

```powershell
.\.venv\Scripts\python.exe main.py
```

No environment activation or PowerShell execution-policy changes are required. Use the integrated terminal for input.

## Try the banking system

1. Register `alice` with passcode `1234` and starting balance `1000`.
2. Register `bob` with passcode `5678` and starting balance `200`.
3. Log in as `alice`, transfer `150` to `bob`, then withdraw `50`. Alice now has `800`; Bob has `350`.
4. Choose Update account to change the username, passcode, or balance. Press Enter at a field to keep its current value. Directly changing the balance follows the teacher's diagram at approximately 05:30.
5. Log out and exit. Restart the program and log in again to check that the data persists.

The application starts without sample accounts. `userlist.txt` is created on the first successful registration. All amounts use the same unspecified currency, with up to two decimal places. This is an educational simulation; its starting balance is entered during registration. Names such as `Htet Myet Zaw` are accepted. Usernames have 3-40 letters, numbers, spaces, or underscores and are compared without case sensitivity. Repeated spaces are normalized.

## Files and concepts

| File | Purpose |
| --- | --- |
| `main.py` | Menus, input, output, and handling invalid operations |
| `bank.py` | Registration, login, transfer, withdrawal, updates, file reading/writing |
| `userlist.txt` | Automatically generated account records in CSV text format |
| `tests/test_bank.py` | Tests using temporary files; never changes your account data |
| `.vscode/` | Interpreter defaults, F5 debugger, extension recommendations, tasks |
| `setup.bat` / `run.bat` | Windows setup and launch shortcuts |
| `requirements.txt` | Confirms that no third-party runtime packages are needed |

At startup, `csv.DictReader` reads `userlist.txt` into an account dictionary. Changes are written with `csv.DictWriter` to a temporary file and then replace the saved file. `with open(...)` closes files automatically. `Decimal` keeps currency arithmetic exact. Exceptions produce readable error messages. Passcodes are stored as salted hashes instead of readable digits. Username comparisons are case insensitive.

Transfer validates the recipient and balance before updating both accounts together. Zero/negative transactions, duplicate usernames, invalid money, incorrect login details, and self-transfers are rejected. Updating an account lets you change its username, passcode, and balance, matching the teacher's diagram. A balance of zero is allowed during registration or an account update.

Run only one instance of the application at a time because storage is a local text file. If an existing data file is invalid, the program stops without overwriting it; restore a valid backup before continuing. To start over, close the application and move `userlist.txt` to a backup location, then restart.

## Run checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

You can also choose **Terminal > Run Task > Test banking assignment** in VS Code.
