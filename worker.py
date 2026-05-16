import asyncio
import logging
from decimal import Decimal
from cantex_sdk import CantexSDK, OperatorKeySigner, IntentTradingKeySigner
from db import fetch_active_accounts, fetch_global_gas_threshold
from config import BASE_URL, POLL_INTERVAL_SEC, SWAP_TIMEOUT_SEC

# Define double‑leg routes
SWAP_ROUTES = {
    "CBTC-USDCX": ["CBTC-CC", "CC-USDCX"],
    "USDCX-CBTC": ["USDCX-CC", "CC-CBTC"],
}

async def perform_swap(sdk, route_key, amount):
    """Executes a double‑leg swap route."""
    legs = SWAP_ROUTES.get(route_key)
    if not legs:
        raise ValueError(f"No route defined for {route_key}")

    for leg in legs:
        base, quote = leg.split("-")
        quote_data = await sdk.get_quote(base, quote, amount)
        await sdk.swap_and_confirm(quote_data)
        amount = Decimal(str(quote_data["output_amount"]))  # carry output to next leg

async def process_account(acc):
    log = logging.getLogger(f"worker.{acc['name']}")
    operator = OperatorKeySigner.from_hex(acc["operator_key"])
    intent = IntentTradingKeySigner.from_hex(acc["trading_key"])

    async with CantexSDK(operator, intent, base_url=BASE_URL) as sdk:
        await sdk.authenticate()
        while True:
            try:
                gas_threshold = fetch_global_gas_threshold()
                # Example: decide direction dynamically
                direction = "CBTC-USDCX"  # or "USDCX-CBTC" based on balance logic
                amount = Decimal("0.01")  # example amount

                log.info("Starting double‑leg swap for %s (%s)", acc["name"], direction)
                await perform_swap(sdk, direction, amount)
                log.info("Completed double‑leg swap for %s", acc["name"])

            except Exception as e:
                log.error("Error in account %s: %s", acc["name"], e)
            await asyncio.sleep(POLL_INTERVAL_SEC)

async def main():
    accounts = fetch_active_accounts()
    tasks = [asyncio.create_task(process_account(acc)) for acc in accounts]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Stopped.")
