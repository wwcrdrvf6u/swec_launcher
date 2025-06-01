import os
import sys
import logging
import xml.etree.ElementTree as ET
import subprocess
import tkinter as tk
from tkinter import messagebox

# ========================
# Windows高DPI兼容性设置
# ========================
if sys.platform == 'win32':
    try:
        from ctypes import windll, WinDLL
        # 尝试新式DPI缩放
        shcore = WinDLL('shcore')
        shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError, WindowsError, ImportError):
        try:
            # 回退到旧式缩放
            windll.user32.SetProcessDPIAware()
        except:
            pass

# ========================
# 日志配置（兼容Python 3.8）
# ========================
log_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s: %(message)s'
)
file_handler = logging.FileHandler('launcher.log', mode='w', encoding='utf-8')
file_handler.setFormatter(log_formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

if sys.platform == 'win32':
    # Windows添加控制台输出
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

# ========================
# 主启动器类
# ========================
class EasiCameraLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # 跨平台DPI兼容设置
        self._configure_dpi()

    def _configure_dpi(self):
        """处理不同系统的DPI缩放"""
        if sys.platform == 'win32':
            # 已经通过ctypes设置
            pass
        else:
            # Linux/macOS的缩放设置
            self.root.tk.call('tk', 'scaling', 1.5)

    def load_config(self):
        """安全加载配置文件"""
        config_path = 'config.xml'
        try:
            if not os.path.exists(config_path):
                raise FileNotFoundError(f"配置文件 {config_path} 不存在")

            tree = ET.parse(config_path)
            exe_path = tree.findtext('ExecutablePath', '').strip()

            if not exe_path:
                raise ValueError("配置文件中 ExecutablePath 为空")

            # 标准化路径处理
            exe_path = os.path.normpath(exe_path)
            logger.info("配置文件解析成功")
            return exe_path

        except ET.ParseError as e:
            logger.error("XML解析失败: %s", str(e))
            messagebox.showerror(
                "配置错误",
                "配置文件格式不正确\n请使用设置程序修复"
            )
            sys.exit(2)
        except Exception as e:
            logger.error("配置加载失败: %s", str(e), exc_info=True)
            messagebox.showerror(
                "配置错误",
                f"无法读取配置: {str(e)}"
            )
            sys.exit(1)

    def validate_executable(self, path):
        """三级路径验证"""
        checks = [
            (os.path.exists, "路径不存在"),
            (os.path.isfile, "目标不是文件"),
            (lambda p: p.lower().endswith('.exe'), "非可执行文件")
        ]
        
        for check, msg in checks:
            if not check(path):
                logger.error("验证失败: %s - %s", msg, path)
                raise ValueError(f"{msg}: {path}")
        return True

    def launch(self):
        """主启动流程"""
        try:
            # 加载配置
            exe_path = self.load_config()
            logger.info("目标路径: %s", exe_path)

            # 验证路径
            self.validate_executable(exe_path)
            logger.info("路径验证通过")

            # 启动程序
            logger.info("正在启动程序...")
            process = subprocess.Popen(
                [exe_path],
                shell=(sys.platform == 'win32'),  # Windows需要shell处理空格
                cwd=os.path.dirname(exe_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # 等待进程启动
            timeout = 10 if sys.platform == 'win32' else 5
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                if process.returncode != 0:
                    logger.error(
                        "进程异常退出，代码%d\n输出：%s\n错误：%s",
                        process.returncode,
                        stdout,
                        stderr
                    )
            except subprocess.TimeoutExpired:
                logger.info("程序已后台运行")

            logger.info("启动流程完成")

        except Exception as e:
            logger.error("启动失败: %s", str(e), exc_info=True)
            messagebox.showerror(
                "启动失败",
                f"无法启动程序：{str(e)}\n详细信息请查看日志"
            )
            sys.exit(3)
        finally:
            self.root.destroy()

if __name__ == "__main__":
    launcher = EasiCameraLauncher()
    launcher.launch()
    sys.exit(0)