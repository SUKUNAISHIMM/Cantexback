import os
from decimal import Decimal

DATABASE_URL = os.environ.get("DATABASE_URL")
BASE_URL = os.environ.get("CANTEX_BASE_URL", "https://api.cantex.io")
POLL_INTERVAL_SEC = int(os.environ.get("AUTO_SWAP_POLL_SEC", "3"))
SWAPS_PER_DIRECTION = int(os.environ.get("AUTO_SWAP_PER_DIRECTION", "25"))
SWAP_TIMEOUT_SEC = float(os.environ.get("AUTO_SWAP_TIMEOUT", "90"))
MIN_SWEEP_AMOUNT = Decimal(os.environ.get("AUTO_SWAP_MIN", "0"))
