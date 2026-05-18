from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_accounts():
    return supabase.table("accounts").select("*").execute().data

def get_threshold():
    result = supabase.table("global_settings").select("gas_threshold").execute().data
    return float(result[0]["gas_threshold"]) if result else 0.0

def log_swap(account_id, account_name, direction, input_amount, input_symbol,
             output_amount, output_symbol, price, status, network_fee):
    supabase.table("swap_history").insert({
        "account_id": account_id,
        "account_name": account_name,
        "direction": direction,
        "input_amount": f"{input_amount:.10f}",
        "input_symbol": input_symbol,
        "output_amount": f"{output_amount:.10f}",
        "output_symbol": output_symbol,
        "price": f"{price:.10f}",
        "status": status,
        "network_fee": f"{network_fee:.10f}"
    }).execute()

def add_account(account_name, operator_key, trading_key):
    return supabase.table("accounts").insert({
        "account_name": account_name,
        "operator_key": operator_key,
        "trading_key": trading_key
    }).execute()

def remove_account(account_id):
    return supabase.table("accounts").delete().eq("id", account_id).execute()
