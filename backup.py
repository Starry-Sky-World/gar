import threading
import threading
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import requests

from config import cfg
from utils import get_accounts_file_path


class WebDavBackupManager:
    """管理 WebDAV 备份的工具类"""

    def __init__(self, logger: Optional[Callable[[str], None]] = None):
        self._config = cfg.webdav
        self._logger = logger or print
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._scheduler_thread: Optional[threading.Thread] = None
        self._accounts_file = Path(get_accounts_file_path())

        self._apply_scheduler_state()

    def set_logger(self, logger: Callable[[str], None]) -> None:
        """设置日志输出函数"""
        if logger:
            self._logger = logger

    def update_accounts_file_path(self, path: str) -> None:
        """更新账号文件路径，便于自定义保存位置"""
        with self._lock:
            self._accounts_file = Path(path)

    def get_config(self, mask_password: bool = False) -> Dict:
        config_dict = asdict(self._config)
        if mask_password and config_dict.get("password"):
            config_dict["password"] = "***"
        return config_dict

    def update_config(
        self,
        *,
        enabled: Optional[bool] = None,
        url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        remote_dir: Optional[str] = None,
        interval_minutes: Optional[int] = None,
    ) -> None:
        """更新 WebDAV 配置并调整调度器"""
        with self._lock:
            if enabled is not None:
                self._config.enabled = bool(enabled)
            if url is not None:
                self._config.url = url.strip()
            if username is not None:
                self._config.username = username.strip()
            if password is not None:
                # 空字符串意味着清空密码
                self._config.password = password
            if remote_dir is not None:
                self._config.remote_dir = remote_dir.strip() or "oai_accounts"
            if interval_minutes is not None:
                try:
                    self._config.interval_minutes = max(0, int(interval_minutes))
                except ValueError:
                    self._logger("⚠️ WebDAV interval_minutes 必须是整数，已忽略此次更新")

        self._apply_scheduler_state()

    def _apply_scheduler_state(self) -> None:
        """根据当前配置启动或关闭定时任务"""
        if self._config.enabled and self._config.interval_minutes > 0:
            self._start_scheduler()
        else:
            self._stop_scheduler()

    def _start_scheduler(self) -> None:
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        self._logger(
            f"⏰ WebDAV 定时备份已启动，间隔 {self._config.interval_minutes} 分钟"
        )

    def _stop_scheduler(self) -> None:
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._stop_event.set()
            self._scheduler_thread.join(timeout=1)
            self._scheduler_thread = None
            self._stop_event.clear()
            self._logger("⏹️ 已停止 WebDAV 定时备份")

    def _scheduler_loop(self) -> None:
        while not self._stop_event.wait(self._config.interval_minutes * 60):
            self.backup(reason="scheduled")

    def backup(self, reason: str = "manual") -> Tuple[bool, str]:
        """执行一次备份"""
        with self._lock:
            config = asdict(self._config)
            accounts_file = self._accounts_file

        if not config.get("enabled"):
            return False, "WebDAV 备份未开启"

        if not config.get("url"):
            return False, "未配置 WebDAV 服务器地址"

        if not accounts_file.exists():
            return False, "账号文件不存在，跳过备份"

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        remote_dir = config.get("remote_dir") or "oai_accounts"
        remote_path = f"{remote_dir.strip('/')}/{timestamp}_accounts.txt"

        try:
            self._ensure_remote_dir(config["url"], remote_dir, config)
            self._upload_file(config["url"], remote_path, accounts_file, config)
            message = f"✅ 已备份账号文件 ({reason})"
            self._logger(message)
            return True, message
        except Exception as exc:  # noqa: BLE001
            message = f"❌ WebDAV 备份失败: {exc}"
            self._logger(message)
            return False, message

    def _ensure_remote_dir(self, base_url: str, remote_dir: str, config: Dict) -> None:
        """确保远端目录存在，兼容已存在返回码"""
        base = base_url.rstrip("/")
        auth = self._build_auth(config)
        segments = [s for s in remote_dir.strip("/").split("/") if s]
        current = ""

        for segment in segments:
            current += f"/{segment}"
            url = f"{base}{current}"
            resp = requests.request("MKCOL", url, auth=auth)
            if resp.status_code in {201, 301, 405, 409, 207}:
                continue
            if resp.status_code >= 400:
                raise RuntimeError(f"创建远端目录失败: {resp.status_code} {resp.text}")

    def _upload_file(
        self, base_url: str, remote_path: str, local_path: Path, config: Dict
    ) -> None:
        url = f"{base_url.rstrip('/')}/{remote_path}"
        with local_path.open("rb") as handle:
            resp = requests.put(url, data=handle, auth=self._build_auth(config))
            if resp.status_code not in {200, 201, 204}:
                raise RuntimeError(f"上传失败: {resp.status_code} {resp.text}")

    def _build_auth(self, config: Dict):
        if config.get("username") or config.get("password"):
            return (config.get("username", ""), config.get("password", ""))
        return None


# 全局备份管理器实例
backup_manager = WebDavBackupManager()
