import asyncio
import logging
from cantex_sdk import CantexSDK, OperatorKeySigner, IntentTradingKeySigner
from db import fetch_active_accounts, fetch_global_gas_threshold
from config import BASE_URL, POLL_INTERVAL_SEC, SWAP_TIMEOUT_SEC

async def process_account(acc):
    log = logging.getLogger(f"worker.{acc['name']}")
    operator = OperatorKeySigner.from_hex(acc["operator_key"])
    intent = IntentTradingKeySigner.from_hex(acc["trading_key"])

    async with CantexSDK(operator, intent, base_url=BASE_URL) as sdk:
        await sdk.authenticate()
        while True:
            try:
                gas_threshold = fetch_global_gas_threshold()
                # TODO: fetch balances, choose direction, get quote
                # TODO: check gas fee <= threshold
                # TODO: perform swap via sdk.swap_and_confirm()
                log.info("Worker tick for %s (threshold=%s)", acc["name"], gas_threshold)
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
