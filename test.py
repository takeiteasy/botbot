import asyncio
from botbot import DefaultBot
    
if __name__ == "__main__":
    bot = DefaultBot()
    asyncio.run(bot.run())