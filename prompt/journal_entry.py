from typing import Dict


def generate_prompt(t:Dict[str, str]) -> str:
  return f"""
  1. Predefined Account IDs:
  Use the following `account_ids` mapping. Account names in the transaction should be matched to
  these (case-insensitive, and common variations like "A/P" for "accounts_payable" should be
  recognized).

  ```json
  {{
    "account_ids": {{
      "cash": "J100",
      "accounts_receivable": "J150",
      "inventory": "J200",
      "prepaid_expenses": "J250",
      "equipment": "J300",
      "accumulated_depreciation": "J305",
      "accounts_payable": "L100",
      "unearned_revenue": "L150",
      "notes_payable": "L200",
      "common_stock": "Q100",
      "retained_earnings": "Q150",
      "sales_revenue": "R100",
      "service_revenue": "R110",
      "cost_of_goods_sold": "E100",
      "rent_expense": "E200",
      "salaries_expense": "E210",
      "utilities_expense": "E220",
      "office_supplies_expense": "E230"
    }}
  }}
  ```

  2. Output Format:
  Create a journal entry from this {t}, the journal entry should specify the accounts
  debited or credited. Your response MUST be a single JSON object strictly following this format:
  {{
    "date": "YYYY-MM-DD",
    "description": "Transaction description for the journal entry.",
    "debit": [
      {{
        "name": "account_name",
        "account_id": "ACCOUNT_ID",
        "amount": "numerical_amount_as_string"
      }}
    ],
    "credit": [
      {{
        "name": "account_name",
        "account_id": "ACCOUNT_ID",
        "amount": "numerical_amount_as_string"
      }}
    ]
  }}

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
  {{
    "date": "2024-08-17" #(yyyy-mm-dd),
    "description": "bought inventory worth $5000 from XYZ company with cash",
    "debit": [
      {{
        "name": "inventory",
        "account_id": "J200",
        "amount": "5000"
      }},
    ]
    "credit": [
      {{
        "name": "cash",
        "account_id": "J100",
        "amount": "5000"
      }},
    ]
  }}

  5. Key Accounting Principles to Adhere To:
  * Double-Entry System: For every transaction, total debits MUST equal total credits.
  * Account Identification: Correctly identify the accounts affected by the transaction based on
    standard accounting principles (e.g., an increase in an asset is a debit, an increase in a
    liability is a credit).

  Your response should strictly follow the structure of example output, , with no additional
  explanation or commentary.
  """