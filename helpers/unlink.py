#!/usr/bin/env python3

import sys
import os
# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.plaid_utils import create_plaid_client
from plaid.model.item_remove_request import ItemRemoveRequest # type: ignore


def unlink_plaid_account() -> None:
  if len(sys.argv) != 2:
    print("Usage: python unlink.py <access_token>")
    return

  client = create_plaid_client()
  try:
    request = ItemRemoveRequest(access_token=sys.argv[1])
    response = client.item_remove(request)
    print(response)
    sys.exit("Account unlinked successfully")
  except Exception: sys.exit("Error unlinking account")


if __name__ == "__main__":
  unlink_plaid_account()