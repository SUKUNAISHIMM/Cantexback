from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from decimal import Decimal
from cantex_sdk import CantexSDK, OperatorKeySigner, IntentTradingKeySigner
from db import add_account, remove_account, get_accounts

app = FastAPI()

class Account(BaseModel):
    account_name: str
    operator_key: str
    trading_key: str

@app.post("/add_account")
def add_account_endpoint(account: Account):
    try:
        add_account(account.account_name, account.operator_key, account.trading_key)
        return {"status": "success", "message": "Account added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/remove_account/{account_id}")
def remove_account_endpoint(account_id: str):
    try:
        remove_account(account_id)
        return {"status": "success", "message": "Account removed"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/current_fee")
async def current_fee():
    accounts = get_accounts()
    if not accounts:
        return {"network_fee": None}

    account = accounts[0]  # use first account for monitoring
    operator = OperatorKeySigner.from_hex(account["operator_key"])
    intent = IntentTradingKeySigner.from_hex(account["trading_key"])

    async with CantexSDK(operator, intent) as sdk:
        await sdk.authenticate()
        quote = await sdk.get_swap_quote("CBTC", "USDCX", Decimal("0.1"))
        return {"network_fee": str(quote.network_fee)}
