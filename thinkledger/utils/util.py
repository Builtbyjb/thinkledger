import secrets


def generate_crypto_string(length: int=32) -> str:
    """
    Generates a unique URL-safe cryptographic string of the specified length.
    Args:
        length (int): Desired length of the output string. Defaults to 32.
    Returns:
        str: A cryptographically secure random string.
    """
    required_bytes = (length * 6 + 7) // 8  # Calculate bytes needed for the desired length
    token = secrets.token_urlsafe(required_bytes)
    return token[:length]


def time_format(time: float) -> str:
  """
  Formats time in seconds to milliseconds(ms), microseconds(us), or seconds(s) to 2 decimals
  places
  """
  # Set default to milliseconds
  t = time * 1000
  t_rep = "ms" # milliseconds

  if t >= 1000:
    t = t/1000
    t_rep = "s" # seconds
  elif t < 1:
    t = t * 1000
    t_rep = "us" # microseconds
  return f"{t:.2f} {t_rep}"


def invert_amount(amount: float) -> float:
  """
    Inverts the amount to be negative if it is positive, and positive if it is negative
  """
  if amount > 0: return -amount
  return abs(amount)