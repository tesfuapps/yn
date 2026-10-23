import asyncio
from database.models import init_db
from database.connection import close_pool, get_conn

async def main():
    await init_db()
    async with get_conn() as conn:
        print("get_conn OK")
    await close_pool()
    print("close_pool OK")

asyncio.run(main())
