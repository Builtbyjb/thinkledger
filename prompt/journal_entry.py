from typing import Dict


def generate_prompt(t:Dict[str, str]) -> str:
  return f"""
  1. Predefined Account IDs:
  Use the following `account_ids` mapping. Account names in the transaction should be matched to
  these (case-insensitive, and common variations like "A/P" for "accounts_payable" should be
  recognized).

  ```json ("ACCOUNT_NAME":"ACCOUNT_ID")
  {{
    "account_ids": {{
      "Cash": "J100",
      "Accounts Receivable": "J149",
      "Inventory": "J200",
      "Prepaid Expenses": "J250",
      "Equipment": "J300",
      "Accumulated Depreciation": "J305",
      "Accounts Payable": "L100",
      "Unearned Revenue": "L150",
      "Notes Payable": "L200",
      "Common Stock": "Q100",
      "Retained Earnings": "Q150",
      "Sales Revenue": "R100",
      "Service Revenue": "R110",
      "Cost of Goods Sold": "E100",
      "Rent Expense": "E200",
      "Salaries Expense": "E210",
      "Utilities Expense": "E220",
      "Office Supplies Expense": "E230"
    }}
  }}
  ```
  2. Output Format:
  Create a journal entry from this {t}, the journal entry should specify the accounts
  debited or credited. Your response MUST be a single JSON object strictly following this format:
  ```json
  {{
    "date": "YYYY-MM-DD",
    "description": "Transaction description for the journal entry.",
    "debit": [
      {{
        "name": "ACCOUNT_NAME",
        "account_id": "ACCOUNT_ID",
        "amount": "numerical_amount_as_string"
      }}
    ],
    "credit": [
      {{
        "name": "ACCOUNT_NAME",
        "account_id": "ACCOUNT_ID",
        "amount": "numerical_amount_as_string"
      }}
    ]
  }}
  ```
  3. Field Descriptions and Rules:
  * Date: is the transaction date.
  * Description: A clear and concise description of the journal entry.  This should accurately
    reflect the nature of the {t}.
  * Debit: Is a list of all the accounts that are being debited.
  * Credit": Is a list of all the accounts that are being credited.
  * Name: The name of the account debited or credited.
  * Account ID: A id assigned to the account debited or credited. Select the corresponding
    account id for the account from the account_ids variable. If the account is not found in the
    variable create an account id following the same format.
  * Amount: The amount that is to be credited or debited

  4. Example Output:
  ```json
  {{
    "date": "2024-08-17" #(yyyy-mm-dd),
    "description": "bought inventory worth $5000 from XYZ company with cash",
    "debit": [
      {{
        "name": "Inventory",
        "account_id": "J200",
        "amount": "5000"
      }},
    ]
    "credit": [
      {{
        "name": "Cash",
        "account_id": "J100",
        "amount": "5000"
      }},
    ]
  }}
  ```
  5. Key Accounting Principles to Adhere To:
  * Double-Entry System: For every transaction, total debits MUST equal total credits.
  * Account Identification: Correctly identify the accounts affected by the transaction based on
    standard accounting principles (e.g., an increase in an asset is a debit, an increase in a
    liability is a credit).

  Your response should strictly follow the structure of example output, , with no additional
  explanation or commentary.
  """