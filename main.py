import asyncio
import os
import uvicorn
from worker import run_swaps
from api import app

async def start_worker():
    await run_swaps()

def start_api():
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

if __name__ == "__main__":
    # Explicitly create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Launch worker in background
    loop.create_task(start_worker())

    # Run API server (blocking call)
    start_api()
