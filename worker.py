import asyncio, datetime
from decimal import Decimal
from cantex_sdk import CantexSDK, OperatorKeySigner, IntentTradingKeySigner
from db import get_accounts, get_threshold, log_swap

DAILY_SWAP_LIMIT = 25

async def run_swaps():
    while True:
        accounts = get_accounts()
        threshold = Decimal(str(get_threshold()))

        for account in accounts:
            operator = OperatorKeySigner.from_hex(account["operator_key"])
            intent = IntentTradingKeySigner.from_hex(account["trading_key"])

            async with CantexSDK(operator, intent) as sdk:
                await sdk.authenticate()
                swaps_today = 0

                while swaps_today < DAILY_SWAP_LIMIT:
                    quote = await sdk.get_swap_quote("CBTC", "USDCX", Decimal("0.1"))

                    if quote.network_fee <= threshold:
                        result = await sdk.swap_and_confirm(
                            "CBTC", "USDCX", Decimal("0.1"),
                            maxNetworkFee=threshold
                        )
                        log_swap(
                            account_id=account["id"],
                            account_name=account["account_name"],
                            direction="CBTC→USDCX",
                            input_amount=Decimal("0.1"),
                            input_symbol="CBTC",
                            output_amount=result.output_amount,
                            output_symbol="USDCX",
                            price=result.price,
                            status=result.status,
                            network_fee=result.network_fee
                        )
                        swaps_today += 1
                    else:
                        # Retry quickly if fee too high
                        await asyncio.sleep(2)
