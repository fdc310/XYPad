import asyncio
import json
import os
import sys
import time
import tomllib
from pathlib import Path

from loguru import logger

import WechatAPI
from database.XYBotDB import XYBotDB
from database.keyvalDB import KeyvalDB
from database.messsagDB import MessageDB
from utils.decorators import scheduler
from utils.plugin_manager import plugin_manager
from utils.xybot import XYBot

# 导入管理后台模块
try:
    # 正确设置导入路径
    admin_path = str(Path(__file__).resolve().parent)
    if admin_path not in sys.path:
        sys.path.append(admin_path)
    
    # 导入管理后台服务器模块
    try:
        from admin.server import set_bot_instance as admin_set_bot_instance
        logger.debug("成功导入admin.server.set_bot_instance")
    except ImportError as e:
        logger.error(f"导入admin.server.set_bot_instance失败: {e}")
        # 创建一个空函数
        def admin_set_bot_instance(bot):
            logger.warning("admin.server.set_bot_instance未导入，调用被忽略")
            return None
    
    # 直接定义状态更新函数，不依赖导入
    def update_bot_status(status, details=None, extra_data=None):
        """更新bot状态，供管理后台读取"""
        try:
            # 使用统一的路径写入状态文件 - 修复路径问题
            status_file = Path(admin_path) / "admin" / "bot_status.json"
            root_status_file = Path(admin_path) / "bot_status.json"
            
            # 读取当前状态
            current_status = {}
            if status_file.exists():
                with open(status_file, "r", encoding="utf-8") as f:
                    current_status = json.load(f)
            
            # 更新状态
            current_status["status"] = status
            current_status["timestamp"] = time.time()
            if details:
                current_status["details"] = details
            
            # 添加额外数据
            if extra_data and isinstance(extra_data, dict):
                for key, value in extra_data.items():
                    current_status[key] = value
            
            # 确保目录存在
            status_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入status_file
            with open(status_file, "w", encoding="utf-8") as f:
                json.dump(current_status, f)
            
            # 写入root_status_file
            with open(root_status_file, "w", encoding="utf-8") as f:
                json.dump(current_status, f)
                
            logger.debug(f"成功更新bot状态: {status}, 路径: {status_file} 和 {root_status_file}")
            
            # 输出更多调试信息
            if "nickname" in current_status:
                logger.debug(f"状态文件包含昵称: {current_status['nickname']}")
            if "wxid" in current_status:
                logger.debug(f"状态文件包含微信ID: {current_status['wxid']}")
            if "alias" in current_status:
                logger.debug(f"状态文件包含微信号: {current_status['alias']}")
                
        except Exception as e:
            logger.error(f"更新bot状态失败: {e}")
    
    # 定义设置bot实例的函数
    def set_bot_instance(bot):
        """设置bot实例到管理后台"""
        # 先调用admin模块的设置函数
        admin_set_bot_instance(bot)
        
        # 更新状态
        update_bot_status("initialized", "机器人实例已设置")
        logger.success("成功设置bot实例并更新状态")
        
        return bot
        
except ImportError as e:
    logger.error(f"导入管理后台模块失败: {e}")
    # 创建空函数，防止程序崩溃
    def set_bot_instance(bot):
        logger.warning("管理后台模块未正确导入，set_bot_instance调用被忽略")
        return None
    
    # 创建一个空的状态更新函数
    def update_bot_status(status, details=None):
        logger.debug(f"管理后台模块未正确导入，状态更新被忽略: {status}")


async def bot_core():
    # 设置工作目录
    script_dir = Path(__file__).resolve().parent
    os.chdir(script_dir)
    
    # 更新初始化状态
    update_bot_status("initializing", "系统初始化中")
    
    # 读取配置文件
    config_path = script_dir / "main_config.toml"
    try:
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        logger.success("读取主设置成功")
    except Exception as e:
        logger.error(f"读取主设置失败: {e}")
        return

    # 启动WechatAPI服务
    server = WechatAPI.WechatAPIServer()
    api_config = config.get("WechatAPIServer", {})
    redis_host = api_config.get("redis-host", "127.0.0.1")
    redis_port = api_config.get("redis-port", 6379)
    logger.debug("Redis 主机地址: {}:{}", redis_host, redis_port)
    server.start(port=api_config.get("port", 9000),
                 mode=api_config.get("mode", "release"),
                 redis_host=redis_host,
                 redis_port=redis_port,
                 redis_password=api_config.get("redis-password", ""),
                 redis_db=api_config.get("redis-db", 0))

    
        
    # 返回机器人实例（此处不会执行到，因为上面的无限循环）
    return 1
