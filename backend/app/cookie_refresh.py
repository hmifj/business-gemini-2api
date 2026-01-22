"""Cookie 自动刷新模块
使用临时邮箱方式自动刷新过期的 Cookie
"""

import threading
import time
from datetime import datetime

# 创建一个事件用于触发立即刷新
_immediate_refresh_event = threading.Event()


def auto_refresh_account_cookie(account_idx, account):
    """
    自动刷新单个账号的 Cookie
    
    Args:
        account_idx: 账号索引
        account: 账号配置字典
    
    Returns:
        bool: 刷新是否成功
    """
    try:
        from .logger import print
        
        tempmail_name = account.get("tempmail_name", "")
        tempmail_url = account.get("tempmail_url", "")
        
        if not tempmail_name or not tempmail_url:
            print(f"[Cookie 刷新] 账号 {account_idx} 缺少临时邮箱信息，无法自动刷新", _level="WARNING")
            return False
        
        print(f"[Cookie 刷新] 开始刷新账号 {account_idx}: {tempmail_name}", _level="INFO")
        
        # 这里可以添加实际的刷新逻辑
        # 目前只是占位符，返回 False 表示需要手动刷新
        print(f"[Cookie 刷新] 账号 {account_idx} 需要通过前端面板手动刷新", _level="WARNING")
        return False
        
    except Exception as e:
        try:
            from .logger import print
            print(f"[Cookie 刷新] 账号 {account_idx} 刷新失败: {e}", _level="ERROR")
        except:
            pass
        return False


def auto_refresh_expired_cookies_worker():
    """
    后台线程：定期检查并刷新过期的 Cookie
    每 30 分钟检查一次
    """
    from .logger import print
    from .account_manager import account_manager
    
    check_interval = 30 * 60  # 30 分钟
    
    print("[Cookie 自动刷新] 后台线程已启动", _level="INFO")
    
    while True:
        try:
            # 等待检查间隔或立即刷新事件
            triggered = _immediate_refresh_event.wait(timeout=check_interval)
            
            if triggered:
                _immediate_refresh_event.clear()
                print("[Cookie 自动刷新] 收到立即刷新信号", _level="INFO")
            
            # 检查是否启用了自动刷新
            auto_refresh_enabled = account_manager.config.get("auto_refresh_cookie", False)
            if not auto_refresh_enabled:
                continue
            
            # 获取所有需要刷新的账号
            expired_accounts = []
            for i, acc in enumerate(account_manager.accounts):
                state = account_manager.account_states.get(i, {})
                cookie_expired = acc.get("cookie_expired", False) or state.get("cookie_expired", False)
                
                if cookie_expired:
                    expired_accounts.append((i, acc))
            
            if not expired_accounts:
                continue
            
            print(f"[Cookie 自动刷新] 发现 {len(expired_accounts)} 个过期账号", _level="INFO")
            
            # 逐个刷新
            for account_idx, account in expired_accounts:
                try:
                    success = auto_refresh_account_cookie(account_idx, account)
                    if success:
                        print(f"[Cookie 自动刷新] 账号 {account_idx} 刷新成功", _level="INFO")
                    else:
                        print(f"[Cookie 自动刷新] 账号 {account_idx} 刷新失败，需要手动刷新", _level="WARNING")
                    
                    # 每个账号之间间隔 30 秒
                    time.sleep(30)
                    
                except Exception as e:
                    print(f"[Cookie 自动刷新] 账号 {account_idx} 刷新异常: {e}", _level="ERROR")
                    continue
            
        except Exception as e:
            print(f"[Cookie 自动刷新] 后台线程异常: {e}", _level="ERROR")
            time.sleep(60)  # 出错后等待 1 分钟再继续


def trigger_immediate_refresh():
    """触发立即刷新检查"""
    _immediate_refresh_event.set()
