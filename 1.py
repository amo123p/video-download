#!/usr/bin/env python3
"""
一键打包脚本 - 自动下载FFmpeg并打包成EXE
使用方法: python build_exe.py
"""

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
import tempfile
from pathlib import Path

# ==================== 配置 ====================
MAIN_SCRIPT = "video.py"  # 主程序文件名
APP_NAME = "VideoDownloader"          # 应用名称
APP_VERSION = "2.0"                   # 版本号
ICON_FILE = "icon.ico"               # 图标文件(可选)

# FFmpeg下载地址 (Windows版本)
FFMPEG_URL = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
# 备用地址
FFMPEG_URL_BACKUP = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"

# ==================== 颜色输出 ====================
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_color(text, color=Colors.GREEN):
    print(f"{color}{text}{Colors.END}")

def print_step(step, text):
    print(f"\n{Colors.BLUE}[{step}]{Colors.END} {Colors.BOLD}{text}{Colors.END}")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

# ==================== 工具函数 ====================
def run_command(cmd, check=True):
    """运行命令"""
    print(f"  执行: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
    result = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True)
    if check and result.returncode != 0:
        print_error(f"命令失败: {result.stderr}")
        return False
    return True

def download_file(url, dest, desc="文件"):
    """下载文件并显示进度"""
    print(f"  下载: {url[:80]}...")
    try:
        def reporthook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, downloaded * 100 / total_size)
                mb_down = downloaded / 1024 / 1024
                mb_total = total_size / 1024 / 1024
                sys.stdout.write(f"\r  进度: {percent:.1f}% ({mb_down:.1f}/{mb_total:.1f} MB)")
                sys.stdout.flush()
        
        urllib.request.urlretrieve(url, dest, reporthook)
        print()  # 换行
        return True
    except Exception as e:
        print_error(f"下载失败: {e}")
        return False

# ==================== 安装依赖 ====================
def install_dependencies():
    """安装打包所需依赖"""
    print_step(1, "安装打包依赖...")
    
    packages = ['pyinstaller', 'yt-dlp']
    
    for pkg in packages:
        print(f"  安装 {pkg}...")
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--upgrade', pkg],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print_success(f"{pkg} 安装成功")
        else:
            print_warning(f"{pkg} 安装可能有问题，继续...")
    
    return True

# ==================== 下载FFmpeg ====================
def download_ffmpeg(dest_dir):
    """下载并解压FFmpeg"""
    print_step(2, "下载 FFmpeg...")
    
    ffmpeg_dir = os.path.join(dest_dir, "ffmpeg")
    
    # 检查是否已存在
    if os.path.exists(os.path.join(ffmpeg_dir, "ffmpeg.exe")):
        print_success("FFmpeg 已存在，跳过下载")
        return ffmpeg_dir
    
    os.makedirs(ffmpeg_dir, exist_ok=True)
    
    # 下载
    zip_path = os.path.join(dest_dir, "ffmpeg.zip")
    
    # 尝试主地址
    if not download_file(FFMPEG_URL, zip_path, "FFmpeg"):
        print_warning("主地址失败，尝试备用地址...")
        if not download_file(FFMPEG_URL_BACKUP, zip_path, "FFmpeg"):
            print_error("FFmpeg 下载失败!")
            print_warning("请手动下载 FFmpeg 并放入 ffmpeg 文件夹")
            return None
    
    # 解压
    print("  解压 FFmpeg...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # 找到bin目录
            for name in zf.namelist():
                if name.endswith('ffmpeg.exe') or name.endswith('ffprobe.exe'):
                    # 提取文件名
                    filename = os.path.basename(name)
                    # 读取并写入目标
                    with zf.open(name) as src:
                        with open(os.path.join(ffmpeg_dir, filename), 'wb') as dst:
                            dst.write(src.read())
                    print_success(f"提取 {filename}")
        
        # 清理zip
        os.remove(zip_path)
        print_success("FFmpeg 准备完成")
        return ffmpeg_dir
        
    except Exception as e:
        print_error(f"解压失败: {e}")
        return None

# ==================== 修改程序以内置FFmpeg ====================
def patch_script_for_embedded_ffmpeg(script_path, output_path):
    """修改脚本以支持内置FFmpeg"""
    print_step(3, "修改程序以支持内置FFmpeg...")
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 添加内置FFmpeg检测代码
    patch_code = '''
# ========== 内置FFmpeg支持 ==========
def get_embedded_ffmpeg_path():
    """获取内置FFmpeg路径"""
    import sys
    import os
    
    # PyInstaller打包后的路径
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    ffmpeg_dir = os.path.join(base_path, 'ffmpeg')
    ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
    
    if os.path.exists(ffmpeg_exe):
        return ffmpeg_dir
    return None

# 在程序启动时设置FFmpeg路径
_embedded_ffmpeg = get_embedded_ffmpeg_path()
if _embedded_ffmpeg:
    import os
    os.environ['PATH'] = _embedded_ffmpeg + os.pathsep + os.environ.get('PATH', '')
# ========== 内置FFmpeg支持结束 ==========

'''
    
    # 在import之后插入
    import_end = content.find('def is_admin():')
    if import_end == -1:
        import_end = content.find('class ConfigManager')
    
    if import_end != -1:
        content = content[:import_end] + patch_code + content[import_end:]
    
    # 修改FFmpegManager的检测逻辑
    old_detect = 'def detect_ffmpeg(self):'
    new_detect = '''def detect_ffmpeg(self):
        # 优先检查内置FFmpeg
        embedded = get_embedded_ffmpeg_path()
        if embedded and self.validate_ffmpeg_path(embedded):
            return True
        '''
    
    content = content.replace(old_detect, new_detect)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print_success("程序已修改")
    return True

# ==================== PyInstaller打包 ====================
def build_exe(script_path, ffmpeg_dir):
    """使用PyInstaller打包"""
    print_step(4, "开始打包EXE...")
    
    # 构建PyInstaller命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                    # 单文件
        '--windowed',                   # 无控制台窗口
        f'--name={APP_NAME}',          # 输出名称
        '--clean',                      # 清理临时文件
        '--noconfirm',                  # 不确认覆盖
    ]
    
    # 添加图标
    if os.path.exists(ICON_FILE):
        cmd.append(f'--icon={ICON_FILE}')
        print(f"  使用图标: {ICON_FILE}")
    
    # 添加FFmpeg
    if ffmpeg_dir and os.path.exists(ffmpeg_dir):
        cmd.append(f'--add-data={ffmpeg_dir};ffmpeg')
        print(f"  内置FFmpeg: {ffmpeg_dir}")
    
    # 添加隐藏导入
    hidden_imports = [
        'yt_dlp',
        'yt_dlp.extractor',
        'yt_dlp.downloader',
        'yt_dlp.postprocessor',
    ]
    for imp in hidden_imports:
        cmd.append(f'--hidden-import={imp}')
    
    # 主脚本
    cmd.append(script_path)
    
    print(f"  命令: {' '.join(cmd)[:100]}...")
    
    # 执行打包
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print_success("打包成功!")
        return True
    else:
        print_error("打包失败!")
        return False

# ==================== 清理和整理 ====================
def cleanup_and_organize():
    """清理临时文件并整理输出"""
    print_step(5, "清理和整理...")
    
    # 创建发布目录
    release_dir = "release"
    os.makedirs(release_dir, exist_ok=True)
    
    # 移动EXE
    exe_path = f"dist/{APP_NAME}.exe"
    if os.path.exists(exe_path):
        dest = os.path.join(release_dir, f"{APP_NAME}_v{APP_VERSION}.exe")
        shutil.copy2(exe_path, dest)
        print_success(f"输出: {dest}")
        
        # 获取文件大小
        size_mb = os.path.getsize(dest) / 1024 / 1024
        print(f"  文件大小: {size_mb:.1f} MB")
    
    # 清理临时文件
    for item in ['build', '__pycache__', f'{APP_NAME}.spec']:
        if os.path.exists(item):
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)
    
    # 清理临时修改的脚本
    temp_script = f"{APP_NAME}_temp.py"
    if os.path.exists(temp_script):
        os.remove(temp_script)
    
    print_success("清理完成")
    return True

# ==================== 主函数 ====================
def main():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          🎬 视频下载器 一键打包工具 v{APP_VERSION}                ║
║                   内置 FFmpeg 版本                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # 检查主程序是否存在
    if not os.path.exists(MAIN_SCRIPT):
        print_error(f"找不到主程序: {MAIN_SCRIPT}")
        print("请确保此脚本和主程序在同一目录")
        return 1
    
    print(f"主程序: {MAIN_SCRIPT}")
    print(f"输出名称: {APP_NAME}.exe")
    print()
    
    # 确认
    input("按 Enter 开始打包 (Ctrl+C 取消)...")
    
    try:
        # 1. 安装依赖
        if not install_dependencies():
            return 1
        
        # 2. 下载FFmpeg
        ffmpeg_dir = download_ffmpeg(".")
        
        # 3. 修改脚本
        temp_script = f"{APP_NAME}_temp.py"
        if not patch_script_for_embedded_ffmpeg(MAIN_SCRIPT, temp_script):
            temp_script = MAIN_SCRIPT  # 使用原始脚本
        
        # 4. 打包
        if not build_exe(temp_script, ffmpeg_dir):
            return 1
        
        # 5. 清理
        cleanup_and_organize()
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    ✅ 打包完成!                               ║
╠══════════════════════════════════════════════════════════════╣
║  输出目录: release/                                          ║
║  文件名: {APP_NAME}_v{APP_VERSION}.exe                             ║
║                                                              ║
║  特性:                                                       ║
║  ✓ 单文件EXE，无需安装                                       ║
║  ✓ 内置FFmpeg，支持4K/8K下载                                 ║
║  ✓ 开箱即用                                                  ║
╚══════════════════════════════════════════════════════════════╝
        """)
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n已取消")
        return 1
    except Exception as e:
        print_error(f"打包失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())