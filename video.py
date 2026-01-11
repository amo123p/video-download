import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import subprocess
import re
import json
import ctypes
from concurrent.futures import ThreadPoolExecutor
import time

# 检查并安装 yt-dlp
try:
    import yt_dlp
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    import yt_dlp


def is_admin():
    """检查是否以管理员身份运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def fix_proxy_protocol(proxy):
    """修正代理协议"""
    if not proxy:
        return proxy
    proxy = proxy.strip()
    local_hosts = ['127.0.0.1', 'localhost', '0.0.0.0']
    for host in local_hosts:
        if host in proxy and proxy.startswith('https://'):
            return proxy.replace('https://', 'http://', 1)
    return proxy


class ConfigManager:
    """配置管理器"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.config_dir = os.path.join(os.path.expanduser("~"), ".video_downloader")
        self.config_file = os.path.join(self.config_dir, "config.json")
        
        self.default_config = {
            "ffmpeg_path": "",
            "download_path": os.path.expanduser("~/Downloads"),
            "proxy": "",
            "cookies_browser": "",
            "cookies_file": "",
            "max_concurrent": 3,
            "thread_count": 8,
            "prefer_free_formats": False,  # 新增：是否优先免费格式
        }
        
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
        except Exception as e:
            print(f"创建配置目录失败: {e}")
            
        self.config = self.load_config()
        
    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    for key, value in self.default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
        except Exception as e:
            print(f"加载配置失败: {e}")
        return self.default_config.copy()
    
    def save_config(self):
        try:
            if not os.path.exists(self.config_dir):
                os.makedirs(self.config_dir)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
            
    def get(self, key, default=None):
        return self.config.get(key, self.default_config.get(key, default))
    
    def set(self, key, value):
        self.config[key] = value
        return self.save_config()
    
    def set_multiple(self, settings_dict):
        for key, value in settings_dict.items():
            self.config[key] = value
        return self.save_config()
    
    def reload(self):
        self.config = self.load_config()


class FFmpegManager:
    """FFmpeg 管理器"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.ffmpeg_path = None
        self.ffprobe_path = None
        self.is_available = False
        self.detect_ffmpeg()
        
    def detect_ffmpeg(self):
        custom_path = self.config.get("ffmpeg_path", "")
        if custom_path and self.validate_ffmpeg_path(custom_path):
            return True
        if self.check_system_ffmpeg():
            return True
        self.is_available = False
        return False
        
    def check_system_ffmpeg(self):
        try:
            kwargs = {}
            if sys.platform == 'win32':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True, **kwargs)
            self.ffmpeg_path = "ffmpeg"
            self.ffprobe_path = "ffprobe"
            self.is_available = True
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
            
    def validate_ffmpeg_path(self, path):
        if not path or not os.path.exists(path):
            return False
        if os.path.isdir(path):
            exe_name = "ffmpeg.exe" if sys.platform == 'win32' else "ffmpeg"
            ffmpeg_exe = os.path.join(path, exe_name)
            ffprobe_exe = os.path.join(path, "ffprobe.exe" if sys.platform == 'win32' else "ffprobe")
        else:
            dir_path = os.path.dirname(path)
            exe_name = "ffmpeg.exe" if sys.platform == 'win32' else "ffmpeg"
            ffmpeg_exe = os.path.join(dir_path, exe_name)
            ffprobe_exe = os.path.join(dir_path, "ffprobe.exe" if sys.platform == 'win32' else "ffprobe")
        if not os.path.exists(ffmpeg_exe):
            return False
        try:
            kwargs = {}
            if sys.platform == 'win32':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            subprocess.run([ffmpeg_exe, '-version'], capture_output=True, check=True, **kwargs)
            self.ffmpeg_path = ffmpeg_exe
            self.ffprobe_path = ffprobe_exe if os.path.exists(ffprobe_exe) else None
            self.is_available = True
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, OSError):
            return False
            
    def get_ffmpeg_location(self):
        if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg":
            return os.path.dirname(self.ffmpeg_path)
        return None
        
    def get_version(self):
        if not self.is_available:
            return None
        try:
            ffmpeg_cmd = self.ffmpeg_path or "ffmpeg"
            kwargs = {}
            if sys.platform == 'win32':
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            result = subprocess.run([ffmpeg_cmd, '-version'], capture_output=True, text=True, **kwargs)
            if result.stdout:
                return result.stdout.split('\n')[0]
        except:
            pass
        return "未知版本"


class DownloadTask:
    """下载任务"""
    def __init__(self, url, title=None):
        self.url = url
        self.title = title or url[:50]
        self.status = "等待中"
        self.progress = 0
        self.speed = ""
        self.eta = ""
        self.error = None
        self.completed = False
        self.cancelled = False
        self.resolution = ""  # 新增：实际下载分辨率


class DownloadManager:
    """下载管理器 - 支持多线程批量下载"""
    
    def __init__(self, app, max_workers=3):
        self.app = app
        self.max_workers = max_workers
        self.executor = None
        self.tasks = []
        self.current_futures = {}
        self.is_running = False
        self.lock = threading.Lock()
        
    def add_task(self, url, title=None):
        task = DownloadTask(url, title)
        self.tasks.append(task)
        return task
        
    def clear_tasks(self):
        self.tasks = []
        
    def start(self, ydl_opts_base):
        if self.is_running:
            return
        self.is_running = True
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
        for task in self.tasks:
            if not task.completed and not task.cancelled:
                future = self.executor.submit(self._download_task, task, ydl_opts_base.copy())
                self.current_futures[future] = task
                
    def _download_task(self, task, ydl_opts):
        try:
            task.status = "下载中"
            self.app.root.after(0, self.app.update_task_display)
            
            def progress_hook(d):
                if task.cancelled:
                    raise Exception("用户取消")
                if d['status'] == 'downloading':
                    try:
                        percent_str = d.get('_percent_str', '0%').strip()
                        task.progress = float(re.sub(r'[^\d.]', '', percent_str) or 0)
                        task.speed = d.get('_speed_str', 'N/A').strip()
                        task.eta = d.get('_eta_str', 'N/A').strip()
                        
                        # 获取分辨率信息
                        info = d.get('info_dict', {})
                        height = info.get('height', '')
                        width = info.get('width', '')
                        if height:
                            task.resolution = f"{height}p"
                        
                        task.status = f"下载中 {task.progress:.1f}%"
                        self.app.root.after(0, self.app.update_task_display)
                    except:
                        pass
                elif d['status'] == 'finished':
                    task.status = "处理中..."
                    self.app.root.after(0, self.app.update_task_display)
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 先获取信息
                try:
                    info = ydl.extract_info(task.url, download=False)
                    if info:
                        task.title = info.get('title', task.url[:50])
                        # 获取最高分辨率
                        formats = info.get('formats', [])
                        video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
                        if video_formats:
                            max_height = max(f.get('height', 0) for f in video_formats)
                            task.resolution = f"最高{max_height}p"
                        self.app.root.after(0, self.app.update_task_display)
                except:
                    pass
                
                # 下载
                ydl.download([task.url])
            
            task.status = f"✅ 完成 {task.resolution}"
            task.progress = 100
            task.completed = True
            
        except Exception as e:
            error_msg = str(e)
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            error_msg = ansi_escape.sub('', error_msg)
            task.status = f"❌ 失败"
            task.error = error_msg[:100]
            self.app.log(f"❌ {task.title[:30]}: {error_msg[:150]}")
            
        finally:
            self.app.root.after(0, self.app.update_task_display)
            self.app.root.after(0, self.app.check_all_completed)
            
    def cancel_all(self):
        for task in self.tasks:
            task.cancelled = True
        if self.executor:
            self.executor.shutdown(wait=False)
        self.is_running = False
        
    def shutdown(self):
        self.is_running = False
        if self.executor:
            self.executor.shutdown(wait=False)


class SettingsWindow:
    """设置窗口"""
    
    def __init__(self, parent, config, ffmpeg_manager, callback=None):
        self.parent = parent
        self.config = config
        self.ffmpeg_manager = ffmpeg_manager
        self.callback = callback
        
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ 设置")
        self.window.geometry("700x850")
        self.window.configure(bg='#2b2b2b')
        self.window.transient(parent)
        self.window.grab_set()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.center_window()
        self.create_widgets()
        self.load_current_settings()
        
    def center_window(self):
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - 350
        y = (self.window.winfo_screenheight() // 2) - 425
        self.window.geometry(f'+{x}+{y}')
        
    def load_current_settings(self):
        self.browser_var.set(self.config.get("cookies_browser", ""))
        self.cookies_file_var.set(self.config.get("cookies_file", ""))
        self.proxy_var.set(self.config.get("proxy", ""))
        self.ffmpeg_path_var.set(self.config.get("ffmpeg_path", ""))
        self.concurrent_var.set(self.config.get("max_concurrent", 3))
        self.thread_var.set(self.config.get("thread_count", 8))
        self.prefer_free_var.set(self.config.get("prefer_free_formats", False))
        self.update_ffmpeg_status()
        
    def create_widgets(self):
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ==================== Cookies 设置页 ====================
        cookies_frame = ttk.Frame(notebook, padding="15")
        notebook.add(cookies_frame, text="🍪 Cookies")
        
        if is_admin():
            warning_frame = tk.Frame(cookies_frame, bg='#ff4444', padx=10, pady=8)
            warning_frame.pack(fill=tk.X, pady=(0, 10))
            tk.Label(warning_frame, text="⚠️ 管理员模式！建议使用 Cookies 文件",
                    font=('微软雅黑', 10, 'bold'), fg='white', bg='#ff4444').pack(anchor=tk.W)
        
        # 浏览器选择
        browser_frame = ttk.LabelFrame(cookies_frame, text="从浏览器导入", padding="10")
        browser_frame.pack(fill=tk.X, pady=5)
        
        self.browser_var = tk.StringVar()
        browsers = [("不使用", ""), ("Chrome", "chrome"), ("Firefox", "firefox"), 
                   ("Edge", "edge"), ("Brave", "brave")]
        
        browser_inner = ttk.Frame(browser_frame)
        browser_inner.pack(fill=tk.X, pady=5)
        for i, (text, value) in enumerate(browsers):
            ttk.Radiobutton(browser_inner, text=text, variable=self.browser_var, 
                           value=value).grid(row=0, column=i, padx=10)
        
        # Cookies 文件
        file_frame = ttk.LabelFrame(cookies_frame, text="Cookies 文件 (推荐)", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        file_inner = ttk.Frame(file_frame)
        file_inner.pack(fill=tk.X, pady=5)
        
        self.cookies_file_var = tk.StringVar()
        ttk.Entry(file_inner, textvariable=self.cookies_file_var, 
                 font=('Consolas', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(file_inner, text="📂 浏览", command=self.browse_cookies_file, 
                  width=10).pack(side=tk.RIGHT)
        
        # ==================== 代理设置页 ====================
        proxy_frame = ttk.Frame(notebook, padding="15")
        notebook.add(proxy_frame, text="🌐 代理")
        
        warning = tk.Label(proxy_frame, text="⚠️ 本地代理请使用 http:// 而不是 https://",
                          font=('微软雅黑', 10, 'bold'), fg='#ff8800', bg='#2b2b2b')
        warning.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(proxy_frame, text="代理地址:").pack(anchor=tk.W)
        self.proxy_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=self.proxy_var, 
                 font=('Consolas', 12)).pack(fill=tk.X, pady=10)
        
        examples = """示例:
✅ http://127.0.0.1:7890 (Clash)
✅ http://127.0.0.1:7897 (Clash Verge)  
✅ socks5://127.0.0.1:1080"""
        tk.Label(proxy_frame, text=examples, justify=tk.LEFT,
                font=('Consolas', 10), fg='#888888', bg='#2b2b2b').pack(anchor=tk.W)
        
        btn_frame = ttk.Frame(proxy_frame)
        btn_frame.pack(anchor=tk.W, pady=10)
        ttk.Button(btn_frame, text="🔧 自动修正", command=self.auto_fix_proxy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ 清除", command=lambda: self.proxy_var.set("")).pack(side=tk.LEFT, padx=5)
        
        # ==================== 下载设置页 ====================
        download_frame = ttk.Frame(notebook, padding="15")
        notebook.add(download_frame, text="⚡ 下载设置")
        
        # 并发数
        concurrent_frame = ttk.LabelFrame(download_frame, text="同时下载数量", padding="10")
        concurrent_frame.pack(fill=tk.X, pady=5)
        
        self.concurrent_var = tk.IntVar(value=3)
        concurrent_inner = ttk.Frame(concurrent_frame)
        concurrent_inner.pack(fill=tk.X)
        
        ttk.Label(concurrent_inner, text="同时下载视频数:").pack(side=tk.LEFT)
        ttk.Spinbox(concurrent_inner, from_=1, to=10, textvariable=self.concurrent_var,
                   width=10, font=('Consolas', 12)).pack(side=tk.LEFT, padx=10)
        ttk.Label(concurrent_inner, text="(建议 1-5)").pack(side=tk.LEFT)
        
        # 线程数
        thread_frame = ttk.LabelFrame(download_frame, text="单视频下载线程", padding="10")
        thread_frame.pack(fill=tk.X, pady=10)
        
        self.thread_var = tk.IntVar(value=8)
        thread_inner = ttk.Frame(thread_frame)
        thread_inner.pack(fill=tk.X)
        
        ttk.Label(thread_inner, text="分片下载线程数:").pack(side=tk.LEFT)
        ttk.Spinbox(thread_inner, from_=1, to=32, textvariable=self.thread_var,
                   width=10, font=('Consolas', 12)).pack(side=tk.LEFT, padx=10)
        ttk.Label(thread_inner, text="(建议 4-16)").pack(side=tk.LEFT)
        
        # 格式偏好
        format_frame = ttk.LabelFrame(download_frame, text="格式偏好", padding="10")
        format_frame.pack(fill=tk.X, pady=10)
        
        self.prefer_free_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(format_frame, text="优先免费/开放格式 (VP9/AV1/Opus)", 
                       variable=self.prefer_free_var).pack(anchor=tk.W)
        
        tk.Label(download_frame, 
                text="💡 分片线程: 加速单个视频下载\n💡 同时下载数: 同时下载多个视频\n💡 4K视频通常是VP9/AV1编码，需要FFmpeg",
                justify=tk.LEFT, font=('微软雅黑', 9), fg='#888888', bg='#2b2b2b').pack(anchor=tk.W, pady=10)
        
        # ==================== FFmpeg 设置页 ====================
        ffmpeg_frame = ttk.Frame(notebook, padding="15")
        notebook.add(ffmpeg_frame, text="🎬 FFmpeg")
        
        status_frame = ttk.LabelFrame(ffmpeg_frame, text="状态", padding="10")
        status_frame.pack(fill=tk.X, pady=5)
        
        self.ffmpeg_status_label = ttk.Label(status_frame, text="检测中...")
        self.ffmpeg_status_label.pack(anchor=tk.W)
        
        self.ffmpeg_version_label = ttk.Label(status_frame, text="")
        self.ffmpeg_version_label.pack(anchor=tk.W)
        
        # 重要提示
        notice = tk.Label(ffmpeg_frame, 
                         text="⚠️ 下载4K/高码率视频必须安装FFmpeg！\n下载地址: https://ffmpeg.org/download.html",
                         font=('微软雅黑', 10, 'bold'), fg='#ff8800', bg='#2b2b2b', justify=tk.LEFT)
        notice.pack(anchor=tk.W, pady=10)
        
        path_frame = ttk.LabelFrame(ffmpeg_frame, text="FFmpeg 路径", padding="10")
        path_frame.pack(fill=tk.X, pady=10)
        
        path_inner = ttk.Frame(path_frame)
        path_inner.pack(fill=tk.X, pady=5)
        
        self.ffmpeg_path_var = tk.StringVar()
        ttk.Entry(path_inner, textvariable=self.ffmpeg_path_var, 
                 font=('Consolas', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(path_inner, text="📂 浏览", command=self.browse_ffmpeg, 
                  width=10).pack(side=tk.RIGHT)
        
        # ==================== 底部按钮 ====================
        bottom_frame = ttk.Frame(self.window)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(bottom_frame, text="关闭", command=self.on_close, 
                  width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="💾 保存", command=self.save_settings, 
                  width=15).pack(side=tk.RIGHT, padx=5)
        
    def browse_cookies_file(self):
        path = filedialog.askopenfilename(
            title="选择 Cookies 文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if path:
            self.cookies_file_var.set(path)
            self.browser_var.set("")
            
    def browse_ffmpeg(self):
        path = filedialog.askdirectory(title="选择 FFmpeg 文件夹")
        if path:
            self.ffmpeg_path_var.set(path)
            
    def auto_fix_proxy(self):
        proxy = self.proxy_var.get().strip()
        if proxy:
            fixed = fix_proxy_protocol(proxy)
            if not fixed.startswith(('http://', 'https://', 'socks')):
                fixed = 'http://' + fixed
            self.proxy_var.set(fixed)
            if fixed != proxy:
                messagebox.showinfo("已修正", f"代理已修正为:\n{fixed}")
                
    def update_ffmpeg_status(self):
        if self.ffmpeg_manager.is_available:
            self.ffmpeg_status_label.config(text="✅ FFmpeg 已就绪", foreground='#00ff00')
            version = self.ffmpeg_manager.get_version()
            if version:
                self.ffmpeg_version_label.config(text=f"版本: {version[:60]}")
        else:
            self.ffmpeg_status_label.config(text="❌ FFmpeg 未检测到 (无法下载4K)", foreground='#ff4444')
            
    def save_settings(self):
        try:
            proxy = fix_proxy_protocol(self.proxy_var.get().strip())
            
            settings = {
                "cookies_browser": self.browser_var.get(),
                "cookies_file": self.cookies_file_var.get().strip(),
                "proxy": proxy,
                "ffmpeg_path": self.ffmpeg_path_var.get().strip(),
                "max_concurrent": self.concurrent_var.get(),
                "thread_count": self.thread_var.get(),
                "prefer_free_formats": self.prefer_free_var.get(),
            }
            
            if self.config.set_multiple(settings):
                self.ffmpeg_manager.detect_ffmpeg()
                self.update_ffmpeg_status()
                messagebox.showinfo("成功", "✅ 设置已保存!")
                if self.callback:
                    self.callback()
            else:
                messagebox.showerror("失败", "保存失败!")
        except Exception as e:
            messagebox.showerror("错误", str(e))
            
    def on_close(self):
        self.window.destroy()


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 多平台视频下载器 v2.0 - 支持4K/8K")
        self.root.geometry("1050x900")
        self.root.configure(bg='#2b2b2b')
        
        self.config = ConfigManager()
        self.ffmpeg_manager = FFmpegManager(self.config)
        self.download_manager = None
        
        self.setup_styles()
        self.create_widgets()
        
        self.is_downloading = False
        self.update_status_display()
        self.show_config_status()
        
    def show_config_status(self):
        self.log(f"📁 配置: {self.config.config_file}")
        proxy = self.config.get("proxy")
        if proxy:
            self.log(f"🌐 代理: {proxy}")
        if self.ffmpeg_manager.is_available:
            self.log(f"🎬 FFmpeg: 已就绪 ✓")
        else:
            self.log(f"⚠️ FFmpeg: 未配置 (无法下载4K)")
        self.log("=" * 60)
        self.log("💡 提示: 一行一个链接，支持播放列表和频道")
        self.log("💡 4K/8K: 需要 FFmpeg + Cookies (部分需要Premium账号)")
        self.log("💡 选择'原始最高'获取视频最高可用画质")
        self.log("=" * 60)
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TLabelframe', background='#2b2b2b', foreground='#ffffff')
        style.configure('TLabelframe.Label', background='#2b2b2b', foreground='#00d4ff', 
                       font=('微软雅黑', 10, 'bold'))
        style.configure('TLabel', background='#2b2b2b', foreground='#ffffff', font=('微软雅黑', 9))
        style.configure('TButton', font=('微软雅黑', 10, 'bold'))
        style.configure('TRadiobutton', background='#2b2b2b', foreground='#ffffff', font=('微软雅黑', 9))
        style.configure('TCheckbutton', background='#2b2b2b', foreground='#ffffff', font=('微软雅黑', 9))
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ==================== 顶部 ====================
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="🎬 多平台视频下载器", font=('微软雅黑', 16, 'bold'), 
                fg='#00d4ff', bg='#2b2b2b').pack(side=tk.LEFT)
        
        ttk.Button(header_frame, text="⚙️ 设置", command=self.open_settings, 
                  width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Button(header_frame, text="🔄 更新yt-dlp", command=self.update_ytdlp, 
                  width=12).pack(side=tk.RIGHT, padx=5)
        
        self.status_bar = ttk.Frame(header_frame)
        self.status_bar.pack(side=tk.RIGHT, padx=20)
        
        self.ffmpeg_indicator = tk.Label(self.status_bar, text="", font=('Arial', 10), bg='#2b2b2b')
        self.ffmpeg_indicator.pack(side=tk.LEFT, padx=3)
        self.proxy_indicator = tk.Label(self.status_bar, text="", font=('Arial', 10), bg='#2b2b2b')
        self.proxy_indicator.pack(side=tk.LEFT, padx=3)
        
        # ==================== URL输入 (多行) ====================
        url_frame = ttk.LabelFrame(main_frame, text="📎 视频链接 (一行一个，支持播放列表)", padding="10")
        url_frame.pack(fill=tk.X, pady=5)
        
        url_container = ttk.Frame(url_frame)
        url_container.pack(fill=tk.X)
        
        self.url_text = scrolledtext.ScrolledText(url_container, height=5, wrap=tk.WORD,
                                                  font=('Consolas', 10), bg='#1e1e1e', fg='#ffffff',
                                                  insertbackground='#ffffff')
        self.url_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(url_container)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        ttk.Button(btn_frame, text="📋 粘贴", command=self.paste_urls, width=10).pack(pady=2)
        ttk.Button(btn_frame, text="🗑️ 清空", command=self.clear_urls, width=10).pack(pady=2)
        ttk.Button(btn_frame, text="📂 从文件", command=self.load_from_file, width=10).pack(pady=2)
        
        # ==================== 下载选项 ====================
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=5)
        
        # 左侧：下载类型
        left_frame = ttk.LabelFrame(options_frame, text="📥 下载类型", padding="8")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        self.download_type = tk.StringVar(value="video_audio")
        types = [("🎬 视频+音频", "video_audio"), ("🎥 仅视频", "video_only"), ("🎵 仅音频", "audio_only")]
        for text, value in types:
            ttk.Radiobutton(left_frame, text=text, variable=self.download_type, 
                           value=value, command=self.on_type_change).pack(anchor=tk.W, pady=2)
        
        # 中间：视频质量 - 重新设计
        self.quality_frame = ttk.LabelFrame(options_frame, text="📺 视频质量", padding="8")
        self.quality_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.quality_var = tk.StringVar(value="best")
        qualities = [
            ("🏆 原始最高 (推荐)", "best"),    # 修改文字更清晰
            ("8K (4320p)", "4320"),
            ("4K (2160p)", "2160"),
            ("2K (1440p)", "1440"),
            ("1080p Full HD", "1080"),
            ("720p HD", "720"),
            ("480p", "480"),
        ]
        for text, value in qualities:
            ttk.Radiobutton(self.quality_frame, text=text, variable=self.quality_var, 
                           value=value).pack(anchor=tk.W, pady=1)
        
        # 右侧：音频选项
        self.audio_frame = ttk.LabelFrame(options_frame, text="🎵 音频设置", padding="8")
        
        ttk.Label(self.audio_frame, text="格式:").pack(anchor=tk.W)
        self.audio_format = tk.StringVar(value="mp3")
        fmt_frame = ttk.Frame(self.audio_frame)
        fmt_frame.pack(anchor=tk.W)
        for text, value in [("MP3", "mp3"), ("M4A", "m4a"), ("FLAC", "flac"), ("OPUS", "opus")]:
            ttk.Radiobutton(fmt_frame, text=text, variable=self.audio_format, value=value).pack(side=tk.LEFT, padx=3)
        
        ttk.Label(self.audio_frame, text="质量:").pack(anchor=tk.W, pady=(5, 0))
        self.audio_quality = tk.StringVar(value="0")  # 0 = 最高质量
        qual_frame = ttk.Frame(self.audio_frame)
        qual_frame.pack(anchor=tk.W)
        for text, value in [("最高", "0"), ("320k", "320"), ("256k", "256"), ("192k", "192")]:
            ttk.Radiobutton(qual_frame, text=text, variable=self.audio_quality, value=value).pack(side=tk.LEFT, padx=3)
        
        # 高级选项
        adv_frame = ttk.LabelFrame(options_frame, text="🔧 选项", padding="8")
        adv_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        self.use_cookies = tk.BooleanVar(value=True)
        self.use_proxy = tk.BooleanVar(value=True)
        self.download_playlist = tk.BooleanVar(value=True)
        self.embed_subs = tk.BooleanVar(value=False)
        self.keep_original = tk.BooleanVar(value=False)  # 新增：保持原始格式
        
        ttk.Checkbutton(adv_frame, text="使用 Cookies", variable=self.use_cookies).pack(anchor=tk.W)
        ttk.Checkbutton(adv_frame, text="使用代理", variable=self.use_proxy).pack(anchor=tk.W)
        ttk.Checkbutton(adv_frame, text="下载播放列表", variable=self.download_playlist).pack(anchor=tk.W)
        ttk.Checkbutton(adv_frame, text="嵌入字幕", variable=self.embed_subs).pack(anchor=tk.W)
        ttk.Checkbutton(adv_frame, text="保持原始格式", variable=self.keep_original).pack(anchor=tk.W)
        
        # ==================== 保存路径 ====================
        path_frame = ttk.LabelFrame(main_frame, text="📁 保存位置", padding="8")
        path_frame.pack(fill=tk.X, pady=5)
        
        self.path_var = tk.StringVar(value=self.config.get("download_path"))
        ttk.Entry(path_frame, textvariable=self.path_var, font=('Consolas', 10)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(path_frame, text="📂 浏览", command=self.browse_path, width=10).pack(side=tk.RIGHT)
        
        # ==================== 操作按钮 ====================
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        self.info_btn = ttk.Button(action_frame, text="ℹ️ 获取信息", command=self.get_video_info, width=14)
        self.info_btn.pack(side=tk.LEFT, padx=5)
        
        self.download_btn = ttk.Button(action_frame, text="⬇️ 开始下载", command=self.start_download, width=18)
        self.download_btn.pack(side=tk.LEFT, padx=15)
        
        self.cancel_btn = ttk.Button(action_frame, text="⏹️ 取消全部", command=self.cancel_download, width=12, state='disabled')
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        self.stats_label = ttk.Label(action_frame, text="")
        self.stats_label.pack(side=tk.RIGHT, padx=10)
        
        # ==================== 任务列表 ====================
        task_frame = ttk.LabelFrame(main_frame, text="📋 下载任务", padding="5")
        task_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 任务列表 - 增加分辨率列
        columns = ('title', 'status', 'progress', 'speed', 'resolution')
        self.task_tree = ttk.Treeview(task_frame, columns=columns, show='headings', height=8)
        self.task_tree.heading('title', text='标题')
        self.task_tree.heading('status', text='状态')
        self.task_tree.heading('progress', text='进度')
        self.task_tree.heading('speed', text='速度')
        self.task_tree.heading('resolution', text='分辨率')
        
        self.task_tree.column('title', width=350)
        self.task_tree.column('status', width=120)
        self.task_tree.column('progress', width=80)
        self.task_tree.column('speed', width=100)
        self.task_tree.column('resolution', width=100)
        
        task_scroll = ttk.Scrollbar(task_frame, orient=tk.VERTICAL, command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=task_scroll.set)
        
        self.task_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        task_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ==================== 日志 ====================
        log_frame = ttk.LabelFrame(main_frame, text="📝 日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        log_toolbar = ttk.Frame(log_frame)
        log_toolbar.pack(fill=tk.X)
        ttk.Button(log_toolbar, text="🗑️ 清空", command=self.clear_log, width=10).pack(side=tk.RIGHT)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, font=('Consolas', 9),
                               bg='#1e1e1e', fg='#00ff00', insertbackground='#00ff00')
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        log_scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
    def update_status_display(self):
        if self.ffmpeg_manager.is_available:
            self.ffmpeg_indicator.config(text="[FFmpeg ✓]", fg='#00ff00')
        else:
            self.ffmpeg_indicator.config(text="[FFmpeg ✗]", fg='#ff4444')
        proxy = self.config.get("proxy", "")
        if proxy:
            self.proxy_indicator.config(text="[Proxy ✓]", fg='#00ff00')
        else:
            self.proxy_indicator.config(text="[Proxy ○]", fg='#888888')
            
    def open_settings(self):
        SettingsWindow(self.root, self.config, self.ffmpeg_manager, self.on_settings_closed)
        
    def on_settings_closed(self):
        self.config.reload()
        self.ffmpeg_manager.detect_ffmpeg()
        self.update_status_display()
        self.log("✅ 设置已更新")
        
    def update_ytdlp(self):
        def _update():
            self.log("🔄 正在更新 yt-dlp...")
            try:
                result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("✅ yt-dlp 更新成功! 建议重启程序")
                else:
                    self.log(f"❌ 更新失败")
            except Exception as e:
                self.log(f"❌ 更新出错: {e}")
        threading.Thread(target=_update, daemon=True).start()
        
    def on_type_change(self):
        dtype = self.download_type.get()
        if dtype == "audio_only":
            self.quality_frame.pack_forget()
            self.audio_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, after=self.quality_frame.master.winfo_children()[0])
        else:
            self.audio_frame.pack_forget()
            self.quality_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
            
    def paste_urls(self):
        try:
            urls = self.root.clipboard_get()
            self.url_text.insert(tk.END, urls + "\n")
            self.log(f"📋 已粘贴链接")
        except:
            self.log("❌ 剪贴板为空")
            
    def clear_urls(self):
        self.url_text.delete(1.0, tk.END)
        
    def load_from_file(self):
        path = filedialog.askopenfilename(title="选择链接文件", 
                                          filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    urls = f.read()
                self.url_text.insert(tk.END, urls)
                self.log(f"📂 已加载文件: {os.path.basename(path)}")
            except Exception as e:
                self.log(f"❌ 读取文件失败: {e}")
                
    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.path_var.get())
        if path:
            self.path_var.set(path)
            self.config.set("download_path", path)
            
    def log(self, message):
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_message = ansi_escape.sub('', str(message))
        self.log_text.insert(tk.END, clean_message + "\n")
        self.log_text.see(tk.END)
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def get_urls(self):
        """获取所有URL"""
        text = self.url_text.get(1.0, tk.END)
        urls = []
        for line in text.strip().split('\n'):
            line = line.strip()
            if line and (line.startswith('http') or line.startswith('www')):
                if line.startswith('www'):
                    line = 'https://' + line
                urls.append(line)
        return urls
        
    def get_ydl_opts(self, for_info_only=False):
        """获取 yt-dlp 配置 - 完全修复最高画质下载"""
        download_path = self.path_var.get()
        download_type = self.download_type.get()
        quality = self.quality_var.get()
        
        opts = {
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'nocheckcertificate': True,
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            # 多线程下载分片
            'concurrent_fragment_downloads': self.config.get("thread_count", 8),
            # 🔑 关键：允许不安全的扩展名（某些高分辨率格式需要）
            'allow_unplayable_formats': False,
        }
        
        # 播放列表设置
        if not self.download_playlist.get():
            opts['noplaylist'] = True
        else:
            opts['yes_playlist'] = True
        
        # Cookies - 4K视频通常需要
        if self.use_cookies.get():
            cookies_file = self.config.get("cookies_file", "")
            cookies_browser = self.config.get("cookies_browser", "")
            if cookies_file and os.path.exists(cookies_file):
                opts['cookiefile'] = cookies_file
            elif cookies_browser:
                opts['cookiesfrombrowser'] = (cookies_browser,)
                
        # 代理
        if self.use_proxy.get():
            proxy = fix_proxy_protocol(self.config.get("proxy", ""))
            if proxy:
                opts['proxy'] = proxy
                
        # FFmpeg
        ffmpeg_location = self.ffmpeg_manager.get_ffmpeg_location()
        if ffmpeg_location:
            opts['ffmpeg_location'] = ffmpeg_location
            
        # ========== 🔥 核心修复：格式选择 ==========
        if download_type == "audio_only":
            audio_fmt = self.audio_format.get()
            audio_qual = self.audio_quality.get()
            
            # 选择最佳音频
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_fmt,
                'preferredquality': audio_qual if audio_qual != "0" else "0",
            }]
            
        elif download_type == "video_only":
            if quality == "best":
                # 🔑 使用 bv* 获取所有视频格式中的最佳
                opts['format'] = 'bv*[vcodec!^=none]/bv*/best'
                # 强制按分辨率排序，最高优先
                opts['format_sort'] = ['res:4320', 'res']  # 最高支持8K
            else:
                opts['format'] = f'bv*[height<={quality}]/bv*/best[height<={quality}]/best'
                
        else:  # video_audio - 最常用
            if quality == "best":
                # 🔑🔑🔑 关键修复：获取绝对最高画质
                # bv* = 最佳视频（包括所有编码格式）
                # ba = 最佳音频
                # /b = 备选：合并格式
                opts['format'] = 'bv*+ba/b'
                
                # 🔥 强制格式排序 - 分辨率最优先
                opts['format_sort'] = [
                    'res:4320',     # 优先8K
                    'res:2160',     # 然后4K
                    'res:1440',     # 然后2K
                    'res',          # 然后按分辨率排序
                    'vcodec:vp9.2', # VP9 Profile 2 (HDR)
                    'vcodec:vp9',   # VP9
                    'vcodec:av01',  # AV1
                    'vcodec:avc',   # H.264
                    'acodec:opus',  # Opus音频
                    'acodec:aac',   # AAC音频
                ]
                
                # 🔑 强制使用我们的排序规则
                opts['format_sort_force'] = True
                
            else:
                # 指定分辨率
                opts['format'] = f'bv*[height<={quality}]+ba/b[height<={quality}]/b'
                opts['format_sort'] = ['res', 'vcodec:vp9', 'acodec:opus']
            
            # 输出容器格式 - 不强制，让yt-dlp自动选择
            if not self.keep_original.get():
                # mkv 兼容性最好，支持几乎所有编码
                opts['merge_output_format'] = 'mkv'
                # 如果用户想要mp4，可能会限制某些编码
                # opts['merge_output_format'] = 'mp4'
            # else: 保持原始格式，不设置 merge_output_format
            
        # 字幕
        if self.embed_subs.get():
            opts['writesubtitles'] = True
            opts['writeautomaticsub'] = True
            opts['subtitleslangs'] = ['zh', 'en', 'zh-Hans', 'zh-Hant', 'ja', 'ko']
            opts.setdefault('postprocessors', []).append({
                'key': 'FFmpegEmbedSubtitle',
            })
            
        return opts
        
    def get_video_info(self):
        urls = self.get_urls()
        if not urls:
            messagebox.showerror("错误", "请输入视频链接")
            return
        self.info_btn.config(state='disabled')
        threading.Thread(target=self._get_info, args=(urls,), daemon=True).start()
        
    def _get_info(self, urls):
        try:
            opts = self.get_ydl_opts(for_info_only=True)
            opts['quiet'] = True
            
            self.log(f"\n🔍 正在获取 {len(urls)} 个链接的信息...")
            
            for url in urls[:5]:  # 最多显示5个
                try:
                    with yt_dlp.YoutubeDL(opts) as ydl:
                        info = ydl.extract_info(url, download=False)
                        
                        if info.get('_type') == 'playlist':
                            entries = info.get('entries', [])
                            self.log(f"\n📁 播放列表: {info.get('title', 'N/A')}")
                            self.log(f"   视频数量: {len(entries)}")
                        else:
                            self.log("=" * 60)
                            self.log(f"📹 标题: {info.get('title', 'N/A')}")
                            self.log(f"⏱️ 时长: {self.format_duration(info.get('duration', 0))}")
                            
                            # 详细分析可用格式
                            formats = info.get('formats', [])
                            video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
                            
                            if video_formats:
                                # 按分辨率分组
                                res_info = {}
                                for f in video_formats:
                                    h = f.get('height', 0)
                                    vcodec = f.get('vcodec', 'unknown')
                                    ext = f.get('ext', '?')
                                    key = h
                                    if key not in res_info:
                                        res_info[key] = []
                                    res_info[key].append(f"{vcodec[:10]}|{ext}")
                                
                                # 显示所有分辨率
                                sorted_res = sorted(res_info.keys(), reverse=True)
                                res_str = ', '.join([f'{r}p' for r in sorted_res[:8]])
                                self.log(f"📺 可用画质: {res_str}")
                                
                                # 显示最高分辨率的详细信息
                                max_res = sorted_res[0] if sorted_res else 0
                                best_formats = [f for f in video_formats if f.get('height') == max_res]
                                
                                if best_formats:
                                    # 找到最佳格式
                                    best = max(best_formats, key=lambda x: (
                                        x.get('filesize') or x.get('filesize_approx') or 0,
                                        x.get('vbr') or 0
                                    ))
                                    
                                    vcodec = best.get('vcodec', 'N/A')
                                    ext = best.get('ext', 'N/A')
                                    vbr = best.get('vbr', 0)
                                    filesize = best.get('filesize') or best.get('filesize_approx') or 0
                                    
                                    size_str = f"{filesize/1024/1024:.1f}MB" if filesize else "未知"
                                    vbr_str = f"{vbr:.0f}kbps" if vbr else "N/A"
                                    
                                    self.log(f"🏆 最高: {max_res}p | 编码: {vcodec} | 格式: {ext}")
                                    self.log(f"   码率: {vbr_str} | 大小: {size_str}")
                                    
                                    # 显示其他高分辨率选项
                                    for res in sorted_res[1:4]:
                                        codecs = set([c.split('|')[0] for c in res_info[res]])
                                        self.log(f"   {res}p: {', '.join(codecs)}")
                                        
                except Exception as e:
                    self.log(f"❌ 获取失败: {str(e)[:100]}")
                    
            self.log("=" * 60)
        finally:
            self.root.after(0, lambda: self.info_btn.config(state='normal'))
            
    def format_duration(self, seconds):
        if not seconds:
            return "N/A"
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"
        
    def start_download(self):
        urls = self.get_urls()
        if not urls:
            messagebox.showerror("错误", "请输入视频链接")
            return
            
        quality = self.quality_var.get()
        if quality == "best" and not self.ffmpeg_manager.is_available:
            result = messagebox.askyesno("警告", 
                "⚠️ FFmpeg 未配置！\n\n"
                "4K/8K 等高分辨率视频需要 FFmpeg 来合并视频和音频流。\n"
                "没有 FFmpeg 可能只能下载到 720p 或更低。\n\n"
                "建议：\n"
                "1. 下载 FFmpeg: https://ffmpeg.org/download.html\n"
                "2. 在设置中配置 FFmpeg 路径\n\n"
                "是否仍要继续？")
            if not result:
                return
        
        # 清空任务列表
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
            
        self.is_downloading = True
        self.download_btn.config(state='disabled')
        self.cancel_btn.config(state='normal')
        
        # 创建下载管理器
        max_concurrent = self.config.get("max_concurrent", 3)
        self.download_manager = DownloadManager(self, max_workers=max_concurrent)
        
        # 添加任务
        for url in urls:
            task = self.download_manager.add_task(url)
            self.task_tree.insert('', tk.END, iid=id(task), 
                                 values=(task.title[:50], task.status, f"{task.progress}%", task.speed, task.resolution))
        
        self.log(f"\n{'='*60}")
        self.log(f"🚀 开始下载 {len(urls)} 个链接")
        self.log(f"📁 保存到: {self.path_var.get()}")
        self.log(f"📺 画质: {'原始最高' if quality == 'best' else quality + 'p'}")
        self.log(f"⚡ 同时下载: {max_concurrent} | 线程: {self.config.get('thread_count', 8)}")
        self.log(f"🎬 FFmpeg: {'✓' if self.ffmpeg_manager.is_available else '✗ (可能限制画质)'}")
        self.log(f"{'='*60}")
        
        # 开始下载
        ydl_opts = self.get_ydl_opts()
        
        # 调试输出format设置
        self.log(f"📋 Format: {ydl_opts.get('format', 'N/A')}")
        if 'format_sort' in ydl_opts:
            self.log(f"📋 Sort: {ydl_opts.get('format_sort', [])[:3]}...")
        
        self.download_manager.start(ydl_opts)
        
    def update_task_display(self):
        """更新任务列表显示"""
        if not self.download_manager:
            return
            
        completed = 0
        failed = 0
        
        for task in self.download_manager.tasks:
            try:
                self.task_tree.item(id(task), values=(
                    task.title[:50] + "..." if len(task.title) > 50 else task.title,
                    task.status,
                    f"{task.progress:.1f}%",
                    task.speed,
                    task.resolution
                ))
                if task.completed:
                    completed += 1
                if task.error:
                    failed += 1
            except:
                pass
                
        total = len(self.download_manager.tasks)
        self.stats_label.config(text=f"完成: {completed}/{total} | 失败: {failed}")
        
    def check_all_completed(self):
        """检查是否全部完成"""
        if not self.download_manager:
            return
            
        all_done = all(task.completed or task.error or task.cancelled 
                      for task in self.download_manager.tasks)
        
        if all_done:
            completed = sum(1 for t in self.download_manager.tasks if t.completed)
            failed = sum(1 for t in self.download_manager.tasks if t.error)
            
            # 统计分辨率
            resolutions = [t.resolution for t in self.download_manager.tasks if t.completed and t.resolution]
            
            self.log(f"\n{'='*60}")
            self.log(f"🎉 下载完成! 成功: {completed} | 失败: {failed}")
            if resolutions:
                self.log(f"📺 下载画质: {', '.join(set(resolutions))}")
            self.log(f"📁 保存在: {self.path_var.get()}")
            self.log(f"{'='*60}")
            
            self.is_downloading = False
            self.download_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            
            if failed == 0:
                messagebox.showinfo("完成", f"✅ 全部下载完成!\n\n成功: {completed} 个")
            else:
                messagebox.showwarning("完成", f"下载完成\n\n成功: {completed} 个\n失败: {failed} 个")
                
    def cancel_download(self):
        if self.download_manager:
            self.download_manager.cancel_all()
        self.is_downloading = False
        self.download_btn.config(state='normal')
        self.cancel_btn.config(state='disabled')
        self.log("\n⏹️ 已取消所有下载")


def main():
    root = tk.Tk()
    
    if is_admin():
        if not messagebox.askyesno("警告", 
            "检测到管理员模式运行！\n可能无法读取浏览器 Cookies。\n\n继续？"):
            root.destroy()
            return
    
    app = VideoDownloaderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()