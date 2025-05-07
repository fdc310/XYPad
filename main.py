import asyncio

# 修改导入语句，确保导入正确的bot_core模块
try:
    # 先尝试使用相对导入（当前目录）
    from .bot_core import bot_core
except ImportError:
    # 如果相对导入失败，尝试使用绝对导入（当前目录）
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.append(current_dir)
    from bot_core import bot_core

async def main():
    try:
        bot = await bot_core()
        while True:
            await asyncio.sleep(1)
    except Exception as e:
        print(e)
        return
if __name__ == '__main__':
    asyncio.run(main())
