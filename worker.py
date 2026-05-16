import asyncio
import logging
from decimal import Decimal
from cantex_sdk import CantexSDK, OperatorKeySigner, IntentTradingKeySigner
from db import fetch_active_accounts, fetch_global_gas_threshold, db_connect
from config import BASE_URL, POLL_INTERVAL_SEC

def log_swap(account_id, account_name, route_key, quote_data, status):
    """Insert a single high-level swap record into swap_history."""
    base, quote = route_key.split("-")
    with db_connect() as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO swap_history (
                account_id, account_name, direction,
                input_amount, input_symbol,
                output_amount, output_symbol,
                price, status, network_fee, executed_at
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
        """, (
            account_id,
            account_name,
            route_key,
            quote_data["input_amount"],
            base,
            quote_data["output_amount"],
            quote,
            quote_data.get("price"),
            status,
            quote_data.get("network_fee"),
        ))

async def perform_swap(sdk, acc, route_key, amount, gas_threshold):
    """Perform a swap via Cantex, enforcing gas fee threshold."""
    base, quote = route_key.split("-")
    quote_data = await sdk.get_quote(base, quote, amount)

    # Block if fee exceeds threshold
    if gas_threshold and quote_data["network_fee"] > gas_threshold:
        logging.info("Swap blocked for %s: fee %s > threshold %s",
                     acc["name"], quote_data["network_fee"], gas_threshold)
        return

    try:
        await sdk.swap_and_confirm(quote_data)
        log_swap(acc["id"], acc["name"], route_key, quote_data, "Success")
    except Exception as e:
        log_swap(acc["id"], acc["name"], route_key, quote_data, f"Failed: {e}")
        raise

async def process_account(acc):
    log = logging.getLogger(f"worker.{acc['name']}")
    operator = OperatorKeySigner.from_hex(acc["operator_key"])
    intent = IntentTradingKeySigner.from_hex(acc["trading_key"])

    async with CantexSDK(operator, intent, base_url=BASE_URL) as sdk:
        await sdk.authenticate()
        while True:
            try:
                balances = await sdk.get_balances()
                cbtc_balance = Decimal(str(balances.get("CBTC", 0)))
                usdcx_balance = Decimal(str(balances.get("USDCX", 0)))
                gas_threshold = fetch_global_gas_threshold()

                # Decide which balance to swap
                if cbtc_balance > 0 and usdcx_balance > 0:
                    cbtc_quote = await sdk.get_quote("CBTC", "CC", cbtc_balance)
                    usdcx_quote = await sdk.get_quote("USDCX", "CC", usdcx_balance)
                    if Decimal(str(cbtc_quote["output_amount"])) >= Decimal(str(usdcx_quote["output_amount"])):
                        direction, amount = "CBTC-USDCX", cbtc_balance
                    else:
                        direction, amount = "USDCX-CBTC", usdcx_balance
                elif cbtc_balance > 0:
                    direction, amount = "CBTC-USDCX", cbtc_balance
                elif usdcx_balance > 0:
                    direction, amount = "USDCX-CBTC", usdcx_balance
                else:
                    log.info("No balance to swap for %s", acc["name"])
                    await asyncio.sleep(POLL_INTERVAL_SEC)
                    continue

                log.info("Swapping %s for %s (%s)", amount, acc["name"], direction)
                await perform_swap(sdk, acc, direction, amount, gas_threshold)

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
