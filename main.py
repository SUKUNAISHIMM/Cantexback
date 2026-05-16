from fastapi import FastAPI
from db import fetch_active_accounts, fetch_swap_history, fetch_global_gas_threshold
from models import Account, SwapHistory, GasThreshold

app = FastAPI(title="Cantex Trading Bot API")

@app.get("/accounts", response_model=list[Account])
def get_accounts():
    return fetch_active_accounts()

@app.get("/swap-history/{account_id}", response_model=list[SwapHistory])
def get_history(account_id: int):
    return fetch_swap_history(account_id)

@app.get("/gas-threshold", response_model=GasThreshold)
def get_threshold():
    return {"threshold": fetch_global_gas_threshold()}
