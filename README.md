# 🎬 多平台视频下载器 V2.0

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![yt-dlp](https://img.shields.io/badge/yt--dlp-latest-green.svg)](https://github.com/yt-dlp/yt-dlp)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一款功能强大的视频下载工具，支持 YouTube、Bilibili、Twitter 等 1000+ 网站，支持 4K/8K 超高清视频下载。


## ✨ 功能特性

### 🎯 核心功能
- **多平台支持** - 支持 YouTube、Bilibili、Twitter、TikTok、Instagram 等 1000+ 网站
- **超高清下载** - 支持 4K/8K/HDR 视频下载
- **批量下载** - 支持多链接批量下载、播放列表、频道下载
- **多线程加速** - 分片多线程下载，速度更快
- **格式选择** - 视频+音频、仅视频、仅音频多种模式

### 🛠️ 高级特性
- **代理支持** - 支持 HTTP/HTTPS/SOCKS5 代理
- **Cookies 导入** - 支持从浏览器导入 Cookies，下载会员视频
- **自动合并** - 内置 FFmpeg 自动合并音视频流
- **字幕嵌入** - 自动下载并嵌入字幕
- **断点续传** - 支持下载中断后继续

### 💡 用户体验
- **深色主题** - 护眼深色界面
- **实时进度** - 下载进度、速度、剩余时间实时显示
- **配置持久化** - 自动保存用户配置
- **一键更新** - 内置 yt-dlp 更新功能

## 📸 界面截图

<details>
<summary>点击展开查看截图</summary>

### 主界面
![主界面](screenshots/main.png)

### 设置界面
![设置](screenshots/settings.png)

### 下载中
![下载](screenshots/downloading.png)

</details>

## 🚀 快速开始

### 方式一：打包 EXE（推荐）

1. 下载1.py
2. 自行打包
3. 双击运行即可使用

### 方式二：从源码运行

```bash
# 克隆项目
git clone https://github.com/amo123p/video-download.git
cd video-download

# 安装依赖
pip install -r requirements.txt

# 运行程序
python video.py
