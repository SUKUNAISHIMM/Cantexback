
import asyncio
import os
import uvicorn
from worker import run_swaps
from api import app

async def start_worker():
    # Run your continuous swap loop
    await run_swaps()

def start_api():
    # Run FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # Launch worker in background
    loop.create_task(start_worker())
    # Launch API server
    start_api()
