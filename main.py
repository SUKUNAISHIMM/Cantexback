import asyncio
from worker import run_swaps

if __name__ == "__main__":
    asyncio.run(run_swaps())
