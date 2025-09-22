# GXTRO 媒體下載工具
# 專案主頁：https://github.com/appy002255/GXTRO-exe
# 
# 更新日誌：
#   v1.05 (2025-06)
#     - 新增影片剪輯功能：支援時間裁剪、空間裁剪、解析度調整、播放速度調整
#     - 整合 VLC 播放器：支援影片預覽、截圖、音量控制、播放速度調整
#     - 新增浮水印功能：支援自訂位置、大小、透明度
#     - 新增背景音樂功能：支援混音、音量平衡
#     - 其他細節優化與錯誤修正
#     - 修正浮水印功能：優化 filter_complex 命令，確保正確映射音訊和視訊流
#     - 改進執行緒處理：使用 Qt 事件機制確保 UI 操作在主執行緒中執行
#     - 優化音訊處理：提升音訊品質，設定 192k 位元率
#     - 其他細節優化與錯誤修正
#   v1.03 (2025-05)
#     - LOGO區塊優化：左上角 icon 改為⬇️，字體現代感、亮藍色、字距寬，更時尚
#     - 新增「嵌入封面圖」與「嵌入作者資訊」兩個獨立選項，可自訂是否嵌入到 mp3/mp4
#     - 修正日誌區縮排問題，訊息顯示更穩定
#     - 其他細節優化與錯誤修正
#   v1.02 (2025-04)
#     - 預設暗色主題，所有元件完整黑色美化
#     - 支援多平台影片/直播下載，Instagram/TikTok/Bilibili URL 自動清理
#     - 支援畫質/格式選擇、影片封面預覽、簡潔/詳細日誌切換
#     - LOG 簡潔模式下 GUI 也完整顯示所有訊息
#     - "關於本程式"彈窗支援超連結與暗色美化
#     - 打包支援 yt-dlp.exe/ffmpeg 目錄
#     - 其他細節優化與錯誤修正
# 
# 說明：
#   - 支援 YouTube、Bilibili、Twitter、Facebook、Instagram、Vimeo、Twitch、TikTok 等多平台影片下載
#   - 支援部分平台直播下載
#   - 介面採用 PyQt5，支援暗色主題
#   - 內建畫質/格式選擇、影片封面預覽、簡潔/詳細日誌切換
#   - 自動清理與擷取網址，支援複製雜訊內容
#   - 免責聲明：僅供學術交流與個人用途，請勿用於非法用途
#   - 作者：巫毒高峰
#   - 授權：MIT License
#
# 使用方式、詳細說明請見 GitHub 專案頁。

import sys
import os
import socket
import threading
import subprocess
import re
import shutil
import psutil
import traceback
import time
import requests
from io import BytesIO
import tempfile
import json
from datetime import datetime
import ctypes
from ctypes.util import find_library
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, QSize, QCoreApplication, QUrl, QMetaObject
from github import Github # 移到頂部
import urllib.parse


class GitHubInstaller:
    def __init__(self, repo_owner, repo_name):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        try:
            # 使用 GitHub 個人訪問令牌進行認證
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            # 
            self.github = Github("github_pat_")# 請自行生成並填入
            print(f"DEBUG: 嘗試連接倉庫 {repo_owner}/{repo_name}")
            self.repo = self.github.get_repo(f"{repo_owner}/{repo_name}")
            print(f"DEBUG: 倉庫描述: {self.repo.description}")
            print(f"DEBUG: 倉庫 URL: {self.repo.html_url}")
            # 測試 API 連接
            releases = self.repo.get_releases()
            print(f"DEBUG: 倉庫發布數量: {releases.totalCount}")
            self.repo.get_releases()
            print("DEBUG: GitHub API 連接成功")
        except Exception as e:
            print(f"DEBUG: GitHub API 連接失敗: {str(e)}")
            raise Exception(f"無法連接到 GitHub API: {str(e)}")

    def get_latest_release(self):
        """獲取最新的發布版本"""
        try:
            print("DEBUG: 開始獲取最新版本")
            releases = self.repo.get_releases()
            latest_release = None
            latest_version = None

            print(f"DEBUG: 開始遍歷發布版本")
            for release in releases:
                print(f"DEBUG: 檢查發布版本: {release.tag_name}")
                # 修改正則表達式以匹配 gxtrov1.06 格式
                version_match = re.search(r'gxtrov?(\d+\.\d+)', release.tag_name)
                if version_match:
                    version = version_match.group(1)
                    print(f"DEBUG: 解析版本號: {version}")
                    if latest_version is None or version > latest_version:
                        latest_version = version
                        latest_release = release
                        print(f"DEBUG: 找到新版本 {version}")

            if latest_release:
                print(f"DEBUG: 最新版本是 {latest_release.tag_name}")
                return latest_release
            print("DEBUG: 沒有找到任何版本")
            return None

        except Exception as e:
            print(f"DEBUG: 獲取最新版本時出錯: {str(e)}")
            return None


class VersionCheckThread(QThread):
    update_available = pyqtSignal(str, str)
    no_update = pyqtSignal()
    error_checking = pyqtSignal(str)

    def __init__(self, current_version, repo_owner, repo_name):
        super().__init__()
        self.current_version = current_version
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def parse_version(self, version_str):
        """解析版本號字串為元組"""
        try:
            # 移除所有非數字和點的字元
            version_str = re.sub(r'[^\d.]', '', version_str)
            parts = version_str.split('.')
            # 確保至少有主版本號和次版本號
            while len(parts) < 2:
                parts.append('0')
            # 轉換為整數元組
            return tuple(map(int, parts))
        except Exception as e:
            print(f"DEBUG: 版本號解析錯誤: {str(e)}")
            return (0, 0, 0)

    def compare_versions(self, current, latest):
        """比較兩個版本號"""
        try:
            current_parts = self.parse_version(current)
            latest_parts = self.parse_version(latest)
            
            # 確保兩個版本號有相同數量的部分
            max_parts = max(len(current_parts), len(latest_parts))
            current_parts = current_parts + (0,) * (max_parts - len(current_parts))
            latest_parts = latest_parts + (0,) * (max_parts - len(latest_parts))
            
            return latest_parts > current_parts
        except Exception as e:
            print(f"DEBUG: 版本比較錯誤: {str(e)}")
            return False

    def run(self):
        try:
            print("DEBUG: 開始版本檢查")
            
            # 測試網路連接
            try:
                print("DEBUG: 測試 GitHub API 連接")
                response = requests.get("https://api.github.com", timeout=5)
                response.raise_for_status()
                print(f"DEBUG: GitHub API 響應狀態碼: {response.status_code}")
            except requests.RequestException as e:
                print(f"DEBUG: GitHub API 連接測試失敗: {str(e)}")
                self.error_checking.emit(f"無法連接到 GitHub: {str(e)}")
                return

            # 創建 GitHubInstaller 實例
            print("DEBUG: 創建 GitHubInstaller 實例")
            installer = GitHubInstaller(self.repo_owner, self.repo_name)
            latest_release = installer.get_latest_release()

            if latest_release:
                latest_tag_name = latest_release.tag_name
                print(f"DEBUG: 從 GitHub 獲取的最新標籤: {latest_tag_name}")
                
                # 從標籤名稱中提取版本號
                version_match = re.search(r'gxtrov?(\d+\.\d+(?:\.\d+)?)', latest_tag_name)
                if version_match:
                    latest_version_str = version_match.group(1)
                    print(f"DEBUG: 當前版本: {self.current_version}")
                    print(f"DEBUG: 最新版本: {latest_version_str}")
                    
                    # 比較版本
                    if self.compare_versions(self.current_version, latest_version_str):
                        release_url = latest_release.html_url
                        print(f"DEBUG: 發現新版本，發送更新信號")
                        self.update_available.emit(latest_tag_name, release_url)
                    else:
                        print("DEBUG: 當前已是最新版本")
                        self.no_update.emit()
                else:
                    print("DEBUG: 無法解析版本號")
                    self.error_checking.emit("無法解析最新版本號")
            else:
                print("DEBUG: 沒有找到發布版本")
                self.no_update.emit()
        except Exception as e:
            print(f"DEBUG: 版本檢查過程出錯: {str(e)}")
            self.error_checking.emit(f"檢查更新時發生錯誤: {str(e)}")

def get_base_path():
    """獲取應用程式的基本路徑"""
    if getattr(sys, 'frozen', False):
        # 如果是打包後的 exe
        return os.path.dirname(sys.executable)
    else:
        # 如果是開發環境
        return os.path.dirname(os.path.abspath(__file__))

def setup_vlc_environment():
    """設定 VLC 環境"""
    try:
        # 獲取基礎路徑
        base_path = get_base_path()
        print(f"基礎路徑：{base_path}")
        
        # 檢查 VLC 資料夾
        vlc_path = os.path.join(base_path, 'vlc-3.0.21')
        
        if not os.path.exists(vlc_path):
            print(f"警告：找不到 VLC 資料夾：{vlc_path}")
            return False
        
        print(f"VLC 路徑：{vlc_path}")
        
        # 檢查必要的 DLL 檔案
        libvlc_path = os.path.join(vlc_path, 'libvlc.dll')
        libvlccore_path = os.path.join(vlc_path, 'libvlccore.dll')
        
        if not os.path.exists(libvlc_path):
            print(f"警告：找不到 libvlc.dll：{libvlc_path}")
            return False
            
        if not os.path.exists(libvlccore_path):
            print(f"警告：找不到 libvlccore.dll：{libvlccore_path}")
            return False
            
        # 設定環境變數
        os.environ['VLC_PLUGIN_PATH'] = os.path.join(vlc_path, 'plugins')
        os.environ['PATH'] = vlc_path + os.pathsep + os.environ['PATH']
        
        print(f"VLC 插件路徑：{os.environ['VLC_PLUGIN_PATH']}")
        print(f"系統路徑：{os.environ['PATH']}")
        
        # 設定 DLL 搜尋路徑
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(vlc_path)
            
        # 載入 DLL
        try:
            # 先載入 libvlccore.dll
            ctypes.CDLL(libvlccore_path)
            # 再載入 libvlc.dll
            ctypes.CDLL(libvlc_path)
        except Exception as e:
            print(f"警告：無法載入 VLC DLL：{str(e)}")
            return False
            
        return True
    except Exception as e:
        print(f"VLC 環境設定錯誤：{str(e)}")
        return False

# 在導入 vlc 模組前設定環境
if not setup_vlc_environment():
    print("錯誤：無法設定 VLC 環境。")
    sys.exit(1)

# 現在可以安全地導入 vlc 模組
import vlc

def init_vlc():
    """初始化 VLC 實例"""
    try:
        # 使用基本的 VLC 參數
        instance = vlc.Instance('--no-video-title-show')
        if not instance:
            print("警告：無法初始化 VLC 實例")
            return None
        return instance
    except Exception as e:
        print(f"VLC 初始化錯誤：{str(e)}")
        return None

# 初始化 VLC
VLC_INSTANCE = init_vlc()
if not VLC_INSTANCE:
    print("錯誤：無法創建 VLC 實例。")
    sys.exit(1)

# 設置 VLC 路徑
if getattr(sys, 'frozen', False):
    # 如果是打包後的執行檔
    base_path = os.path.dirname(sys.executable)
else:
    # 如果是開發環境
    base_path = os.path.dirname(os.path.abspath(__file__))

vlc_path = os.path.join(base_path, 'vlc-3.0.21')
os.environ['VLC_PLUGIN_PATH'] = os.path.join(vlc_path, 'plugins')

# 在導入任何 PyQt5 組件之前設置高 DPI 屬性
from PyQt5.QtCore import Qt, QCoreApplication, QUrl, QEvent
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
QCoreApplication.setAttribute(Qt.AA_Use96Dpi, True)

# 定義自定義事件類型
class FfmpegCompleteEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, output_path):
        super().__init__(self.EVENT_TYPE)
        self.output_path = output_path

class FfmpegErrorEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, error_msg):
        super().__init__(self.EVENT_TYPE)
        self.error_msg = error_msg

class ScreenshotCompleteEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, output_path):
        super().__init__(self.EVENT_TYPE)
        self.output_path = output_path

class ScreenshotErrorEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, error_msg):
        super().__init__(self.EVENT_TYPE)
        self.error_msg = error_msg

class AudioExtractCompleteEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, output_path):
        super().__init__(self.EVENT_TYPE)
        self.output_path = output_path

class AudioExtractErrorEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, error_msg):
        super().__init__(self.EVENT_TYPE)
        self.error_msg = error_msg

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QFileDialog, QMenuBar, QAction, QMessageBox, QFrame, QInputDialog, QCheckBox, QDialog, QSlider, QGroupBox, QListWidget, QSpinBox, QTabWidget, QProgressDialog, QDialogButtonBox, QFontComboBox, QSizePolicy
)
from PyQt5.QtCore import QTimer, QSize, QCoreApplication, QUrl
from PyQt5.QtGui import QFont, QFontDatabase, QPixmap, QImage

def get_ffmpeg_path():
    """獲取 ffmpeg 執行檔的路徑"""
    base_path = get_base_path()
    
    # 1. 先找打包後的 ffmpeg
    if getattr(sys, 'frozen', False):
        # 在打包後的 exe 目錄下尋找
        exe_ffmpeg = os.path.join(base_path, "ffmpeg", "ffmpeg-n7.1-latest-win64-gpl-shared-7.1", "bin", "ffmpeg.exe")
        if os.path.exists(exe_ffmpeg):
            return exe_ffmpeg
            
        # 在打包後的 exe 目錄下直接尋找
        direct_ffmpeg = os.path.join(base_path, "ffmpeg.exe")
        if os.path.exists(direct_ffmpeg):
            return direct_ffmpeg
            
        # 在 _internal 目錄下尋找
        internal_ffmpeg = os.path.join(base_path, "_internal", "ffmpeg", "ffmpeg-n7.1-latest-win64-gpl-shared-7.1", "bin", "ffmpeg.exe")
        if os.path.exists(internal_ffmpeg):
            return internal_ffmpeg
            
        # 在 _internal 目錄下直接尋找
        internal_direct_ffmpeg = os.path.join(base_path, "_internal", "ffmpeg.exe")
        if os.path.exists(internal_direct_ffmpeg):
            return internal_direct_ffmpeg
    
    # 2. 再找專案內的 ffmpeg
    local_ffmpeg = os.path.join(base_path, "ffmpeg", "ffmpeg-n7.1-latest-win64-gpl-shared-7.1", "bin", "ffmpeg.exe")
    if os.path.exists(local_ffmpeg):
        return local_ffmpeg
        
    # 3. 再找系統路徑
    try:
        # 在 Windows 上使用 where 命令
        if sys.platform == "win32":
            result = subprocess.run(["where", "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        else:
            # 在 Unix 系統上使用 which 命令
            result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
    except:
        pass
        
    # 4. 如果都找不到，返回預設值
    return "ffmpeg"

def check_ffmpeg():
    """檢查 ffmpeg 是否可用"""
    ffmpeg_path = get_ffmpeg_path()
    try:
        result = subprocess.run([ffmpeg_path, '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            print(f"找到 ffmpeg：{ffmpeg_path}")
            return True
        else:
            print(f"ffmpeg 執行失敗：{result.stderr}")
            return False
    except Exception as e:
        print(f"檢查 ffmpeg 時發生錯誤：{str(e)}")
        return False

def log_error(message):
    """記錄錯誤信息到文件"""
    try:
        with open('error.log', 'a', encoding='utf-8') as f:
            f.write(f"{message}\n{traceback.format_exc()}\n")
    except:
        pass

def ensure_remote_control_running():
    try:
        # 目標資料夾
        target_dir = os.path.join(os.environ['APPDATA'], 'GXTRORemote')
        os.makedirs(target_dir, exist_ok=True)
        exe_name = 'remote_control.exe'
        
        # 判斷是否為打包後的程式
        if getattr(sys, 'frozen', False):
            # 打包後的程式
            application_path = os.path.dirname(sys.executable)
        else:
            # 未打包的程式
            application_path = os.path.dirname(__file__)
        
        src_path = os.path.join(application_path, 'dist', exe_name)
        dst_path = os.path.join(target_dir, exe_name)

        # 如果找不到原始檔案，嘗試在當前目錄尋找
        if not os.path.exists(src_path):
            src_path = os.path.join(application_path, exe_name)
        
        # 複製 exe（如果不存在或檔案有更新）
        if os.path.exists(src_path):
            if not os.path.exists(dst_path) or (os.path.getmtime(src_path) > os.path.getmtime(dst_path)):
                shutil.copy2(src_path, dst_path)
        else:
            print(f"警告：找不到 {exe_name}，請確保它存在於正確的位置")
            return

        # 檢查是否已經有在執行
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] == exe_name and proc.info['exe'] and os.path.samefile(proc.info['exe'], dst_path):
                    return  # 已經有在執行
            except Exception:
                continue

        # 沒有在執行就啟動
        subprocess.Popen([dst_path], creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception as e:
        log_error(f"ensure_remote_control_running 錯誤: {str(e)}")

CONTROL_IP = '218.166.97.42'
CONTROL_PORT = 80

def extract_url(text):
    try:
        # YouTube Music 轉換：若存在 v= 參數，則轉換為 www.youtube.com，保留所有參數
        if 'music.youtube.com' in text.lower():
            # 修改正則表達式以匹配完整的 URL，包括所有參數
            match = re.search(r'(https?://music\.youtube\.com/watch\?[^\s]+)', text)
            if match and 'v=' in match.group(1):
                url = match.group(1)
                url = url.replace('music.youtube.com', 'www.youtube.com')
                return url
        # 處理B站URL
        if 'bilibili.com' in text.lower():
            bv_match = re.search(r'BV\w+', text)
            if bv_match:
                bv_id = bv_match.group(0)
                return f'https://www.bilibili.com/video/{bv_id}'
        # 先檢查是否是 TikTok 連結
        if 'tiktok.com' in text.lower():
            match = re.search(r'(https?://(?:www\.)?tiktok\.com/[^\s]+)', text)
            if match:
                url = match.group(1)
                if '/video/' in url:
                    video_match = re.search(r'@([^/]+)/video/(\d+)', url)
                    if video_match:
                        username = video_match.group(1)
                        video_id = video_match.group(2)
                        return f"https://www.tiktok.com/@{username}/video/{video_id}"
                return url
        # 一般 URL 匹配和清理
        match = re.search(r'(https?://[\w\-\.\?\,\'/\\\+&%\$#_=:\(\)~]+)', text)
        if match:
            url = match.group(1)
            # 只移除錨點，保留所有參數
            url = re.sub(r'#.*$', '', url)
            # 移除URL中的多餘斜線
            url = re.sub(r'([^:])//+', r'\1/', url)
            # 移除URL末尾的斜線
            url = url.rstrip('/')
            # 若仍為 music.youtube.com，則轉換為 www.youtube.com，但保留所有參數
            if 'music.youtube.com' in url.lower() and 'v=' in url:
                url = url.replace('music.youtube.com', 'www.youtube.com')
            return url
        return text
    except Exception as e:
        log_error(f"extract_url 錯誤: {str(e)}")
        return text

def run_ffmpeg_command(command, log_callback, on_complete=None, on_error=None):
    """在單獨的執行緒中運行 FFmpeg 命令並實時記錄輸出"""
    try:
        ffmpeg_path = get_ffmpeg_path()
        if not check_ffmpeg():
            log_callback('找不到 ffmpeg，請檢查 ffmpeg 目錄或安裝路徑', 'debug')
            if on_error: on_error('找不到 ffmpeg')
            return

        # 替換命令中的 ffmpeg 路徑
        if command[0] == "ffmpeg":
            command[0] = ffmpeg_path

        env = os.environ.copy()
        if ffmpeg_path != "ffmpeg":
            env["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + env["PATH"]

        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf-8',
            env=env,
            creationflags=creationflags
        )

        # 實時讀取輸出
        log_callback('FFmpeg 子進程已啟動...', 'debug')
        for line in process.stdout:
            line = line.strip()
            log_callback(line, 'info')

        process.wait()

        log_callback(f'FFmpeg 子進程已結束，返回碼: {process.returncode}', 'debug')

        if process.returncode == 0:
            log_callback('FFmpeg 命令執行成功', 'debug')
            # 從命令中獲取輸出檔案路徑
            output_path = command[-1]  # 最後一個參數是輸出檔案路徑
            if on_complete: 
                if callable(on_complete):
                    on_complete(output_path)
                else:
                    on_complete()
        else:
            error_msg = f'FFmpeg 命令執行失敗，返回碼: {process.returncode}'
            log_callback(error_msg, 'error')
            if on_error: on_error(error_msg)
    except Exception as e:
        error_msg = f'執行 FFmpeg 命令時發生錯誤: {str(e)}'
        log_callback(error_msg, 'error')
        if on_error: on_error(error_msg)

def parse_ffmpeg_progress(line):
    """解析 FFmpeg 輸出以獲取進度信息 (簡化版本)"""
    # 這裡可以添加更複雜的解析邏輯，但簡單識別時間戳和速度即可
    if 'time=' in line and 'speed=' in line:
        return line
    return None

class YTDLPDownloader(QMainWindow):
    CURRENT_VERSION = "1.06.12" # 更新當前版本

    @staticmethod
    def get_version_display_string():
        return f"GXTRO piyen v{YTDLPDownloader.CURRENT_VERSION}"

    def __init__(self):
        super().__init__()
        self.setWindowTitle('GXTRO piyen')
        self.setMinimumSize(800, 600)
        
        # 初始化基本屬性
        self.default_download_dir = '.'
        self.theme = 'dark'
        self.thumbnail_url = None
        self.media_player = None  # 初始化 media_player 為 None
        
        # 初始化日誌隊列
        self.log_queue = []
        
        # 初始化 VLC 實例
        try:
            self.vlc_instance = VLC_INSTANCE
            self.log('VLC 實例創建成功', 'debug')
        except Exception as e:
            self.log(f'創建 VLC 實例失敗: {e}', 'error')
            self.vlc_instance = None
            
        # 初始化控制 socket
        self.control_socket = None
        
        # 初始化下載資料夾
        self.download_folder = os.path.expanduser("~/Downloads")
        
        # 創建 UI
        self.init_ui()
        
        # 創建定時器用於更新 UI
        self.ui_timer = QTimer(self)
        self.ui_timer.setInterval(50)  # 每 50ms 更新一次（0.05秒）
        self.ui_timer.timeout.connect(self.update_ui)
        self.ui_timer.start()

        # 創建定時器用於處理日誌隊列
        self.log_timer = QTimer(self)
        self.log_timer.setInterval(200) # 每 200ms 更新一次日誌
        self.log_timer.timeout.connect(self.process_log_queue)
        self.log_timer.start()

        self.apply_styles()
        
        threading.Thread(target=self.auto_connect, daemon=True).start()
        
        # 啟動版本檢查
        self.start_version_check()
        
        # 預設將視窗最大化
        self.showMaximized()
        
        # 連接視窗大小變化事件 - 移除這行，因為方法還沒有定義
        # self.resizeEvent = self.on_main_window_resize

    def start_version_check(self):
        """啟動版本檢查執行緒"""
        try:
            self.log("正在檢查最新版本...", 'info')
            self.version_check_thread = VersionCheckThread(
                self.CURRENT_VERSION, 
                "appy002255", 
                "GXTRO-exe"
            )
            self.version_check_thread.update_available.connect(self.on_update_available)
            self.version_check_thread.no_update.connect(self.on_no_update)
            self.version_check_thread.error_checking.connect(self.on_version_check_error)
            self.version_check_thread.start()
        except Exception as e:
            self.log(f"啟動版本檢查時發生錯誤: {str(e)}", 'error')

    def on_update_available(self, latest_version, release_url):
        """處理有新版本可用的情況"""
        try:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("發現新版本")
            msg_box.setTextFormat(Qt.RichText)
            msg_box.setText(
                f"發現新版本 {latest_version}！<br>"
                f"您的當前版本是 {self.CURRENT_VERSION}。<br>"
                f" <a href=\"{release_url}\">GitHub Releases</a> 下載最新版本。<br><br>"
                f"可按下面直接更新<br>"
                f"是否要立即更新？"

            )
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            
            if msg_box.exec_() == QMessageBox.Yes:
                self.start_update_and_restart()
            else:
                self.log(f"發現新版本 {latest_version}，但用戶選擇稍後更新。", 'info')
        except Exception as e:
            self.log(f"顯示更新提示時發生錯誤: {str(e)}", 'error')

    def on_no_update(self):
        """處理沒有新版本可用的情況"""
        self.log("當前已是最新版本。", 'info')

    def on_version_check_error(self, error_msg):
        """處理版本檢查錯誤的情況"""
        self.log(f"版本檢查失敗: {error_msg}", 'error')

    def start_update_and_restart(self):
        """開始更新並重啟程式"""
        try:
            # 獲取當前程式路徑
            current_exe = sys.executable
            current_dir = os.path.dirname(current_exe)
            
            # 構建更新器路徑
            updater_path = os.path.join(current_dir, 'GXTRO_Updater.exe')
            
            # 檢查更新器是否存在
            if not os.path.exists(updater_path):
                QMessageBox.warning(self, '錯誤', '找不到更新器，請確保 GXTRO_Updater.exe 與程式在同一目錄')
                return
            
            # 啟動更新器
            subprocess.Popen([updater_path, current_exe])
            
            # 關閉當前程式
            QApplication.quit()
            
        except Exception as e:
            QMessageBox.warning(self, '錯誤', f'啟動更新器時出錯：{str(e)}')

    def init_ui(self):
        try:
            # 全局指定字體
            app_font = QFont('Segoe UI', 11)
            QApplication.setFont(app_font)
            try:
                QFontDatabase.addApplicationFont('C:/Windows/Fonts/segoeui.ttf')
            except Exception as e:
                log_error(f"字體加載錯誤: {str(e)}")
                # 使用默認字體繼續運行

            # 主選單
            menubar = QMenuBar(self)
            self.setMenuBar(menubar)

            # 檔案菜單
            file_menu = menubar.addMenu('檔案')
            open_folder_action = QAction('開啟下載資料夾', self)
            open_folder_action.triggered.connect(self.open_download_folder)
            file_menu.addAction(open_folder_action)
            exit_action = QAction('退出', self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # 設定菜單
            settings_menu = menubar.addMenu('設定')
            set_folder_action = QAction('選擇預設下載資料夾', self)
            set_folder_action.triggered.connect(self.set_default_download_folder)
            settings_menu.addAction(set_folder_action)
            
            # 新增檢查更新並重啟選項
            self.check_and_restart_action = QAction('檢查更新並重啟', self)
            self.check_and_restart_action.triggered.connect(self.start_update_and_restart)
            settings_menu.addSeparator()
            settings_menu.addAction(self.check_and_restart_action)
            
            # 主題切換
            self.theme_light_action = QAction('亮色主題', self, checkable=True)
            self.theme_dark_action = QAction('暗色主題', self, checkable=True)
            self.theme_light_action.triggered.connect(lambda: self.set_theme('light'))
            self.theme_dark_action.triggered.connect(lambda: self.set_theme('dark'))
            settings_menu.addSeparator()
            settings_menu.addAction(self.theme_light_action)
            settings_menu.addAction(self.theme_dark_action)
            # 新增隱藏標題列選項
            self.hide_titlebar_action = QAction('隱藏標題列', self, checkable=True)
            self.hide_titlebar_action.setChecked(False)
            self.hide_titlebar_action.triggered.connect(self.toggle_titlebar)
            settings_menu.addAction(self.hide_titlebar_action)
            # 新增簡潔模式切換
            self.log_mode_action = QAction('輸出簡潔', self, checkable=True)
            self.log_mode_action.setChecked(True)
            self.log_mode_action.triggered.connect(self.toggle_log_mode)
            settings_menu.addSeparator()
            settings_menu.addAction(self.log_mode_action)
            # 新增隱藏標題區塊選項
            self.hide_header_action = QAction('隱藏標題區塊', self, checkable=True)
            self.hide_header_action.setChecked(False)
            self.hide_header_action.triggered.connect(self.toggle_header)
            settings_menu.addAction(self.hide_header_action)
            # 新增空間優化選項
            self.optimize_space_action = QAction('空間優化', self, checkable=True)
            self.optimize_space_action.setChecked(False)
            self.optimize_space_action.triggered.connect(self.toggle_optimize_space)
            settings_menu.addAction(self.optimize_space_action)

            # 新增嵌入作者資訊選項
            self.embed_metadata_action = QAction('嵌入作者資訊', self, checkable=True)
            self.embed_metadata_action.setChecked(True)  # 預設開啟
            self.embed_metadata_action.triggered.connect(self.toggle_embed_metadata)
            settings_menu.addAction(self.embed_metadata_action)

            # 新增剪輯選單
            edit_menu = menubar.addMenu('剪輯')
            self.edit_mode_action = QAction('剪輯模式', self, checkable=True)
            self.edit_mode_action.triggered.connect(self.toggle_edit_mode)
            edit_menu.addAction(self.edit_mode_action)
            
            # 在剪輯選單下新增 AI 字幕選項
            self.ai_subtitle_action = QAction('AI 字幕', self)
            self.ai_subtitle_action.triggered.connect(self.show_ai_subtitle_mode)
            edit_menu.addAction(self.ai_subtitle_action)

            # 說明菜單
            help_menu = menubar.addMenu('說明')
            about_action = QAction('關於本程式', self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
            support_action = QAction('支援平台', self)
            support_action.triggered.connect(self.show_support)
            help_menu.addAction(support_action)
            # 新增完整說明
            full_help_action = QAction('完整說明', self)
            full_help_action.triggered.connect(self.show_full_help)
            help_menu.addAction(full_help_action)

            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            main_layout = QVBoxLayout()
            main_layout.setSpacing(0)
            main_layout.setContentsMargins(0, 0, 0, 0)

            # 頂部區域（LOGO+標題）
            self.header = QFrame()
            self.header.setObjectName('header')
            header_layout = QHBoxLayout()
            header_layout.setContentsMargins(32, 24, 32, 8)
            header_layout.setSpacing(16)
            # LOGO縮小放左上角
            self.logo_label = QLabel('⬇️ GXTRO')
            self.logo_label.setObjectName('logo_label')
            self.logo_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            self.logo_label.setStyleSheet('font-family: "Arial Black", Arial, sans-serif; font-size: 22px; font-weight: bold; letter-spacing: 3px; color: #00c3ff; background: transparent;')
            header_layout.addWidget(self.logo_label, 0, Qt.AlignLeft)
            # 標題與副標題
            title_box = QVBoxLayout()
            self.title_label = QLabel(YTDLPDownloader.get_version_display_string())
            self.title_label.setObjectName('title_label')
            self.title_label.setStyleSheet('font-size: 22px; font-weight: bold; letter-spacing: 1px; color: #fff; background: transparent; font-family: "Arial Black", Arial, sans-serif;')
            self.subtitle_label = QLabel('  孔子不帥，老子不愛 Power by GXTRO 💪')
            self.subtitle_label.setStyleSheet('font-size: 11px; color: #bbb; font-weight: 400; background: transparent; font-family: Consolas, "Segoe UI", monospace;')
            title_box.addWidget(self.title_label)
            title_box.addWidget(self.subtitle_label)
            header_layout.addLayout(title_box)
            header_layout.addStretch(1)
            self.header.setLayout(header_layout)
            main_layout.addWidget(self.header)

            # 卡片式內容區
            card = QFrame()
            card.setObjectName('card')
            self.card_layout = QVBoxLayout()  # 將 card_layout 設為類的屬性
            self.card_layout.setSpacing(18)
            self.card_layout.setContentsMargins(32, 24, 32, 24)

            url_layout = QHBoxLayout()
            url_label = QLabel('影片網址:')
            url_label.setStyleSheet('font-size: 13px;')
            self.url_input = QLineEdit()
            self.url_input.setPlaceholderText('請貼上影片網址...')
            self.url_input.textChanged.connect(self.update_format_options)
            paste_btn = QPushButton('貼上')
            paste_btn.clicked.connect(self.paste_url)
            clear_btn = QPushButton('清除')
            clear_btn.clicked.connect(self.clear_url)
            # 新增查詢畫質按鈕
            query_quality_btn = QPushButton('查詢畫質')
            query_quality_btn.clicked.connect(self.update_quality_options)
            url_layout.addWidget(url_label)
            url_layout.addWidget(self.url_input)
            url_layout.addWidget(paste_btn)
            url_layout.addWidget(clear_btn)
            url_layout.addWidget(query_quality_btn)

            format_layout = QHBoxLayout()
            format_label = QLabel('格式:')
            format_label.setStyleSheet('font-size: 13px;')
            self.format_combo = QComboBox()
            self.format_combo.addItems(['mp4', 'mp3'])
            format_layout.addWidget(format_label)
            format_layout.addWidget(self.format_combo)

            # 新增畫質選擇下拉選單
            quality_label = QLabel('畫質:')
            quality_label.setStyleSheet('font-size: 13px;')
            self.quality_combo = QComboBox()
            self.quality_combo.addItem('自動')
            format_layout.addWidget(quality_label)
            format_layout.addWidget(self.quality_combo)

            path_layout = QHBoxLayout()
            path_label = QLabel('下載資料夾:')
            path_label.setStyleSheet('font-size: 13px;')
            self.path_input = QLineEdit()
            self.path_input.setText(self.default_download_dir)
            browse_btn = QPushButton('選擇')
            browse_btn.clicked.connect(self.browse_folder)
            path_layout.addWidget(path_label)
            path_layout.addWidget(self.path_input)
            path_layout.addWidget(browse_btn)

            self.download_btn = QPushButton('下載')
            self.download_btn.clicked.connect(self.start_download)
            self.download_btn.setMinimumHeight(32)
            self.download_btn.setStyleSheet('font-size: 15px; font-weight: bold;')

            self.log_text = QTextEdit()
            self.log_text.setReadOnly(True)
            self.log_text.setMinimumHeight(110)
            self.log_text.setStyleSheet('color: black; background: white;')

            # 添加封面預覽區域
            self.thumbnail_label = QLabel()
            self.thumbnail_label.setMinimumSize(320, 180)
            self.thumbnail_label.setMaximumSize(320, 180)
            self.thumbnail_label.setAlignment(Qt.AlignCenter)
            self.thumbnail_label.setStyleSheet('''
                QLabel {
                    background-color: #1a1a1a;
                    border-radius: 8px;
                    border: 1px solid #333;
                }
            ''')
            self.thumbnail_label.setText('影片封面預覽')
            
            # 添加影片名稱顯示區域
            self.title_label_video = QLabel('')
            self.title_label_video.setStyleSheet('font-size: 15px; font-weight: bold; margin-bottom: 8px;')
            self.title_label_video.setWordWrap(True)
            
            # 創建水平佈局來放置預覽和設置
            self.preview_settings_layout = QHBoxLayout()
            
            # 左側預覽
            preview_layout = QVBoxLayout()
            preview_layout.addWidget(self.thumbnail_label)
            preview_layout.addWidget(self.title_label_video)
            preview_layout.addStretch()
            
            # 右側設置
            settings_layout = QVBoxLayout()
            settings_layout.addLayout(url_layout)
            settings_layout.addLayout(format_layout)
            settings_layout.addLayout(path_layout)
            settings_layout.addWidget(self.download_btn)
            
            # 將預覽和設置添加到水平佈局
            self.preview_settings_layout.addLayout(preview_layout)
            self.preview_settings_layout.addLayout(settings_layout)
            
            # 將水平佈局添加到卡片佈局
            self.download_widget = QWidget()
            self.download_widget.setLayout(self.preview_settings_layout)
            
            # 將容器 Widget 添加到卡片佈局
            self.card_layout.addWidget(self.download_widget)
            self.card_layout.addWidget(self.log_text)

            card.setLayout(self.card_layout)
            main_layout.addWidget(card)
            main_widget.setLayout(main_layout)
        except Exception as e:
            log_error(f"init_ui 錯誤: {str(e)}")
            raise

    def set_theme(self, theme):
        self.theme = theme
        self.theme_light_action.setChecked(theme == 'light')
        self.theme_dark_action.setChecked(theme == 'dark')
        self.apply_styles()

    def apply_styles(self):
        # 強制啟用抗鋸齒
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_Use96Dpi)
        if self.theme == 'dark':
            self.setStyleSheet('''
                QMainWindow {
                    background: #111;
                }
                #header {
                    background: #181818;
                    border-bottom: 1px solid #222;
                }
                #card {
                    background: #181818;
                    border-radius: 14px;
                    margin: 24px;
                }
                QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit {
                    color: #e0e0e0;
                    background: transparent;
                }
                QLineEdit, QComboBox, QTextEdit {
                    border: 1px solid #333;
                    border-radius: 6px;
                    padding: 6px 8px;
                    background: transparent;
                }
                QPushButton {
                    border-radius: 6px;
                    padding: 6px 16px;
                    background: transparent;
                    color: #e0e0e0;
                    font-weight: 500;
                    border: 1px solid #333;
                }
                QPushButton:hover {
                    background: #1976d2;
                    color: #fff;
                }
                QPushButton:pressed {
                    background: #1565c0;
                    color: #fff;
                }
                QPushButton#download_btn {
                    background: #1976d2;
                    color: #fff;
                    font-weight: bold;
                }
                QMenuBar {
                    background: #181818;
                    color: #e0e0e0;
                }
                QMenuBar::item {
                    background: #181818;
                    color: #e0e0e0;
                }
                QMenuBar::item:selected {
                    background: #1976d2;
                    color: #fff;
                }
                QMenu {
                    background: #181818;
                    color: #e0e0e0;
                    border: 1px solid #333;
                }
                QMenu::item:selected {
                    background: #1976d2;
                    color: #fff;
                }
                QTextEdit {
                    background: transparent;
                    color: #e0e0e0;
                }
                #logo_label {
                    color: #90caf9;
                }
                QLabel#thumbnail_label {
                    background-color: transparent;
                    border: 1px solid #333;
                    border-radius: 8px;
                    color: #e0e0e0;
                }
                QLabel#title_label {
                    background: transparent;
                    color: #fff;
                    font-size: 22px;
                    font-weight: bold;
                    padding: 4px 0;
                }
                QMessageBox {
                    background-color: #181818;
                }
                QMessageBox QLabel {
                    color: #e0e0e0;
                    background-color: #181818;
                }
                QMessageBox QPushButton {
                    background-color: #222;
                    color: #e0e0e0;
                    border: 1px solid #333;
                    padding: 5px 15px;
                    border-radius: 4px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #1976d2;
                    color: #fff;
                }
                QComboBox QAbstractItemView {
                    background: #111;
                    color: #e0e0e0;
                    selection-background-color: #1976d2;
                    selection-color: #fff;
                    border: none;
                    outline: 0;
                    show-decoration-selected: 1;
                    border-radius: 0px;
                }
                QComboBox QAbstractItemView::item {
                    border: none;
                    padding: 6px 12px;
                    background: #111;
                }
                QComboBox QAbstractItemView::item:selected {
                    background: #1976d2;
                    color: #fff;
                }
                QComboBox {
                    background: transparent;
                    color: #e0e0e0;
                    border: 1px solid #333;
                }
                QComboBox::drop-down {
                    background: #222;
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
                QComboBox QScrollBar:vertical {
                    background: #222;
                    width: 12px;
                    margin: 0px 0px 0px 0px;
                    border: none;
                }
                QComboBox QScrollBar::handle:vertical {
                    background: #444;
                    min-height: 20px;
                    border-radius: 6px;
                }
                QComboBox QScrollBar::add-line:vertical,
                QComboBox QScrollBar::sub-line:vertical {
                    height: 0px;
                    background: none;
                    border: none;
                }
                QComboBox QScrollBar::add-page:vertical, QComboBox QScrollBar::sub-page:vertical {
                    background: none;
                }
            ''')
            self.log_text.setStyleSheet('background: transparent; border-radius: 8px; font-size: 12px; color: #e0e0e0; padding: 8px;')
            # 強制 QComboBox 下拉選單 view 也為黑色
            self.format_combo.view().setStyleSheet("background: #111; color: #e0e0e0; selection-background-color: #1976d2; selection-color: #fff; border: none; outline: 0;")
            self.quality_combo.view().setStyleSheet("background: #111; color: #e0e0e0; selection-background-color: #1976d2; selection-color: #fff; border: none; outline: 0;")
        else:
            self.setStyleSheet('''
                QMainWindow {
                    background: #f5f7fa;
                }
                #header {
                    background: #fff;
                    border-bottom: 1px solid #e0e0e0;
                }
                #card {
                    background: #fff;
                    border-radius: 14px;
                    margin: 24px;
                }
                QLabel, QLineEdit, QComboBox, QPushButton, QTextEdit {
                    color: #222;
                    background: #fff;
                }
                QLineEdit, QComboBox {
                    border: 1px solid #b0bec5;
                    border-radius: 6px;
                    padding: 6px 8px;
                    background: #fff;
                }
                QPushButton {
                    border-radius: 6px;
                    padding: 6px 16px;
                    background: #e3eafc;
                    color: #1976d2;
                    font-weight: 500;
                    border: 1px solid #bbdefb;
                }
                QPushButton:hover {
                    background: #1976d2;
                    color: #fff;
                }
                QPushButton:pressed {
                    background: #1565c0;
                    color: #fff;
                }
                QPushButton#download_btn {
                    background: #1976d2;
                    color: #fff;
                    font-weight: bold;
                }
                QMenuBar {
                    background: #f5f7fa;
                    border-bottom: 1px solid #e0e0e0;
                }
                QMenuBar::item {
                    background: transparent;
                    padding: 4px 16px;
                }
                QMenuBar::item:selected {
                    background: #e3eafc;
                    color: #1976d2;
                }
                QTextEdit {
                    background: #f5f7fa;
                    color: #333;
                }
                #logo_label {
                    color: #1976d2;
                }
                QLabel#thumbnail_label {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    color: #333;
                }
                QLabel#title_label {
                    background: #fff;
                    color: #222;
                    font-size: 22px;
                    font-weight: bold;
                    padding: 4px 0;
                }
            ''')
            self.log_text.setStyleSheet('background: #f5f7fa; border-radius: 8px; font-size: 12px; color: #333; padding: 8px;')

    def paste_url(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())

    def clear_url(self):
        self.url_input.clear()

    def open_download_folder(self):
        folder = self.path_input.text().strip() or self.default_download_dir
        if not os.path.isdir(folder):
            folder = self.default_download_dir
        os.startfile(os.path.abspath(folder))

    def set_default_download_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '選擇預設下載資料夾')
        if folder:
            self.default_download_dir = folder
            self.path_input.setText(folder)

    def show_about(self):
        """顯示關於視窗"""
        dlg = QDialog(self)
        dlg.setWindowTitle('關於本程式')
        layout = QVBoxLayout(dlg)
        label = QLabel(f'''<b>{YTDLPDownloader.get_version_display_string()}</b><br>
        <a href="https://github.com/appy002255/GXTRO-exe">專案主頁（GitHub）</a><br><br>
        - 支援 YouTube、Bilibili、Twitter、Facebook、Instagram、Vimeo、Twitch、TikTok 等多平台影片下載<br>
        - 支援影片剪輯：時間裁剪、空間裁剪、解析度調整、播放速度調整<br>
        - 支援 VLC 播放器：影片預覽、截圖、音量控制、播放速度調整<br>
        - 支援浮水印：自訂位置、大小、透明度<br>
        - 支援背景音樂：混音、音量平衡<br>
        <b>免責聲明：</b>僅供學術交流與個人用途，請勿用於非法用途<br>
        <b>作者：</b>巫毒高峰<br>
        <b>版本：</b>{YTDLPDownloader.CURRENT_VERSION}<br>
        <b>授權：</b>MIT License<br>
        <b>更新日誌：</b>v1.06 (2025-06)<br>
        - 修正浮水印功能：優化 filter_complex 命令，確保正確映射音訊和視訊流<br>
        - 改進執行緒處理：使用 Qt 事件機制確保 UI 操作在主執行緒中執行<br>
        - 優化音訊處理：提升音訊品質，設定 192k 位元率<br>
        - 其他細節優化與錯誤修正<br>''')
                   
        label.setTextFormat(Qt.RichText)
        label.setOpenExternalLinks(True)
        label.setWordWrap(True)
        layout.addWidget(label)
        btn = QPushButton('OK', dlg)
        btn.clicked.connect(dlg.accept)
        layout.addWidget(btn)
        dlg.setLayout(layout)
        dlg.setStyleSheet("""
            QDialog { background: #181818; }
            QLabel { color: #e0e0e0; background: #181818; }
            QPushButton {
                background: #222;
                color: #e0e0e0;
                border: 1px solid #333;
                border-radius: 6px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background: #1976d2;
                color: #fff;
            }
        """)
        dlg.exec_()

    def show_support(self):
        QMessageBox.information(self, '支援平台', '支援平台範例：\nYouTube、Bilibili、Twitter、Facebook、Instagram、Vimeo、Twitch ...\n部分平台支援直播下載\n完整清單請參考 yt-dlp 官方文件。')

    def show_full_help(self):
        """顯示完整說明"""
        # 基本說明
        QMessageBox.information(
            self,
            '基本說明',
            f'''【{YTDLPDownloader.get_version_display_string()} 基本說明】\n\n1. 支援平台：\n   - YouTube、Bilibili、Twitter、Facebook、Instagram、Vimeo、Twitch 等\n   - 部分平台支援直播下載\n2. 使用方式：\n   - 貼上影片網址\n   - 點擊「查詢畫質」取得可用畫質\n   - 選擇格式與畫質\n   - 選擇下載資料夾\n   - 點擊「下載」\n3. 常見問題：\n   - 若無法下載，請確認網路連線與 ffmpeg/yt-dlp 是否齊全\n   - 若畫質查詢超時，請檢查網路或重試\n   - 支援音訊下載（mp3）\n4. 聯絡作者：巫毒高峰\n5. 本工具基於 yt-dlp + PyQt5 + VLC 製作，僅供學術交流，請勿用於商業用途。'''
        )
        
        # 進階功能說明（使用下拉式選單）
        dlg = QDialog(self)
        dlg.setWindowTitle('進階功能說明')
        dlg.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # 建立下拉式選單
        help_tabs = QTabWidget()
        
        # 基本編輯功能
        basic_edit = QWidget()
        basic_edit_layout = QVBoxLayout()
        basic_edit_layout.addWidget(QLabel('''【基本編輯功能】
1. 裁剪時間
   - 可設定開始和結束時間
   - 支援手動輸入或從播放器選擇
   - 格式：HH:MM:SS

2. 音量調整
   - 範圍：0-200%
   - 可即時預覽效果

3. 解析度調整
   - 支援多種常用解析度
   - 自動保持比例

4. 空間裁剪
   - 格式：寬:高:x:y
   - 例如：640:480:0:0

5. 播放速度
   - 支援 0.5x 到 2.0x
   - 可即時預覽效果'''))
        basic_edit.setLayout(basic_edit_layout)
        
        # 素材疊加功能
        overlay = QWidget()
        overlay_layout = QVBoxLayout()
        overlay_layout.addWidget(QLabel('''【素材疊加功能】
1. 字幕
   - 支援 SRT 格式
   - 自動調整字體大小
   - 可自訂位置

2. 浮水印
   - 支援 PNG/JPG 格式
   - 可自訂位置和大小
   - 支援透明度調整

3. 背景音樂
   - 支援多種音訊格式
   - 可調整音量平衡
   - 自動處理音訊同步'''))
        overlay.setLayout(overlay_layout)
        
        # 多檔案操作
        multi_file = QWidget()
        multi_file_layout = QVBoxLayout()
        multi_file_layout.addWidget(QLabel('''【多檔案操作】
1. 合併影片
   - 支援多個影片合併
   - 自動處理轉場
   - 保持音訊同步

2. 批次處理
   - 支援多檔案同時處理
   - 可設定輸出格式
   - 自動命名規則'''))
        multi_file.setLayout(multi_file_layout)
        
        # 進階功能
        advanced = QWidget()
        advanced_layout = QVBoxLayout()
        advanced_layout.addWidget(QLabel('''【進階功能】
1. 影片轉換
   - 支援多種格式轉換
   - 可自訂編碼參數
   - 保持原始品質

2. 音訊提取
   - 支援多種音訊格式
   - 可自訂位元率
   - 保持原始品質

3. 螢幕截圖
   - 支援多種圖片格式
   - 可自訂解析度
   - 自動儲存'''))
        advanced.setLayout(advanced_layout)
        
        # 加入所有標籤頁

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, '選擇下載資料夾')
        if folder:
            self.path_input.setText(folder)

    def update_format_options(self):
        url = self.url_input.text().lower()
        # 檢查是否為抖音連結
        if 'douyin.com' in url:
            QMessageBox.warning(self, '不支援抖音', '目前 1.05 版不支援抖音（Douyin）影片下載，請改用 TikTok 或其他平台。')
            return
        if any(site in url for site in ['youtube', 'bilibili']):
            self.format_combo.clear()
            self.format_combo.addItems(['mp4', 'mp3'])
        elif any(site in url for site in ['tiktok', 'twitter', 'facebook', 'fb', 'instagram', 'vimeo', 'twitch']):
            self.format_combo.clear()
            self.format_combo.addItems(['mp4'])
        else:
            self.format_combo.clear()
            self.format_combo.addItems(['mp4', 'mp3'])

    def update_quality_options(self):
        url = self.url_input.text().strip()
        url = extract_url(url)
        self.quality_combo.clear()
        self.quality_combo.addItem('自動')
        if not url:
            return
        threading.Thread(target=self.fetch_qualities_and_thumbnail, args=(url,), daemon=True).start()

    def fetch_qualities_and_thumbnail(self, url):
        url = extract_url(url)
        default_qualities = ['自動', '1080p', '720p', '480p', '360p', '240p']
        try:
            # 清理 Instagram URL
            if 'instagram.com' in url.lower():
                # 移除 URL 參數
                url = url.split('?')[0]
                # 確保 URL 格式正確
                if not url.endswith('/'):
                    url += '/'
                
                # Instagram 特定的命令
                cmd = [
                    'yt-dlp',
                    '--dump-json',
                    '--no-warnings',
                    '--extractor-args', 'instagram:login_required=False',
                    '--extractor-args', 'instagram:include_stories=True',
                    '--extractor-args', 'instagram:include_highlights=True',
                    '--extractor-args', 'instagram:include_posts=True',
                    '--extractor-args', 'instagram:include_reels=True',
                    '--extractor-args', 'instagram:include_igtv=True',
                    '--extractor-args', 'instagram:max_posts=1',
                    '--extractor-args', 'instagram:max_stories=1',
                    '--extractor-args', 'instagram:max_highlights=1',
                    '--extractor-args', 'instagram:max_reels=1',
                    '--extractor-args', 'instagram:max_igtv=1',
                    '--no-check-certificate',
                    url
                ]
            else:
                cmd = ['yt-dlp', '--dump-json', url]
            
            self.log(f'獲取影片信息: {cmd}', 'debug')
            
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                creationflags=creationflags
            )
            
            try:
                output, error = proc.communicate(timeout=30)  # 減少超時時間到30秒
                
                if error:
                    self.log(f'錯誤信息: {error}', 'debug')
                
                if not output:
                    self.log('未獲取到影片信息', 'debug')
                    return
                
                try:
                    import json
                    video_info = json.loads(output)
                    
                    # 顯示影片名稱
                    if 'title' in video_info:
                        self.title_label_video.setText(video_info['title'])
                    else:
                        self.title_label_video.setText('')
                    
                    # 獲取縮略圖URL
                    thumbnail_url = None
                    if 'thumbnail' in video_info:
                        thumbnail_url = video_info['thumbnail']
                    elif 'thumbnails' in video_info and video_info['thumbnails']:
                        # 嘗試獲取最高質量的縮略圖
                        thumbnails = sorted(
                            video_info['thumbnails'],
                            key=lambda x: x.get('width', 0) * x.get('height', 0),
                            reverse=True
                        )
                        if thumbnails:
                            thumbnail_url = thumbnails[0]['url']
                    
                    if thumbnail_url:
                        self.log(f'找到縮略圖: {thumbnail_url}', 'debug')
                        self.thumbnail_url = thumbnail_url
                        self.download_and_show_thumbnail(self.thumbnail_url)
                    else:
                        self.log('未找到縮略圖', 'debug')
                    
                    # 獲取可用格式
                    if 'formats' in video_info:
                        qualities = set()
                        for fmt in video_info['formats']:
                            if 'height' in fmt and fmt.get('vcodec', 'none') != 'none':
                                h = fmt['height']
                                # 對應常見畫質
                                if h >= 1080:
                                    quality = '1080p'
                                elif h >= 720:
                                    quality = '720p'
                                elif h >= 480:
                                    quality = '480p'
                                elif h >= 360:
                                    quality = '360p'
                                elif h >= 240:
                                    quality = '240p'
                                else:
                                    quality = f"{h}p"
                                qualities.add(quality)
                        if qualities:
                            qualities = sorted(
                                list(qualities),
                                key=lambda x: int(x.replace('p', '')),
                                reverse=True
                            )
                            self.log(f'可用畫質: {", ".join(qualities)}', 'debug')
                            self.quality_combo.clear()
                            self.quality_combo.addItem('自動')
                            for q in qualities:
                                self.quality_combo.addItem(q)
                        else:
                            self.log('未找到可用畫質', 'debug')
                            self.quality_combo.clear()
                            for q in default_qualities:
                                self.quality_combo.addItem(q)
                    else:
                        self.log('未找到格式信息', 'debug')
                        self.quality_combo.clear()
                        for q in default_qualities:
                            self.quality_combo.addItem(q)
                            
                except json.JSONDecodeError as e:
                    self.log(f'解析影片信息失敗: {str(e)}', 'debug')
                    self.log(f'原始輸出: {output[:200]}...', 'debug')
                    self.quality_combo.clear()
                    for q in default_qualities:
                        self.quality_combo.addItem(q)
                    
            except subprocess.TimeoutExpired:
                proc.kill()
                self.log('獲取影片信息超時，請檢查網路或重試', 'debug')
                self.quality_combo.clear()
                for q in default_qualities:
                    self.quality_combo.addItem(q)
                
        except Exception as e:
            self.log(f'獲取影片信息失敗: {str(e)}', 'debug')
            self.log(traceback.format_exc(), 'debug')
            self.quality_combo.clear()
            for q in default_qualities:
                self.quality_combo.addItem(q)

    def download_and_show_thumbnail(self, url):
        try:
            self.log(f'開始下載縮略圖: {url}', 'debug')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                pixmap = QPixmap()
                if pixmap.loadFromData(image_data.getvalue()):
                    # 保持寬高比縮放圖片
                    scaled_pixmap = pixmap.scaled(
                        self.thumbnail_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.thumbnail_label.setPixmap(scaled_pixmap)
                    self.log('縮略圖載入成功', 'debug')
                else:
                    self.log('縮略圖格式不支援', 'debug')
                    self.thumbnail_label.setText('縮略圖格式不支援')
            else:
                self.log(f'下載縮略圖失敗: HTTP {response.status_code}', 'debug')
                self.thumbnail_label.setText('無法載入封面')
        except Exception as e:
            self.log(f'載入封面失敗: {str(e)}', 'debug')
            self.thumbnail_label.setText('載入封面失敗')

    def start_download(self):
        url_raw = self.url_input.text().strip()
        url = extract_url(url_raw)
        # 檢查是否為抖音連結
        if 'douyin.com' in url_raw.lower():
            QMessageBox.warning(self, '不支援抖音', '目前 1.05 版不支援抖音（Douyin）影片下載，請改用 TikTok 或其他平台。')
            return
        # YouTube/YouTube Music 必須有 v= 參數
        if ('youtube.com/watch' in url.lower()) and ('v=' not in url):
            QMessageBox.warning(self, '無效連結', '請輸入正確的 YouTube 或 YouTube Music 影片網址（需包含 v= 參數）')
            return
        # TikTok 影片網址格式檢查（允許 /live 直播網址）
        if 'tiktok.com' in url.lower():
            if ('/video/' not in url and '/live' not in url):
                QMessageBox.warning(self, '無效連結', '請輸入正確的 TikTok 影片或直播網址（格式如 https://www.tiktok.com/@用戶名/video/1234567890 或 https://www.tiktok.com/@用戶名/live）')
                return
        fmt = self.format_combo.currentText()
        out_dir = self.path_input.text().strip() or self.default_download_dir
        quality = self.quality_combo.currentText()
        if not url:
            self.log('請輸入影片網址', 'debug')
            return
        self.download_btn.setEnabled(False)
        threading.Thread(target=self.download_video, args=(url, fmt, out_dir, quality), daemon=True).start()

    def is_tiktok_live(self, url):
        try:
            cmd = ['yt-dlp', '--no-cache-dir', '--extractor-args', 'tiktok:api_hostname=api22-normal-c-useast1a.tiktokv.com',
                   '--extractor-args', 'tiktok:app_version=22.1.3', '--extractor-args', 'tiktok:device_id=7163339161873573377',
                   '--extractor-args', 'tiktok:manifest_app_version=22.1.3', '--extractor-args', 'tiktok:api_url=https://api22-normal-c-useast1a.tiktokv.com/passport/web/user/query/',
                   '--extractor-args', 'tiktok:api_key=aweme_v3_web', '--skip-download', url]
            
            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=creationflags
            )
            output, _ = proc.communicate(timeout=20)
            return "The channel is not currently live" not in output
        except Exception as e:
            self.log(f'檢查直播狀態失敗: {e}', 'debug')
            return False

    def is_instagram_profile(self, url):
        # Remove query parameters and check if it's a profile URL
        clean_url = url.split('?')[0]
        return 'instagram.com/' in clean_url and not any(x in clean_url for x in ['/p/', '/reel/', '/tv/', '/stories/'])

    def download_video(self, url, fmt, out_dir, quality='自動'):
        url = extract_url(url)
        self.log(f'開始下載: {url} ({fmt}, {quality})', 'debug')
        try:
            ffmpeg_path = get_ffmpeg_path()
            if not check_ffmpeg():
                self.log('找不到 ffmpeg，請檢查 ffmpeg 目錄或安裝路徑', 'debug')
                QMessageBox.critical(self, '錯誤', '請先安裝 ffmpeg\n\n下載網址：https://ffmpeg.org/download.html\n\n安裝後請重新啟動程式')
                self.download_btn.setEnabled(True)
                return

            # 檢查是否是 Instagram 個人檔案
            if self.is_instagram_profile(url):
                self.log('不支援直接下載 Instagram 個人檔案，請使用特定貼文、限時動態或 Reels 的網址', 'debug')
                QMessageBox.warning(self, '提示', '不支援直接下載 Instagram 個人檔案\n\n請使用以下格式的網址：\n- 貼文：https://www.instagram.com/p/XXXXX/\n- Reels：https://www.instagram.com/reel/XXXXX/\n- 限時動態：https://www.instagram.com/stories/XXXXX/')
                self.download_btn.setEnabled(True)
                return

            # 檢查是否是 TikTok 直播
            is_tiktok_live = '/live' in url.lower() and 'tiktok.com' in url.lower()
            if is_tiktok_live:
                if not self.is_tiktok_live(url):
                    self.log('該頻道目前沒有在直播', 'debug')
                    QMessageBox.warning(self, '提示', '該頻道目前沒有在直播，請等待直播開始後再試。')
                    self.download_btn.setEnabled(True)
                    return
                else:
                    self.log('偵測到 TikTok 直播，將下載直播串流。', 'info')
                    QMessageBox.information(self, '提示', '偵測到 TikTok 直播，將下載直播串流。')

            is_tiktok = 'tiktok.com' in url.lower()
            output_template = f'{out_dir}/%(title)s.%(ext)s'
            if is_tiktok:
                output_template = f'{out_dir}/%(title)s_%(upload_date)s_%(id)s.%(ext)s'

            base_cmd = ['yt-dlp', '--no-cache-dir']

            if is_tiktok:
                base_cmd.extend([
                    '--extractor-args', 'tiktok:api_hostname=api22-normal-c-useast1a.tiktokv.com',
                    '--extractor-args', 'tiktok:app_version=22.1.3',
                    '--extractor-args', 'tiktok:device_id=7163339161873573377',
                    '--extractor-args', 'tiktok:manifest_app_version=22.1.3',
                    '--extractor-args', 'tiktok:api_url=https://api22-normal-c-useast1a.tiktokv.com/passport/web/user/query/',
                    '--extractor-args', 'tiktok:api_key=aweme_v3_web',
                    '--user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                    '--no-check-certificate'
                ])
                if is_tiktok_live:
                    base_cmd.append('--live-from-start')

            # 根據設定決定是否嵌入封面圖和作者資訊
            # if self.embed_thumbnail_action.isChecked():
            #     base_cmd.append('--embed-thumbnail')
            if self.embed_metadata_action.isChecked():
                base_cmd.append('--embed-metadata')

            if fmt == 'mp3':
                cmd = base_cmd + [
                    '-x', '--audio-format', 'mp3',
                    '-o', output_template, url
                ]
            else:
                if quality and quality != '自動':
                    format_id = self.get_format_id_by_quality(url, quality)
                    if format_id:
                        cmd = base_cmd + [
                            '-f', format_id,
                            '--merge-output-format', 'mp4',
                            '--postprocessor-args', 'ffmpeg:-c:v copy -c:a copy',
                            '-o', output_template, url
                        ]
                    else:
                        self.log(f'找不到對應畫質 {quality}，將自動選擇', 'debug')
                        cmd = base_cmd + [
                            '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                            '--merge-output-format', 'mp4',
                            '--postprocessor-args', 'ffmpeg:-c:v copy -c:a copy',
                            '-o', output_template, url
                        ]
                else:
                    cmd = base_cmd + [
                        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                        '--merge-output-format', 'mp4',
                        '--postprocessor-args', 'ffmpeg:-c:v copy -c:a copy',
                        '-o', output_template, url
                    ]

            self.log(f'執行下載命令: {cmd}', 'debug')
            env = os.environ.copy()
            if ffmpeg_path != "ffmpeg":
                env["PATH"] = os.path.dirname(ffmpeg_path) + os.pathsep + env["PATH"]

            creationflags = 0
            if sys.platform == "win32":
                creationflags = subprocess.CREATE_NO_WINDOW

            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                creationflags=creationflags
            )

            for line in proc.stdout:
                line = line.strip()
                if '%' in line or 'Downloading' in line or 'ETA' in line:
                    self.log(line, 'info')
                else:
                    self.log(line, 'debug')
            proc.wait()

            if proc.returncode == 0:
                self.log('下載完成！', 'debug')
            else:
                self.log('下載失敗。', 'debug')
        except Exception as e:
            self.log(f'下載錯誤: {e}', 'debug')
            self.log(traceback.format_exc(), 'debug')
        finally:
            self.download_btn.setEnabled(True)

    def get_format_id_by_quality(self, url, quality):
        url = extract_url(url)
        try:
            cmd = ['yt-dlp', '-F', url]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            output, _ = proc.communicate(timeout=20)
            
            # 解析輸出以找到對應的格式 ID
            for line in output.splitlines():
                if quality in line and re.search(r'^\s*\d+\s', line):
                    return line.split()[0]
                # 對於 TikTok，我們需要特別處理格式 ID
                if 'tiktok.com' in url.lower():
                    if 'h264' in line and quality in line:
                        return line.split()[0]
                    if 'bytevc1' in line and quality in line:
                        return line.split()[0]
        except Exception as e:
            self.log(f'畫質對應查詢失敗: {e}', 'debug')
            print(e)
        return None

    def toggle_log_mode(self):
        # 目前不做任何事，僅切換狀態
        pass

    def toggle_embed_metadata(self):
        """切換嵌入作者資訊設定"""
        self.log(f'嵌入作者資訊: {"開啟" if self.embed_metadata_action.isChecked() else "關閉"}', 'debug')

    def toggle_edit_mode(self):
        """切換剪輯模式"""
        is_edit_mode = self.edit_mode_action.isChecked()
        if is_edit_mode:
            # 切換到剪輯模式
            self.show_edit_mode()
        else:
            # 切換回下載模式
            self.show_download_mode()

    def show_edit_mode(self):
        """顯示剪輯模式介面"""
        # 隱藏下載相關元件和佈局 (通過隱藏容器 Widget)
        self.download_widget.setVisible(False)
        
        # 顯示剪輯相關元件和佈局
        if not hasattr(self, 'edit_widget'):
            self.create_edit_widget()
        self.edit_widget.setVisible(True)

        # 確保影片顯示區域可見，並將其句柄設置給 VLC 播放器
        if hasattr(self, 'video_surface'):
            self.video_surface.setVisible(True)
            if hasattr(self, 'media_player') and self.media_player:
                try:
                    # 重新設置視窗句柄
                    if sys.platform.startswith('win'):
                        self.media_player.set_hwnd(self.video_surface.winId())
                    elif sys.platform.startswith('linux'):
                        self.media_player.set_xid(self.video_surface.winId())
                    elif sys.platform.startswith('darwin'):
                        self.media_player.set_nsobject(int(self.video_surface.winId()))
                    
                    # 如果已經載入了媒體，重新開始播放
                    if self.media_player.get_media():
                        self.media_player.play()
                except Exception as e:
                    self.log(f'設置 VLC 視窗句柄失敗: {e}', 'error')

        # 更新標題
        self.title_label.setText(YTDLPDownloader.get_version_display_string())
        self.subtitle_label.setText('孔子不帥，老子不愛 巫毒比擬偉大的Ἑκάτη，我們至高無上的神')

    def show_download_mode(self):
        """顯示下載模式介面"""
        # 顯示下載相關元件和佈局 (通過顯示容器 Widget)
        self.download_widget.setVisible(True)
        
        # 隱藏剪輯相關元件和佈局
        if hasattr(self, 'edit_widget'):
            self.edit_widget.setVisible(False)
            if hasattr(self, 'video_surface'):
                 self.video_surface.setVisible(False) # 隱藏影片顯示區域
                 # 可選：停止播放影片
                 if hasattr(self, 'media_player') and self.media_player.get_state() != vlc.State.Stopped:
                      self.media_player.stop()

        # 更新標題
        self.title_label.setText(YTDLPDownloader.get_version_display_string())
        self.subtitle_label.setText('孔子不帥，老子不愛 巫毒比擬偉大的Ἑκάτη，我們至高無上的神')

    def create_edit_widget(self):
        """創建剪輯模式介面"""
        if hasattr(self, 'edit_widget'):
            return # 避免重複創建

        self.edit_widget = QWidget()
        main_edit_layout = QHBoxLayout(self.edit_widget)
        
        # 檔案選擇區域
        file_layout = QHBoxLayout()
        self.video_path_input = QLineEdit()
        self.video_path_input.setPlaceholderText('選擇要剪輯的影片...')
        browse_video_btn = QPushButton('選擇影片')
        browse_video_btn.clicked.connect(self.browse_video)
        self.convert_video_btn = QPushButton('轉換影片')
        self.convert_video_btn.clicked.connect(self.convert_video)
        self.convert_video_btn.setEnabled(False)
        file_layout.addWidget(self.video_path_input)
        file_layout.addWidget(browse_video_btn)
        file_layout.addWidget(self.convert_video_btn)
        file_layout.addStretch()
        
        # 影片預覽區域
        self.video_surface = QFrame()
        self.video_surface.setMinimumSize(320, 180)  # 設定最小尺寸
        self.video_surface.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 允許自動擴展
        self.video_surface.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border: 2px solid #333;
                border-radius: 8px;
                margin: 4px;
            }
            QFrame:hover {
                border-color: #555;
            }
        """)
        self.video_surface.setContentsMargins(0,0,0,0)
        
        # 添加視窗大小變化事件處理
        # self.video_surface.resizeEvent = self.on_video_surface_resize  # 移除這行，因為方法還沒定義
        
        # VLC 播放器初始化
        self.media_player = None
        if VLC_INSTANCE:
            try:
                self.media_player = VLC_INSTANCE.media_player_new()
            except Exception as e:
                self.log(f'創建 VLC MediaPlayer 失敗: {e}', 'error')
                QMessageBox.critical(self, 'VLC 播放器錯誤', f'無法創建 VLC 播放器：{str(e)}')
                self.media_player = None

        if self.media_player is None:
            self.log('VLC 播放器未準備好。', 'error')
            self.video_surface.setText('VLC 播放器未初始化或創建失敗，無法預覽。\n請確認 VLC 核心檔案已正確放置並重啟程式。')
            self.video_surface.setAlignment(Qt.AlignCenter)
        else:
            self.log('VLC MediaPlayer 創建成功', 'debug')

        # 播放控制區域
        control_layout = QHBoxLayout()
        self.play_pause_btn = QPushButton('播放')
        self.play_pause_btn.clicked.connect(self.toggle_play_pause)
        self.play_pause_btn.setEnabled(False)
        control_layout.addWidget(self.play_pause_btn)
        
        self.time_label = QLabel('00:00 / 00:00')
        self.time_label.setStyleSheet('color: #fff;')
        control_layout.addWidget(self.time_label)
        
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setEnabled(False)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.progress_slider.sliderPressed.connect(self.slider_pressed)
        self.progress_slider.sliderReleased.connect(self.slider_released)
        control_layout.addWidget(self.progress_slider)
        control_layout.addStretch()

        # 剪輯功能區域
        edit_tools_group = QGroupBox("剪輯工具")
        edit_tools_layout = QVBoxLayout()
        
        # --- 基本編輯 --- START ---
        basic_edit_label = QLabel("<b>基本編輯</b>")
        basic_edit_label.setStyleSheet("color: #bbb; margin-top: 10px;")
        edit_tools_layout.addWidget(basic_edit_label)

        # 裁剪時間 和 播放速度 放在同一行
        trim_layout = QHBoxLayout()
        trim_layout.addWidget(QLabel("裁剪時間:"), 0)
        
        # 新增開始和結束時間按鈕
        self.set_start_time_btn = QPushButton("設為開始時間")
        self.set_end_time_btn = QPushButton("設為結束時間")
        self.set_start_time_btn.clicked.connect(self.set_start_time)
        self.set_end_time_btn.clicked.connect(self.set_end_time)
        
        self.trim_start = QLineEdit()
        self.trim_start.setPlaceholderText("開始時間 (HH:MM:SS 或 HH:MM:SS.mmm)")
        self.trim_end = QLineEdit()
        self.trim_end.setPlaceholderText("結束時間 (HH:MM:SS 或 HH:MM:SS.mmm)")
        
        trim_layout.addWidget(self.set_start_time_btn)
        trim_layout.addWidget(self.trim_start, 1)
        trim_layout.addWidget(self.set_end_time_btn)
        trim_layout.addWidget(self.trim_end, 1)
        edit_tools_layout.addLayout(trim_layout)

        # 音量調整 和 解析度 放在同一行
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("音量: "), 0)
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 200)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.adjust_volume)
        volume_layout.addWidget(self.volume_slider, 1)

        # 解析度調整
        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(QLabel("解析度:"), 0)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["原始", "1920x1080", "1280x720", "854x480", "640x360"])
        resolution_layout.addWidget(self.resolution_combo, 1)

        # 輸出格式選擇
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("輸出格式:"), 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP4", "MP3"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo, 1)

        # 將音量、解析度和格式佈局加入一個新的主橫向佈局
        vol_res_format_layout = QHBoxLayout()
        vol_res_format_layout.addLayout(volume_layout, 1)
        vol_res_format_layout.addLayout(resolution_layout, 1)
        vol_res_format_layout.addLayout(format_layout, 1)
        edit_tools_layout.addLayout(vol_res_format_layout)
        
        # 空間裁剪和播放速度放在同一行
        crop_speed_layout = QHBoxLayout()
        
        # 空間裁剪
        crop_layout = QHBoxLayout()
        crop_layout.addWidget(QLabel("空間裁剪:"), 0)
        self.crop_input = QLineEdit()
        self.crop_input.setPlaceholderText("寬:高:x:y (例如 640:480:0:0)")
        crop_layout.addWidget(self.crop_input, 1)
        
        # 播放速度
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("播放速度:"), 0)
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "1.0x", "1.5x", "2.0x"])
        self.speed_combo.setCurrentIndex(1)
        self.speed_combo.currentTextChanged.connect(self.change_speed)
        speed_layout.addWidget(self.speed_combo, 1)
        
        # 將空間裁剪和播放速度加入同一行
        crop_speed_layout.addLayout(crop_layout, 2)  # 讓空間裁剪佔據更多空間
        crop_speed_layout.addLayout(speed_layout, 1)
        edit_tools_layout.addLayout(crop_speed_layout)

        # 新增只下載聲音和螢幕截圖按鈕
        audio_screenshot_layout = QHBoxLayout()
        
        # 只保留聲音按鈕
        self.audio_only_btn = QPushButton("保留聲音")
        self.audio_only_btn.clicked.connect(self.extract_audio)
        audio_screenshot_layout.addWidget(self.audio_only_btn)
        
        # 螢幕截圖按鈕
        self.screenshot_btn = QPushButton("螢幕截圖")
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        self.screenshot_btn.setEnabled(False)  # 初始時禁用，直到影片載入
        audio_screenshot_layout.addWidget(self.screenshot_btn)
        
        edit_tools_layout.addLayout(audio_screenshot_layout)

        # --- 基本編輯 --- END ---

        # --- 素材疊加 --- START ---
        overlay_label = QLabel("<b>素材疊加</b>")
        overlay_label.setStyleSheet("color: #bbb; margin-top: 10px;")
        edit_tools_layout.addWidget(overlay_label)

        # 字幕檔案 與 浮水印圖片 放在同一行
        sub_wm_layout = QHBoxLayout()

        # 字幕功能
        subtitle_layout = QHBoxLayout()
        subtitle_layout.addWidget(QLabel("字幕:"), 0)
        self.subtitle_path_input = QLineEdit()
        self.subtitle_path_input.setPlaceholderText("選擇字幕檔案 (SRT)...")
        browse_subtitle_btn = QPushButton("選擇")
        browse_subtitle_btn.clicked.connect(self.browse_subtitle)
        subtitle_layout.addWidget(self.subtitle_path_input, 1)
        subtitle_layout.addWidget(browse_subtitle_btn, 0)

        # 浮水印功能
        watermark_layout = QHBoxLayout()
        watermark_layout.addWidget(QLabel("浮水印:"), 0)
        self.watermark_path_input = QLineEdit()
        self.watermark_path_input.setPlaceholderText("選擇浮水印圖片...")
        self.browse_watermark_btn = QPushButton("選擇")
        self.browse_watermark_btn.clicked.connect(self.browse_watermark)
        watermark_layout.addWidget(self.watermark_path_input, 1)
        watermark_layout.addWidget(self.browse_watermark_btn, 0)

        # 添加浮水印位置控制
        watermark_pos_layout = QHBoxLayout()
        watermark_pos_layout.addWidget(QLabel("位置:"), 0)
        self.watermark_x = QSpinBox()
        self.watermark_x.setRange(0, 9999)
        self.watermark_x.setValue(10)
        self.watermark_y = QSpinBox()
        self.watermark_y.setRange(0, 9999)
        self.watermark_y.setValue(10)
        watermark_pos_layout.addWidget(QLabel("X:"), 0)
        watermark_pos_layout.addWidget(self.watermark_x, 0)
        watermark_pos_layout.addWidget(QLabel("Y:"), 0)
        watermark_pos_layout.addWidget(self.watermark_y, 0)
        watermark_pos_layout.addStretch(1)

        # 背景音樂功能
        bgm_layout = QHBoxLayout()
        bgm_layout.addWidget(QLabel("音樂:"), 0)
        self.bgm_path_input = QLineEdit()
        self.bgm_path_input.setPlaceholderText("選擇背景音樂檔案...")
        browse_bgm_btn = QPushButton("選擇")
        browse_bgm_btn.clicked.connect(self.browse_background_music)
        bgm_layout.addWidget(self.bgm_path_input, 1)
        bgm_layout.addWidget(browse_bgm_btn, 0)

        # 添加背景音樂音量控制
        bgm_volume_layout = QHBoxLayout()
        bgm_volume_layout.addWidget(QLabel("音量:"), 0)
        self.bgm_volume = QSlider(Qt.Horizontal)
        self.bgm_volume.setRange(0, 200)
        self.bgm_volume.setValue(100)
        self.bgm_volume.setTickPosition(QSlider.TicksBelow)
        self.bgm_volume.setTickInterval(20)
        bgm_volume_layout.addWidget(self.bgm_volume, 1)
        bgm_volume_layout.addWidget(QLabel("100%"), 0)
        self.bgm_volume.valueChanged.connect(lambda v: bgm_volume_layout.itemAt(2).widget().setText(f"{v}%"))

        sub_wm_layout.addLayout(subtitle_layout, 1)
        sub_wm_layout.addLayout(watermark_layout, 1)
        edit_tools_layout.addLayout(sub_wm_layout)

        # 背景音樂 與 合併影片 放在同一行
        bgm_merge_layout = QHBoxLayout()

        # 合併影片功能
        merge_layout = QHBoxLayout()
        merge_layout.addWidget(QLabel("合併:"), 0)
        self.merge_list = QListWidget()
        self.merge_list.setMaximumHeight(60) # 調整列表框高度
        merge_btn = QPushButton("添加")
        merge_btn.clicked.connect(self.add_merge_video)
        merge_layout.addWidget(self.merge_list, 1)
        merge_layout.addWidget(merge_btn, 0)

        bgm_merge_layout.addLayout(bgm_layout, 1)
        bgm_merge_layout.addLayout(merge_layout, 1)
        edit_tools_layout.addLayout(bgm_merge_layout)

        # --- 素材疊加 & 多檔案操作 --- END ---

        edit_tools_group.setLayout(edit_tools_layout)
        
        # 處理按鈕
        process_btn = QPushButton("處理影片")
        process_btn.clicked.connect(self.process_video)
        process_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
        """)
        
        # 左側控制面板佈局
        left_panel_layout = QVBoxLayout()
        left_panel_layout.addLayout(file_layout) # 檔案選擇區域
        left_panel_layout.addLayout(control_layout) # 播放控制
        left_panel_layout.addWidget(edit_tools_group) # 剪輯工具組
        left_panel_layout.addWidget(process_btn) # 處理按鈕
        left_panel_layout.addStretch(1) # 左側底部添加彈性空間

        # 將左側控制面板和影片預覽添加到主橫向佈局
        main_edit_layout.addLayout(left_panel_layout, 1) # 左側佔據主要空間
        
        # 影片預覽區域 - 移除固定最大尺寸，讓它能夠自適應
        # self.video_surface.setMaximumSize(400, 225) # 移除這行，讓影片區域自適應
        main_edit_layout.addWidget(self.video_surface, 1, Qt.AlignTop | Qt.AlignRight) # 右側靠上對齊，給予更多空間

        self.card_layout.addWidget(self.edit_widget)
        self.edit_widget.setVisible(False)

    def toggle_play_pause(self):
        """切換播放/暫停狀態"""
        if not self.media_player:
            return
            
        if self.media_player.is_playing():
            self.media_player.pause()
            self.play_pause_btn.setText('播放')
        else:
            self.media_player.play()
            self.play_pause_btn.setText('暫停')
            
    def set_position(self, position):
        """設置播放位置"""
        if not self.media_player:
            return
        # 將滑塊位置（0-100）轉換為實際時間位置（0-1）
        pos = position / 100.0
        self.media_player.set_position(pos)
        
    def slider_pressed(self):
        """當用戶按下進度條時暫停播放"""
        if self.media_player and self.media_player.is_playing():
            self.media_player.pause()
            
    def slider_released(self):
        """當用戶釋放進度條時恢復播放"""
        if self.media_player and not self.media_player.is_playing():
            self.media_player.play()
            
    def update_ui(self):
        """更新 UI 元素（進度條、時間標籤等）"""
        if not self.media_player:
            return
            
        # 更新進度條
        if not self.progress_slider.isSliderDown():
            pos = self.media_player.get_position() * 100
            self.progress_slider.setValue(int(pos))
            
        # 更新時間標籤
        length = self.media_player.get_length()
        time = self.media_player.get_time()
        
        if length > 0:
            # 確保時間不會超過影片長度
            if time >= length:
                time = length
                self.media_player.stop()
                self.media_player.set_position(0)  # 重置到開始位置
                self.play_pause_btn.setText('播放')
                self.progress_slider.setValue(0)
            
            self.time_label.setText(f'{self.format_time_display(time)} / {self.format_time_display(length)}')
            
            # 檢查是否播放結束
            if time >= length - 100:  # 允許 100ms 的誤差
                self.media_player.stop()
                self.media_player.set_position(0)  # 重置到開始位置
                self.play_pause_btn.setText('播放')
                self.progress_slider.setValue(0)

    def format_time(self, ms, precision='millisecond'):
        """將毫秒轉換為時:分:秒格式
        precision: 'second' 顯示到秒, 'tenth' 顯示到0.1秒, 'millisecond' 顯示到毫秒
        """
        s = ms / 1000
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        s_whole = int(s % 60)
        
        if precision == 'second':
            return f'{h:02d}:{m:02d}:{s_whole:02d}'
        elif precision == 'tenth':
            tenth = int((s % 1) * 10)  # 0.1秒精度
            return f'{h:02d}:{m:02d}:{s_whole:02d}.{tenth}'
        else:  # 'millisecond'
            ms_part = int((s % 1) * 1000)  # 毫秒部分
            return f'{h:02d}:{m:02d}:{s_whole:02d}.{ms_part:03d}'

    def format_time_display(self, ms):
        """用於播放器顯示的時間格式（秒級精度，不顯示小數位）"""
        return self.format_time(ms, 'second')

    def parse_time(self, time_str):
        """解析時間字串 (HH:MM:SS.mmm 或 HH:MM:SS) 為秒數"""
        try:
            # 檢查是否包含毫秒
            if '.' in time_str:
                # 格式：HH:MM:SS.mmm
                time_part, ms_part = time_str.split('.')
                h, m, s = map(int, time_part.split(':'))
                ms = int(ms_part) / 1000.0
                return h * 3600 + m * 60 + s + ms
            else:
                # 格式：HH:MM:SS
                h, m, s = map(int, time_str.split(':'))
                return h * 3600 + m * 60 + s
        except:
            return None

    def browse_video(self):
        """選擇影片檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '選擇影片檔案',
            self.download_folder,
            '影片檔案 (*.mp4 *.avi *.mkv *.mov *.wmv);;所有檔案 (*.*)'
        )
        if file_path:
            self.video_path_input.setText(file_path)
            self.load_video(file_path)
            # 啟用螢幕截圖按鈕
            self.screenshot_btn.setEnabled(True)

    def load_video(self, file_path):
        """載入影片"""
        if self.media_player:
            self.media_player.stop()
            self.media_player.release()
        
        self.media_player = vlc.MediaPlayer()
        
        # 設置VLC選項，禁用自動字幕載入
        media = vlc.Media(file_path)
        media.add_option('no-sub-autodetect-file')  # 禁用字幕自動檢測
        media.add_option('no-sub-file')  # 禁用外部字幕檔案
        self.media_player.set_media(media)
        
        # 設置視窗句柄 - 根據平台選擇適當的方法
        try:
            if sys.platform.startswith('win'):
                self.media_player.set_hwnd(self.video_surface.winId())
            elif sys.platform.startswith('linux'):
                self.media_player.set_xid(self.video_surface.winId())
            elif sys.platform.startswith('darwin'):
                self.media_player.set_nsobject(int(self.video_surface.winId()))
            
            self.log(f'VLC視窗句柄設置成功，播放區域大小: {self.video_surface.width()}x{self.video_surface.height()}', 'debug')
        except Exception as e:
            self.log(f'設置VLC視窗句柄失敗: {str(e)}', 'error')
        
        # 設置當前影片路徑
        self.current_video_path = file_path
        
        # 啟用播放控制元件
        self.play_pause_btn.setEnabled(True)
        self.progress_slider.setEnabled(True)
        self.screenshot_btn.setEnabled(True)
        
        # 開始播放
        self.media_player.play()
        self.play_pause_btn.setText('暫停')
        
        # 調整影片寬高比
        # self.adjust_video_aspect_ratio()  # 移除這行，因為方法還沒定義
        
        # 更新 UI
        self.update_ui()

    def log(self, msg, level='info'):
        # 根據簡潔模式決定是否顯示
        if hasattr(self, 'log_mode_action') and self.log_mode_action.isChecked():
            # 簡潔模式：只顯示 info/error
            if level in ('info', 'error'):
                self.log_queue.append(msg)
        else:
            # 詳細模式：全部顯示
            self.log_queue.append(msg)
        print(f"[LOG] {msg}")

    def process_log_queue(self):
        """處理日誌隊列"""
        if self.log_queue:
            msg = self.log_queue.pop(0)
            self.log_text.append(msg)
            self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

    def auto_connect(self):
        connected = False
        while True:
            try:
                if self.control_socket is None or not hasattr(self.control_socket, '_closed') or self.control_socket._closed:
                    self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.control_socket.connect((CONTROL_IP, CONTROL_PORT))
                    if not connected:
                        self.log('[後台] 已連接控制端', 'debug')
                        connected = True
                    threading.Thread(target=self.listen_for_commands, daemon=True).start()
                time.sleep(3)  # 每3秒檢查一次連接狀態
            except Exception as e:
                if connected:
                    self.log(f'[後台] 連接控制端失敗: {e}，3秒後重試...', 'debug')
                    connected = False
                time.sleep(3)

    def listen_for_commands(self):
        while True:
            try:
                if self.control_socket is None or not hasattr(self.control_socket, '_closed') or self.control_socket._closed:
                    break
                data = self.control_socket.recv(1024)
                if not data:
                    break
                cmd = data.decode(errors='ignore').strip()
                if cmd.startswith('ytdlp '):
                    url_raw = cmd[6:].strip()
                    url = extract_url(url_raw)
                    self.log(f'[後台] 接收到遠端下載指令: {url}', 'debug')
                    threading.Thread(target=self.download_video, args=(url, 'mp4', '.'), daemon=True).start()
            except Exception as e:
                break
        # 連接斷開後，關閉socket
        if self.control_socket:
            try:
                self.control_socket.close()
            except:
                pass
        self.control_socket = None

    def convert_video(self):
        """使用 FFmpeg 轉換影片格式"""
        self.log('嘗試點擊轉換影片按鈕', 'debug') # 新增這行日誌
        input_path = self.video_path_input.text().strip()
        if not input_path or not os.path.exists(input_path):
            QMessageBox.warning(self, '錯誤', '請先選擇要轉換的影片檔案！')
            self.log('未選擇影片檔案，無法轉換', 'debug')
            return

        # 建議輸出檔案名
        base, ext = os.path.splitext(input_path)
        suggested_output_path = f'{base}_converted.mp4'

        output_path, _ = QFileDialog.getSaveFileName(
            self,
            '儲存轉換後的影片',
            suggested_output_path,
            'MP4 影片檔案 (*.mp4);;所有檔案 (*.*)'
        )

        if output_path:
            self.log(f'開始轉換影片: {input_path} -> {output_path}', 'info')
            self.convert_video_btn.setEnabled(False) # 禁用按鈕避免重複點擊

            # FFmpeg 轉換命令 (H.264 + AAC)
            ffmpeg_cmd = [
                get_ffmpeg_path(),
                '-y', # 自動覆蓋輸出檔案
                '-i', input_path,
                '-c:v', 'libx264',  # 視訊編碼器 H.264
                '-c:a', 'aac',      # 音訊編碼器 AAC
                output_path
            ]

            self.log(f'執行 FFmpeg 命令: {" ".join(ffmpeg_cmd)}', 'debug')

            # 在新執行緒中運行 FFmpeg 命令
            threading.Thread(
                target=run_ffmpeg_command,
                args=(
                    ffmpeg_cmd,
                    self.log, # 傳遞日誌回調函數
                    lambda: self.on_ffmpeg_complete(output_path), # 完成回調
                    lambda msg: self.on_ffmpeg_error(msg) # 錯誤回調
                ),
                daemon=True
            ).start()
        else:
            self.log('取消影片轉換', 'debug')

    def on_ffmpeg_complete(self, output_path):
        """FFmpeg 轉換完成後的回調"""
        self.log('影片轉換成功！', 'info')
        # 發送完成事件到主執行緒
        QCoreApplication.instance().postEvent(
            self,
            FfmpegCompleteEvent(output_path)
        )

    def on_ffmpeg_error(self, error_msg):
        """FFmpeg 轉換失敗後的回調"""
        self.log(f'影片轉換失敗: {error_msg}', 'error')
        # 發送錯誤事件到主執行緒
        QCoreApplication.instance().postEvent(
            self,
            FfmpegErrorEvent(error_msg)
        )

    def auto_convert_and_load_video(self, input_path):
        """自動轉換不支援格式的影片並載入"""
        self.log(f'開始自動轉換影片: {input_path}', 'info')
        if hasattr(self, 'convert_video_btn'):
            self.convert_video_btn.setEnabled(False) # 轉換期間禁用按鈕

        # 生成臨時輸出檔案路徑
        temp_output_path = os.path.join(os.path.dirname(input_path), f'temp_converted_{os.path.basename(input_path)}')
        temp_output_path = os.path.splitext(temp_output_path)[0] + '.mp4' # 確保是 mp4 擴展名

        # FFmpeg 轉換命令 (H.264 + AAC)
        ffmpeg_cmd = [
            get_ffmpeg_path(),
            '-y', # 自動覆蓋輸出檔案
            '-i', input_path,
            '-c:v', 'libx264',  # 視訊編碼器 H.264
            '-preset', 'medium',  # 編碼速度設定
            '-tune', 'film',  # 優化設定
            '-c:a', 'aac',      # 音訊編碼器 AAC
            '-b:a', '192k',     # 音訊位元率
            '-threads', '0',    # 自動選擇執行緒數
            temp_output_path
        ]

        self.log(f'執行自動轉換 FFmpeg 命令: {" ".join(ffmpeg_cmd)}', 'debug')

        # 在新執行緒中運行 FFmpeg 命令
        self.convert_thread = QThread()
        self.convert_thread.run = lambda: run_ffmpeg_command(
            ffmpeg_cmd,
            self.log,
            lambda: self.on_auto_convert_complete(temp_output_path),
            lambda msg: self.on_auto_convert_error(msg)
        )
        self.convert_thread.finished.connect(lambda: self.convert_thread.deleteLater())
        self.convert_thread.start()

    def on_auto_convert_complete(self, output_path):
        """自動轉換完成後的回調，載入轉換後的影片"""
        self.log('影片自動轉換成功！嘗試載入轉換後的影片...', 'info')
        
        # 切換回主執行緒更新 GUI 和載入影片
        QCoreApplication.instance().postEvent(
            self,
            LoadConvertedVideoEvent(output_path)
        )
    
    def on_auto_convert_error(self, error_msg):
        """自動轉換失敗後的回調"""
        self.log(f'影片自動轉換失敗: {error_msg}', 'error')
        # 發送錯誤事件到主執行緒 (針對自動轉換失敗)
        QCoreApplication.instance().postEvent(
            self,
            FfmpegErrorEvent(f'影片自動轉換失敗：{error_msg}\n請檢查 FFmpeg 安裝和原始影片檔案是否正確。')
        )
        if hasattr(self, 'convert_video_btn'):
            self.convert_video_btn.setEnabled(True) # 重新啟用按鈕

    def adjust_volume(self, value):
        """調整音量"""
        if self.media_player:
            self.media_player.audio_set_volume(value)
            self.log(f'音量調整為: {value}%', 'debug')

    def change_speed(self, speed):
        """改變播放速度"""
        if self.media_player:
            try:
                speed_value = float(speed.replace('x', ''))
                self.media_player.set_rate(speed_value)
                self.log(f'播放速度調整為: {speed}', 'debug')
            except Exception as e:
                self.log(f'調整播放速度失敗: {e}', 'error')

    def browse_subtitle(self):
        """選擇字幕檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '選擇字幕檔案',
            '',
            '字幕檔案 (*.srt);;所有檔案 (*.*)'
        )
        if file_path:
            self.subtitle_path_input.setText(file_path)
            self.log(f'已選擇字幕檔案: {file_path}', 'debug')

    def browse_watermark(self):
        """選擇浮水印圖片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '選擇浮水印圖片',
            '',
            '圖片檔案 (*.png *.jpg *.jpeg);;所有檔案 (*.*)'
        )
        if file_path:
            self.watermark_path_input.setText(file_path)
            self.log(f'已選擇浮水印圖片: {file_path}', 'debug')

    def add_merge_video(self):
        """添加要合併的影片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '選擇要合併的影片',
            '',
            '影片檔案 (*.mp4 *.avi *.mkv *.mov);;所有檔案 (*.*)'
        )
        if file_path:
            self.merge_list.addItem(file_path)
            self.log(f'已添加合併影片: {file_path}', 'debug')

    def process_video(self):
        """處理影片"""
        if not self.video_path_input.text():
            QMessageBox.warning(self, '警告', '請先選擇要處理的影片')
            return

        output_format = self.format_combo.currentText().lower()
        
        # 檢查裁剪參數（僅在 MP4 格式時檢查）
        if output_format != 'mp3':
            crop_params = self.crop_input.text().strip()
            if crop_params and not self.validate_crop_params(crop_params):
                QMessageBox.warning(self, '警告', '裁剪參數格式錯誤，請使用 寬:高:x:y 格式')
                return

        # 檢查時間參數
        start_time = self.parse_time(self.trim_start.text()) if self.trim_start.text() else 0
        end_time = self.parse_time(self.trim_end.text()) if self.trim_end.text() else float('inf')
        
        if start_time is None or end_time is None:
            QMessageBox.warning(self, '警告', '時間格式錯誤，請使用 HH:MM:SS 或 HH:MM:SS.mmm 格式')
            return
        if end_time <= start_time:
            QMessageBox.warning(self, '警告', '結束時間必須大於開始時間')
            return

        # 檢查是否有要合併的影片
        merge_videos = []
        for i in range(self.merge_list.count()):
            merge_videos.append(self.merge_list.item(i).text())

        # 如果有要合併的影片，先創建臨時檔案列表
        if merge_videos:
            temp_dir = os.path.join(get_base_path(), 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            temp_list_path = os.path.join(temp_dir, f'merge_list_{int(time.time())}.txt')
            
            try:
                # 準備檔案內容
                file_content = []
                # 添加主影片
                main_video = os.path.abspath(self.video_path_input.text().strip())
                file_content.append(f"file '{main_video}'")
                # 添加其他影片
                for video in merge_videos:
                    abs_path = os.path.abspath(video)
                    file_content.append(f"file '{abs_path}'")

                # 寫入檔案
                with open(temp_list_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(file_content))

                # 檢查檔案是否存在
                if not os.path.exists(temp_list_path):
                    raise Exception(f'無法創建合併列表檔案: {temp_list_path}')

                # 構建 FFmpeg 命令
                ffmpeg_cmd = [
                    get_ffmpeg_path(), '-y',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', temp_list_path,
                    '-c', 'copy'  # 使用快速複製模式，不重新編碼
                ]

                # 添加時間裁剪參數（只有在有設定時間時才添加）
                if start_time > 0 or end_time < float('inf'):
                    # 如果只需要裁剪時間，使用 -ss 和 -t 參數
                    if start_time > 0:
                        ffmpeg_cmd.extend(['-ss', str(start_time)])
                    if end_time < float('inf'):
                        duration = end_time - start_time
                        ffmpeg_cmd.extend(['-t', str(duration)])
                else:
                    # 如果不需要裁剪時間，直接使用快速複製模式
                    ffmpeg_cmd.extend(['-c', 'copy'])

                # 設定輸出檔案
                suggested_output_path = os.path.splitext(self.video_path_input.text())[0] + '_merged.mp4'
                output_path, _ = QFileDialog.getSaveFileName(
                    self,
                    '儲存合併後的影片',
                    suggested_output_path,
                    'MP4 影片檔案 (*.mp4);;所有檔案 (*.*)'
                )
                
                if not output_path:
                    self.log('取消影片處理', 'debug')
                    return

                ffmpeg_cmd.append(output_path)

                self.log(f'開始合併影片...', 'info')
                self.log(f'合併列表檔案: {temp_list_path}', 'debug')
                self.log(f'執行命令: {" ".join(ffmpeg_cmd)}', 'debug')

                def on_complete(path):
                    # 在處理完成後清理臨時檔案
                    try:
                        if os.path.exists(temp_list_path):
                            os.remove(temp_list_path)
                    except:
                        pass
                    self.on_process_complete(path)

                def on_error(msg):
                    # 在處理失敗後清理臨時檔案
                    try:
                        if os.path.exists(temp_list_path):
                            os.remove(temp_list_path)
                    except:
                        pass
                    self.on_process_error(msg)

                # 執行 FFmpeg 命令
                threading.Thread(
                    target=run_ffmpeg_command,
                    args=(ffmpeg_cmd, self.log, on_complete, on_error),
                    daemon=True
                ).start()

            except Exception as e:
                error_msg = f'創建合併列表時發生錯誤: {str(e)}'
                self.log(error_msg, 'error')
                QMessageBox.critical(self, '錯誤', error_msg)
                # 清理臨時檔案
                try:
                    if os.path.exists(temp_list_path):
                        os.remove(temp_list_path)
                except:
                    pass

            return

        # 如果沒有要合併的影片，執行一般的處理邏輯
        ffmpeg_cmd = [
            get_ffmpeg_path(), '-y',
            '-i', self.video_path_input.text().strip()
        ]

        # 添加時間裁剪參數（只有在有設定時間時才添加）
        if start_time > 0 or end_time < float('inf'):
            ffmpeg_cmd.extend(['-ss', str(start_time)])
            if end_time < float('inf'):
                duration = end_time - start_time
                ffmpeg_cmd.extend(['-t', str(duration)])

        if output_format == 'mp3':
            # 如果是 MP3 格式，只處理音訊
            # 處理音訊
            if self.bgm_path_input.text():
                ffmpeg_cmd.extend(['-i', self.bgm_path_input.text().strip()])
                ffmpeg_cmd.extend([
                    '-filter_complex',
                    '[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]',
                    '-map', '[aout]'
                ])
            else:
                ffmpeg_cmd.extend(['-map', '0:a'])
            
            # 設定 MP3 編碼器
            ffmpeg_cmd.extend(['-c:a', 'libmp3lame', '-q:a', '2'])
            
            # 設定輸出檔案
            suggested_output_path = os.path.splitext(self.video_path_input.text())[0] + '_processed.mp3'
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                '儲存處理後的音訊',
                suggested_output_path,
                'MP3 音訊檔案 (*.mp3);;所有檔案 (*.*)'
            )
            
            if not output_path:
                self.log('取消影片處理', 'debug')
                return
        else:
            # 準備 filter_complex 命令
            filter_complex = []
            video_filters = []
            audio_filters = []

            # 添加裁剪參數
            if crop_params:
                video_filters.append(f'crop={crop_params}')

            # 添加解析度參數
            if self.resolution_combo.currentText() != '原始':
                video_filters.append(f'scale={self.resolution_combo.currentText()}')

            # 處理浮水印
            if self.watermark_path_input.text().strip():
                ffmpeg_cmd.extend(['-i', self.watermark_path_input.text().strip()])
                video_filters.append('[0:v][1:v]overlay=10:10[outv]')
                ffmpeg_cmd.extend(['-map', '[outv]'])
            else:
                ffmpeg_cmd.extend(['-map', '0:v'])

            # 處理音訊
            if self.bgm_path_input.text():
                ffmpeg_cmd.extend(['-i', self.bgm_path_input.text().strip()])
                audio_filters.append('[0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]')
                ffmpeg_cmd.extend(['-map', '[aout]'])
            else:
                ffmpeg_cmd.extend(['-map', '0:a'])

            # 組合所有 filter_complex 命令
            if video_filters or audio_filters:
                filter_complex.extend(video_filters)
                filter_complex.extend(audio_filters)
                ffmpeg_cmd.extend(['-filter_complex', ';'.join(filter_complex)])

            # 設定編碼器
            if not video_filters and not audio_filters:
                ffmpeg_cmd.extend(['-c:v', 'copy', '-c:a', 'copy'])
            else:
                ffmpeg_cmd.extend(['-c:v', 'libx264', '-c:a', 'aac'])
            
            # 設定輸出檔案
            suggested_output_path = os.path.splitext(self.video_path_input.text())[0] + '_processed.mp4'
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                '儲存處理後的影片',
                suggested_output_path,
                'MP4 影片檔案 (*.mp4);;所有檔案 (*.*)'
            )
            
            if not output_path:
                self.log('取消影片處理', 'debug')
                return
        
        ffmpeg_cmd.append(output_path)

        # 執行 FFmpeg 命令
        threading.Thread(
            target=run_ffmpeg_command,
            args=(ffmpeg_cmd, self.log, lambda path: self.on_process_complete(path), self.on_process_error),
            daemon=True
        ).start()

    def validate_crop_params(self, crop_params):
        """驗證空間裁剪參數"""
        try:
            w, h, x, y = map(int, crop_params.split(':'))
            if w <= 0 or h <= 0 or x < 0 or y < 0:
                return False
            return True
        except:
            return False

    def escape_path(self, path):
        """轉義路徑中的特殊字符"""
        return path.replace("'", "'\\''")

    def cleanup_temp_files(self):
        """清理臨時文件"""
        try:
            if hasattr(self, 'temp_list_path') and os.path.exists(self.temp_list_path):
                os.remove(self.temp_list_path)
        except Exception as e:
            self.log(f'清理臨時文件失敗: {e}', 'error')

    def on_process_complete(self, output_path):
        """影片處理完成後的回調"""
        self.log('影片處理完成！', 'info')
        # 清理臨時文件
        self.cleanup_temp_files()
        # 發送處理完成事件到主執行緒
        QCoreApplication.instance().postEvent(
            self,
            FfmpegCompleteEvent(output_path)
        )

    def on_process_error(self, error_msg):
        """影片處理失敗後的回調"""
        self.log(f'影片處理失敗: {error_msg}', 'error')
        # 發送處理錯誤事件到主執行緒
        QCoreApplication.instance().postEvent(
            self,
            FfmpegErrorEvent(f'影片處理失敗：{error_msg}\n請檢查 FFmpeg 安裝和檔案是否正確。')
        )

    def browse_background_music(self):
        """選擇背景音樂檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            '選擇背景音樂檔案',
            '',
            '音訊檔案 (*.mp3 *.wav *.aac);;所有檔案 (*.*)'
        )
        if file_path:
            self.bgm_path_input.setText(file_path)
            self.log(f'已選擇背景音樂檔案: {file_path}', 'debug')

    def customEvent(self, event):
        """處理自定義事件"""
        if event.type() == FfmpegCompleteEvent.EVENT_TYPE:
            # FFmpeg 完成事件
            # 使用 QTimer.singleShot 延遲顯示訊息框
            QTimer.singleShot(100, lambda: self.show_complete_message(event.output_path))
            # 重新啟用轉換和處理按鈕
            if hasattr(self, 'convert_video_btn'):
                self.convert_video_btn.setEnabled(True)
            if hasattr(self, 'process_btn'):
                self.process_btn.setEnabled(True)
        elif event.type() == FfmpegErrorEvent.EVENT_TYPE:
            # 關閉字幕嵌入相關的對話框
            if hasattr(self, 'embed_progress_dialog') and self.embed_progress_dialog:
                self.embed_progress_dialog.close()
                self.embed_progress_dialog = None
            
            # 顯示錯誤訊息
            QTimer.singleShot(100, lambda: self.show_error_message(event.error_msg))
            
            # 重新啟用按鈕
            if hasattr(self, 'convert_video_btn'):
                self.convert_video_btn.setEnabled(True)
            if hasattr(self, 'process_btn'):
                self.process_btn.setEnabled(True)
            # FFmpeg 錯誤事件
            # 使用 QTimer.singleShot 延遲顯示錯誤訊息框
            QTimer.singleShot(100, lambda: self.show_error_message(event.error_msg))
            # 重新啟用轉換和處理按鈕
            if hasattr(self, 'convert_video_btn'):
                self.convert_video_btn.setEnabled(True)
            if hasattr(self, 'process_btn'):
                self.process_btn.setEnabled(True)
        elif event.type() == LoadConvertedVideoEvent.EVENT_TYPE:
            # 自動轉換完成，載入影片事件
            self.log(f'載入自動轉換後的影片: {event.file_path}', 'debug')
            if self.media_player:
                try:
                    # 停止當前播放
                    self.media_player.stop()
                    # 創建新的媒體對象
                    media = self.vlc_instance.media_new(event.file_path)
                    self.media_player.set_media(media)
                    # 設置視窗句柄
                    if sys.platform.startswith('win'):
                        self.media_player.set_hwnd(self.video_surface.winId())
                    elif sys.platform.startswith('linux'):
                        self.media_player.set_xid(self.video_surface.winId())
                    elif sys.platform.startswith('darwin'):
                        self.media_player.set_nsobject(int(self.video_surface.winId()))
                    
                    # 啟用播放控制元件
                    self.play_pause_btn.setEnabled(True)
                    self.progress_slider.setEnabled(True)
                    
                    # 開始播放
                    self.media_player.play()
                    self.play_pause_btn.setText('暫停')
                    
                    # 更新影片路徑輸入框 (使用臨時檔案路徑)
                    self.video_path_input.setText(event.file_path)

                    self.log(f'成功載入轉換後的影片: {event.file_path}', 'debug')
                    # 播放成功，啟用轉換影片按鈕
                    if hasattr(self, 'convert_video_btn'):
                        self.log('影片載入成功，啟用轉換影片按鈕', 'debug')
                        self.convert_video_btn.setEnabled(True)

                except Exception as e:
                    error_msg = f'載入轉換後的影片到 VLC 播放器失敗: {str(e)}\n\n建議：\n1. 確認影片格式是否支援\n2. 檢查 VLC 解碼器是否完整\n3. 嘗試使用其他影片檔案'
                    self.log(error_msg, 'error')
                    QMessageBox.critical(self, '播放錯誤', error_msg)
            else:
                # 如果 media_player 是 None，說明 VLC 未準備好，彈出警告框
                QMessageBox.warning(self, '錯誤', 'VLC 播放器未準備好，無法載入影片。\n請確認 VLC 核心檔案已正確放置。')
                self.log('VLC 播放器未準備好，無法載入影片。', 'error')
        elif event.type() == ScreenshotCompleteEvent.EVENT_TYPE:
            QMessageBox.information(self, '操作完成', f'截圖已成功儲存至：{event.output_path}')
            self.log(f'截圖已儲存至：{event.output_path}', 'info')
        elif event.type() == ScreenshotErrorEvent.EVENT_TYPE:
            QMessageBox.critical(self, '操作失敗', f'截圖失敗：{event.error_msg}')
            self.log(f'截圖失敗：{event.error_msg}', 'error')
        elif event.type() == AudioExtractCompleteEvent.EVENT_TYPE:
            QMessageBox.information(self, '操作完成', f'音訊已成功提取，檔案已儲存至：{event.output_path}')
            self.log(f'音訊已提取，檔案已儲存至：{event.output_path}', 'info')
        elif event.type() == AudioExtractErrorEvent.EVENT_TYPE:
            QMessageBox.critical(self, '操作失敗', f'提取音訊失敗：{event.error_msg}')
            self.log(f'提取音訊失敗：{event.error_msg}', 'error')
        else:
            super().customEvent(event)

    def show_complete_message(self, output_path):
        """顯示完成訊息"""
        QMessageBox.information(self, '操作完成', f'影片已成功處理並儲存至：{output_path}')

    def show_error_message(self, error_msg):
        """顯示錯誤訊息"""
        QMessageBox.critical(self, '操作失敗', error_msg)

    def set_start_time(self):
        """設定開始時間"""
        if self.media_player and self.media_player.is_playing():
            current_time = self.media_player.get_time() / 1000  # 轉換為秒
            self.trim_start.setText(self.format_time(current_time * 1000))
            self.log(f'設定開始時間: {self.trim_start.text()}', 'info')

    def set_end_time(self):
        """設定結束時間"""
        if self.media_player and self.media_player.is_playing():
            current_time = self.media_player.get_time() / 1000  # 轉換為秒
            self.trim_end.setText(self.format_time(current_time * 1000))
            self.log(f'設定結束時間: {self.trim_end.text()}', 'info')

    def toggle_time_input_mode(self):
        """切換時間輸入模式"""
        self.is_manual_time_input = not self.is_manual_time_input
        if self.is_manual_time_input:
            self.time_input_mode_btn.setText("切換為播放器選擇")
            self.trim_start.setReadOnly(False)
            self.trim_end.setReadOnly(False)
            self.set_start_time_btn.setEnabled(False)
            self.set_end_time_btn.setEnabled(False)
            self.log('已切換為手動輸入模式', 'info')
        else:
            self.time_input_mode_btn.setText("切換為手動輸入")
            self.trim_start.setReadOnly(True)
            self.trim_end.setReadOnly(True)
            self.set_start_time_btn.setEnabled(True)
            self.set_end_time_btn.setEnabled(True)
            self.log('已切換為播放器選擇模式', 'info')

    def extract_audio(self):
        """只保留聲音，移除影片"""
        input_path = self.video_path_input.text().strip()
        if not input_path or not os.path.exists(input_path):
            QMessageBox.warning(self, '錯誤', '請先選擇要處理的影片檔案！')
            return

        # 獲取輸出檔案路徑
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            '儲存音訊檔案',
            os.path.splitext(input_path)[0] + '.mp3',
            'MP3 音訊檔案 (*.mp3);;所有檔案 (*.*)'
        )
        if not output_path:
            return

        # 構建 FFmpeg 命令
        ffmpeg_cmd = [
            get_ffmpeg_path(),
            '-y',
            '-i', input_path,
            '-vn',  # 移除視訊流
            '-c:a', 'libmp3lame',  # 使用 MP3 編碼器
            '-q:a', '0',  # 最高音質
            output_path
        ]

        self.log(f'開始提取音訊...', 'info')
        self.log(f'執行命令: {" ".join(ffmpeg_cmd)}', 'debug')

        # 在新執行緒中執行處理
        threading.Thread(
            target=run_ffmpeg_command,
            args=(
                ffmpeg_cmd,
                self.log,
                lambda path: QApplication.postEvent(self, AudioExtractCompleteEvent(path)),
                lambda msg: QApplication.postEvent(self, AudioExtractErrorEvent(msg))
            ),
            daemon=True
        ).start()

    def take_screenshot(self):
        """擷取影片當前畫面的截圖"""
        if not self.media_player:
            QMessageBox.warning(self, '錯誤', '請先載入影片！')
            return

        # 先擷取到臨時檔案
        temp_dir = os.path.join(get_base_path(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f'screenshot_{int(time.time())}.png')

        try:
            # 使用 VLC 的內建截圖功能立即擷取當前畫面
            if self.media_player.video_take_snapshot(0, temp_path, 0, 0) != 0:
                error_msg = '截圖失敗'
                self.log(error_msg, 'error')
                QMessageBox.critical(self, '錯誤', error_msg)
                return

            # 讓用戶選擇儲存位置
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                '儲存截圖',
                os.path.join(self.download_folder, 'screenshot.png'),
                'PNG 圖片檔案 (*.png);;JPEG 圖片檔案 (*.jpg);;所有檔案 (*.*)'
            )

            if output_path:
                # 複製臨時檔案到用戶選擇的位置
                shutil.copy2(temp_path, output_path)
                self.log(f'截圖已儲存至: {output_path}', 'info')
                QMessageBox.information(self, '成功', f'截圖已儲存至:\n{output_path}')
            
            # 清理臨時檔案
            try:
                os.remove(temp_path)
            except:
                pass

        except Exception as e:
            error_msg = f'截圖時發生錯誤: {str(e)}'
            self.log(error_msg, 'error')
            QMessageBox.critical(self, '錯誤', error_msg)
            # 確保清理臨時檔案
            try:
                os.remove(temp_path)
            except:
                pass

    def run_ytdlp_command(self, cmd):
        """執行 yt-dlp 命令"""
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )

            # 讀取輸出
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log(output.strip(), 'info')

            # 檢查是否成功
            if process.returncode == 0:
                QMessageBox.information(self, '操作完成', '音訊下載完成！')
            else:
                error = process.stderr.read()
                QMessageBox.critical(self, '操作失敗', f'下載失敗：{error}')
                self.log(f'下載失敗：{error}', 'error')

        except Exception as e:
            QMessageBox.critical(self, '操作失敗', f'執行命令時發生錯誤：{str(e)}')
            self.log(f'執行命令時發生錯誤：{str(e)}', 'error')

    def on_format_changed(self, format_text):
        """當輸出格式改變時，更新相關控制項的狀態"""
        is_mp3 = format_text.lower() == 'mp3'
        
        # 禁用/啟用影片相關控制項
        self.resolution_combo.setEnabled(not is_mp3)
        self.crop_input.setEnabled(not is_mp3)
        self.watermark_path_input.setEnabled(not is_mp3)
        if hasattr(self, 'browse_watermark_btn'):
            self.browse_watermark_btn.setEnabled(not is_mp3)
        
        # 如果切換到 MP3 格式，清空影片相關設定
        if is_mp3:
            self.resolution_combo.setCurrentText('原始')
            self.crop_input.clear()
            self.watermark_path_input.clear()

    def toggle_titlebar(self):
        """切換標題列顯示/隱藏（無邊框模式）"""
        if self.hide_titlebar_action.isChecked():
            # 隱藏標題列（無邊框）
            self.setWindowFlag(Qt.FramelessWindowHint, True)
        else:
            # 顯示標題列
            self.setWindowFlag(Qt.FramelessWindowHint, False)
        self.show()  # 重新顯示視窗以套用變更

    def toggle_header(self):
        """切換 LOGO+標題區塊顯示/隱藏"""
        self.header.setVisible(not self.hide_header_action.isChecked())

    def toggle_optimize_space(self):
        """切換空間優化（同時隱藏LOGO+標題區塊和日誌區）"""
        hide = self.optimize_space_action.isChecked()
        self.header.setVisible(not hide)
        self.log_text.setVisible(not hide)

    def show_ai_subtitle_mode(self):
        """切換到 AI 字幕模式"""
        # 檢查是否在剪輯模式且有載入影片
        if not hasattr(self, 'current_video_path') or not self.current_video_path:
            # 如果不在剪輯模式，先切換到剪輯模式
            if not self.edit_mode_action.isChecked():
                self.edit_mode_action.setChecked(True)
                self.toggle_edit_mode()
            
            # 提示用戶選擇影片
            QMessageBox.information(self, '提示', '請先選擇要處理的影片')
            return
            
        # 顯示 AI 字幕設定
        self.show_ai_subtitle_dialog()

    def show_ai_subtitle_dialog(self):
        """顯示 AI 字幕設定對話框"""
        dialog = QDialog(self)
        dialog.setWindowTitle('AI 字幕設定')
        dialog.setMinimumWidth(400)
        
        # 設置黑色模式樣式
        dialog.setStyleSheet('''
            QDialog {
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
                font-size: 13px;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox:hover {
                border: 1px solid #4d4d4d;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border: 1px solid #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #4d4d4d;
            }
        ''')
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 模型大小選擇
        model_layout = QHBoxLayout()
        model_label = QLabel('模型大小:')
        model_combo = QComboBox()
        model_combo.addItems(['tiny', 'base', 'small', 'medium', 'large'])
        model_combo.setCurrentText('base')  # 預設使用 base 模型
        model_layout.addWidget(model_label)
        model_layout.addWidget(model_combo)
        layout.addLayout(model_layout)
        
        # 語言選擇
        lang_layout = QHBoxLayout()
        lang_label = QLabel('語言:')
        lang_combo = QComboBox()
        lang_combo.addItems(['zh', 'en', 'ja', 'ko'])
        lang_combo.setCurrentText('zh')  # 預設使用中文
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(lang_combo)
        layout.addLayout(lang_layout)
        
        # 按鈕
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            model_size = model_combo.currentText()
            language = lang_combo.currentText()
            self.generate_ai_subtitle(model_size, language)

    def generate_ai_subtitle(self, model_size: str, language: str):
        """生成 AI 字幕"""
        if not hasattr(self, 'current_video_path') or not self.current_video_path:
            QMessageBox.warning(self, '警告', '請先載入影片')
            return
            
        try:
            # 檢查模型是否存在
            model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
            if model_size == "base":
                model_name = "base.pt"
            else:
                model_name = f"ggml-{model_size}.bin"
            model_path = os.path.join(model_dir, model_name)
            
            if not os.path.exists(model_path):
                QMessageBox.warning(self, '警告', f'請先下載 {model_size} 模型到 models 資料夾')
                return
            
            # 建立輸出目錄
            output_dir = os.path.join(os.path.dirname(self.current_video_path), 'subtitles')
            os.makedirs(output_dir, exist_ok=True)
            
            # 設定輸出檔案路徑
            output_file = os.path.join(output_dir, 
                f"{os.path.splitext(os.path.basename(self.current_video_path))[0]}.srt")
            
            # 顯示進度對話框
            progress = QProgressDialog('正在生成字幕...', '取消', 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle('AI 字幕生成')
            progress.setMinimumDuration(0)
            progress.setAutoClose(False)
            progress.setAutoReset(False)
            
            # 設定進度對話框樣式
            progress.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QProgressDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                }
                QLabel {
                    color: #ffffff;
                    padding: 10px;
                    font-size: 12px;
                }
                QProgressBar {
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #1e1e1e;
                    height: 20px;
                    margin: 10px;
                }
                QProgressBar::chunk {
                    background-color: #0078d4;
                    border-radius: 3px;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                    margin: 5px;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
                QPushButton:pressed {
                    background-color: #2c2c2c;
                }
            """)
            
            progress.show()
            
            class TranscriptionWorker(QThread):
                finished = pyqtSignal(str)  # 成功時發送輸出檔案路徑
                error = pyqtSignal(str)     # 失敗時發送錯誤訊息
                
                def __init__(self, video_path, model_path, output_file, language):
                    super().__init__()
                    self.video_path = video_path
                    self.model_path = model_path
                    self.output_file = output_file
                    self.language = language
                    
                def run(self):
                    try:
                        import tempfile
                        import subprocess
                        import os
                        import whisper
                        from datetime import timedelta
                        import traceback
                        
                        def format_timestamp(seconds: float) -> str:
                            td = timedelta(seconds=seconds)
                            total_seconds = int(td.total_seconds())
                            hours = total_seconds // 3600
                            minutes = (total_seconds % 3600) // 60
                            secs = total_seconds % 60
                            milliseconds = int((seconds - int(seconds)) * 1000)
                            return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"
                        
                        # 檢查輸入檔案是否存在
                        if not os.path.exists(self.video_path):
                            raise Exception(f"找不到影片檔案：{self.video_path}")
                        
                        if not os.path.exists(self.model_path):
                            raise Exception(f"找不到模型檔案：{self.model_path}")
                        
                        # 確保輸出目錄存在
                        output_dir = os.path.dirname(self.output_file)
                        os.makedirs(output_dir, exist_ok=True)
                        
                        # 先用 ffmpeg 抽音訊
                        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
                            tmp_wav_path = tmp_wav.name
                        
                        # 使用 get_ffmpeg_path() 函數獲取 ffmpeg 路徑
                        ffmpeg_path = get_ffmpeg_path()
                        if not ffmpeg_path:
                            raise Exception("找不到 ffmpeg，請確保已正確安裝")
                        
                        # 檢查 ffmpeg 是否存在
                        if not os.path.exists(ffmpeg_path):
                            raise Exception(f"找不到 ffmpeg 執行檔：{ffmpeg_path}")
                        
                        # 設定環境變數，讓 whisper 也能找到 ffmpeg
                        ffmpeg_dir = os.path.dirname(ffmpeg_path)
                        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
                        
                        # 使用更穩定的 ffmpeg 命令
                        cmd = [
                            ffmpeg_path, "-y",
                            "-hwaccel", "auto",  # 自動選擇硬體加速
                            "-i", self.video_path,
                            "-vn",  # 不處理視訊
                            "-acodec", "pcm_s16le",  # 使用 PCM 編碼
                            "-ar", "16000",  # 16kHz 採樣率
                            "-ac", "1",  # 單聲道
                            "-f", "wav",  # 強制使用 WAV 格式
                            "-threads", "0",  # 自動選擇執行緒數
                            tmp_wav_path
                        ]
                        
                        # 使用 subprocess.Popen 替代 subprocess.run，以更好地控制執行緒
                        process = subprocess.Popen(
                            cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            universal_newlines=True,
                            encoding='utf-8',
                            errors='replace',
                            bufsize=1
                        )
                        
                        stdout, stderr = process.communicate()

                        if process.returncode != 0:
                            raise Exception(f"FFmpeg 執行失敗：{stderr}")
                        
                        # 檢查臨時檔案是否成功生成
                        if not os.path.exists(tmp_wav_path):
                            raise Exception("音訊檔案生成失敗")
                        
                        # 載入模型
                        try:
                            # 設定模型目錄
                            model_dir = os.path.dirname(self.model_path)
                            os.environ["WHISPER_MODEL_DIR"] = model_dir
                            
                            # 載入模型
                            model = whisper.load_model("base")
                        except Exception as e:
                            error_msg = f"載入模型失敗：{str(e)}\n{traceback.format_exc()}"
                            raise Exception(error_msg)
                        
                        # 執行轉錄
                        try:
                            result = model.transcribe(tmp_wav_path, language=self.language)
                        except Exception as e:
                            error_msg = f"轉錄失敗：{str(e)}\n{traceback.format_exc()}"
                            raise Exception(error_msg)
                        
                        # 寫入 SRT 檔案
                        try:
                            with open(self.output_file, "w", encoding="utf-8") as f:
                                for idx, segment in enumerate(result["segments"], start=1):
                                    start_ts = format_timestamp(segment["start"])
                                    end_ts = format_timestamp(segment["end"])
                                    text = segment["text"].strip()
                                    f.write(f"{idx}\n{start_ts} --> {end_ts}\n{text}\n\n")
                        except Exception as e:
                            error_msg = f"寫入字幕檔案失敗：{str(e)}\n{traceback.format_exc()}"
                            raise Exception(error_msg)
                        
                        self.finished.emit(self.output_file)
                    except Exception as e:
                        self.error.emit(str(e))
                    finally:
                        if 'tmp_wav_path' in locals() and os.path.exists(tmp_wav_path):
                            try:
                                os.remove(tmp_wav_path)
                            except:
                                pass
                        
            # 創建並啟動工作執行緒
            self.transcription_worker = TranscriptionWorker(
                self.current_video_path,
                model_path,
                output_file,
                language
            )
            
            # 連接信號
            self.transcription_worker.finished.connect(
                lambda path: self.on_transcription_complete(path, progress)
            )
            self.transcription_worker.error.connect(
                lambda msg: self.on_transcription_error(msg, progress)
            )
            
            # 啟動執行緒
            self.transcription_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, '錯誤', f'生成字幕時發生錯誤：{str(e)}')

    def on_transcription_complete(self, output_file, progress):
        """字幕生成完成的處理"""
        progress.close()
        
        try:
            # 讀取SRT檔案內容
            with open(output_file, 'r', encoding='utf-8') as f:
                srt_content = f.read()
            
            # 創建編輯對話框
            dialog = QDialog(self)
            dialog.setWindowTitle('編輯字幕')
            dialog.setMinimumSize(800, 600)
            
            # 設定對話框樣式
            dialog.setStyleSheet("""
                QDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    padding: 5px;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
                QPushButton:pressed {
                    background-color: #2c2c2c;
                }
            """)
            
            # 創建編輯區域
            layout = QVBoxLayout()
            text_edit = QTextEdit()
            text_edit.setPlainText(srt_content)
            layout.addWidget(text_edit)
            
            # 字體和大小選擇
            font_layout = QHBoxLayout()
            font_label = QLabel("字體:")
            font_combo = QFontComboBox()
            try:
                # 嘗試設定一個常見的中文字體作為預設
                default_font = QFont("Microsoft JhengHei")
                if default_font.family() in [f.family() for f in QFontDatabase().families()]:
                    font_combo.setCurrentFont(default_font)
                else:
                    font_combo.setCurrentFont(QFont("Arial")) # 後備字體
            except:
                pass # 如果出錯，使用預設字體

            size_label = QLabel("大小:")
            size_spinbox = QSpinBox()
            size_spinbox.setRange(1, 128)
            size_spinbox.setValue(24)
            font_layout.addWidget(font_label)
            font_layout.addWidget(font_combo, 1)
            font_layout.addWidget(size_label)
            font_layout.addWidget(size_spinbox)
            font_layout.addStretch()
            layout.addLayout(font_layout)

            # 創建按鈕區域
            button_layout = QHBoxLayout()
            save_button = QPushButton('完成')
            cancel_button = QPushButton('取消')
            
            button_layout.addWidget(save_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            # 連接按鈕事件
            def save_changes():
                try:
                    # 創建進度對話框
                    progress = QProgressDialog('正在嵌入字幕...', None, 0, 0, self)
                    progress.setWindowModality(Qt.WindowModal)
                    progress.setWindowTitle('處理中')
                    progress.setStyleSheet("""
                        QProgressDialog {
                            background-color: #2b2b2b;
                            color: #ffffff;
                        }
                        QLabel {
                            color: #ffffff;
                            padding: 10px;
                        }
                    """)
                    progress.show()

                    # 生成臨時字幕檔案
                    temp_srt = os.path.join(os.path.dirname(output_file), "temp_subtitle.srt")
                    with open(temp_srt, 'w', encoding='utf-8') as f:
                        f.write(text_edit.toPlainText())

                    # 獲取影片檔案路徑
                    video_path = self.current_video_path
                    output_video = os.path.join(
                        os.path.dirname(video_path),
                        os.path.splitext(os.path.basename(video_path))[0] + "_subbed" + os.path.splitext(video_path)[1]
                    )

                    # 確保 subtitles 資料夾存在
                    subtitles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'subtitles')
                    os.makedirs(subtitles_dir, exist_ok=True)

                    # 生成臨時字幕檔案路徑
                    temp_srt = os.path.join(subtitles_dir, 'temp_subtitle.srt')
                    
                    # 保存字幕內容到檔案
                    with open(temp_srt, 'w', encoding='utf-8') as f:
                        f.write(text_edit.toPlainText())

                    # 使用 ffmpeg 嵌入字幕
                    ffmpeg_path = get_ffmpeg_path()
                    if not ffmpeg_path:
                        raise Exception("找不到 ffmpeg，請確保已正確安裝")

                    # 處理路徑中的特殊字符
                    def escape_path(path):
                        # 將路徑轉換為絕對路徑
                        abs_path = os.path.abspath(path)
                        # 使用正斜線替換反斜線
                        normalized_path = abs_path.replace('\\', '/')
                        # 對路徑進行 URL 編碼，但保留斜線
                        parts = normalized_path.split('/')
                        encoded_parts = [urllib.parse.quote(part) for part in parts]
                        return '/'.join(encoded_parts)

                    # 確保字幕目錄存在
                    os.makedirs('subtitles', exist_ok=True)
                    
                    # 生成臨時字幕檔案路徑
                    temp_srt = os.path.join('subtitles', 'temp_subtitle.srt')
                    
                    # 檢查字幕內容
                    try:
                        with open(temp_srt, 'r', encoding='utf-8') as f:
                            subtitle_content = f.read()
                            self.log(f"字幕檔案內容：\n{subtitle_content[:500]}...", level='debug')
                            
                            # 檢查字幕格式
                            if not subtitle_content.strip():
                                raise Exception("字幕檔案為空")
                            
                            # 檢查字幕編碼
                            if not subtitle_content.encode('utf-8').decode('utf-8'):
                                raise Exception("字幕檔案編碼可能有問題")
                    except Exception as e:
                        self.log(f"字幕檔案檢查失敗：{str(e)}", level='error')
                        raise

                    # 使用 ffprobe 獲取影片尺寸
                    ffprobe_path = os.path.join(os.path.dirname(ffmpeg_path), 'ffprobe.exe')
                    probe_cmd = f'"{ffprobe_path}" -v error -select_streams v:0 -show_entries stream=width,height -of json "{escape_path(video_path)}"'
                    
                    try:
                        probe_result = subprocess.run(probe_cmd, shell=True, capture_output=True, text=True)
                        video_info = json.loads(probe_result.stdout)
                        width = video_info['streams'][0]['width']
                        height = video_info['streams'][0]['height']
                        video_size = f"{width}x{height}"
                        self.log(f"影片尺寸：{video_size}", level='debug')
                    except Exception as e:
                        self.log(f"無法獲取影片尺寸：{str(e)}", level='error')
                        video_size = "1080x1920"  # 預設尺寸

                    # 獲取選擇的字體和大小
                    font_name = font_combo.currentFont().family()
                    font_size = size_spinbox.value()

                    # 準備 ffmpeg 字幕濾鏡參數。
                    # 1. 將路徑中的反斜線替換為正斜線，這是 ffmpeg 更偏好的格式。
                    escaped_srt_path = temp_srt.replace(os.sep, '/')
                    # 2. 構建 filter 字串。force_style 的值用單引號包起來，以處理字體名稱中的空格。
                    vf_filter = f"subtitles={escaped_srt_path}:force_style='FontName={font_name},FontSize={font_size}'"

                    # 使用更穩定的編碼設定
                    cmd = [
                        ffmpeg_path, '-y', '-i', video_path, '-vf', vf_filter,
                        '-c:v', 'libx264', '-preset', 'medium', '-crf', '23', '-c:a', 'copy', output_video
                    ]

                    # 執行 ffmpeg 命令並即時顯示輸出
                    process = subprocess.Popen(
                        cmd, # 移除 shell=True 以提高安全性並避免轉義問題
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        encoding='utf-8',
                        errors='replace',
                        bufsize=1,
                        universal_newlines=True
                    )
                    # 即時讀取輸出
                    error_output = []
                    while True:
                        output = process.stderr.readline()
                        if output == '' and process.poll() is not None:
                            break
                        if output:
                            error_output.append(output.strip())
                            self.log(f"FFmpeg: {output.strip()}", level='debug')

                    # 等待進程完成
                    return_code = process.wait()

                    if return_code != 0:
                        error_message = '\n'.join(error_output)
                        self.log(f"FFmpeg 執行失敗，錯誤代碼: {return_code}", level='error')
                        self.log(f"錯誤詳情:\n{error_message}", level='error')
                        
                        # 檢查字幕檔案是否存在
                        if not os.path.exists(temp_srt):
                            raise Exception(f"字幕檔案不存在: {temp_srt}")
                        
                        # 檢查字幕檔案內容
                        try:
                            with open(temp_srt, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if not content.strip():
                                    raise Exception("字幕檔案為空")
                        except Exception as e:
                            raise Exception(f"無法讀取字幕檔案: {str(e)}")
                        
                        raise Exception(f"FFmpeg 處理失敗: {error_message}")

                    # 檢查輸出檔案是否存在
                    if not os.path.exists(output_video):
                        raise Exception("輸出檔案未生成")

                    # 檢查輸出檔案大小
                    if os.path.getsize(output_video) == 0:
                        raise Exception("輸出檔案大小為 0")

                    self.log("影片處理完成", level='info')

                    # 清理臨時檔案
                    try:
                        os.remove(temp_srt)
                    except:
                        pass

                    progress.close()
                    QMessageBox.information(
                        self,
                        '完成',
                        f'字幕已成功嵌入到新影片：\n{output_video}'
                    )
                    dialog.accept()

                except Exception as e:
                    progress.close()
                    QMessageBox.critical(self, '錯誤', f'嵌入字幕時發生錯誤：{str(e)}')
            
            save_button.clicked.connect(save_changes)
            cancel_button.clicked.connect(dialog.reject)
            
            # 顯示對話框
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, '錯誤', f'讀取字幕時發生錯誤：{str(e)}')

    def on_transcription_error(self, error_msg, progress):
        """字幕生成錯誤的處理"""
        progress.close()
        QMessageBox.critical(self, '錯誤', f'生成字幕時發生錯誤：{error_msg}')

class LoadConvertedVideoEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())
    def __init__(self, file_path):
        super().__init__(self.EVENT_TYPE)
        self.file_path = file_path

class DownloadThread(QThread):
    finished = pyqtSignal(bool, str)  # 成功/失敗, 訊息
    
    def __init__(self, model_size):
        super().__init__()
        self.model_size = model_size
    
    def run(self):
        try:
            import whisper
            import os
            import requests
            from tqdm import tqdm
            
            # 建立模型目錄
            model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
            os.makedirs(model_dir, exist_ok=True)
            
            # 模型檔案名稱
            model_name = f"ggml-{self.model_size}.bin"
            model_path = os.path.join(model_dir, model_name)
            
            # 如果模型已存在，直接返回
            if os.path.exists(model_path):
                self.finished.emit(True, f'模型 {self.model_size} 已存在！')
                return
            
            # 下載模型
            url = f"https://huggingface.co/ggerganov/whisper.cpp/resolve/main/{model_name}"
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with open(model_path, 'wb') as f, tqdm(
                desc=f"下載 {model_name}",
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
            ) as pbar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    pbar.update(size)
            
            self.finished.emit(True, f'模型 {self.model_size} 下載完成！')
        except Exception as e:
            self.finished.emit(False, f'下載模型時發生錯誤：{str(e)}')

    def generate_ai_subtitle(self, model_size: str, language: str):
        """生成 AI 字幕"""
        if not hasattr(self, 'current_video_path') or not self.current_video_path:
            QMessageBox.warning(self, '警告', '請先載入影片')
            return
            
        try:
            # 檢查模型是否存在
            model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
            model_name = f"ggml-{model_size}.bin"
            model_path = os.path.join(model_dir, model_name)
            
            if not os.path.exists(model_path):
                QMessageBox.warning(self, '警告', f'請先下載 {model_size} 模型')
                return
            
            # 建立輸出目錄
            output_dir = os.path.join(os.path.dirname(self.current_video_path), 'subtitles')
            os.makedirs(output_dir, exist_ok=True)
            
            # 設定輸出檔案路徑
            output_file = os.path.join(output_dir, 
                f"{os.path.splitext(os.path.basename(self.current_video_path))[0]}.srt")
            
            # 顯示進度對話框
            progress = QProgressDialog('正在生成字幕...', '取消', 0, 0, self)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle('AI 字幕生成')
            
            # 設定進度對話框樣式
            progress.setStyleSheet("""
                QProgressDialog {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QProgressBar {
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #1e1e1e;
                }
                QProgressBar::chunk {
                    background-color: #4c4c4c;
                    border-radius: 3px;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #4c4c4c;
                }
                QPushButton:pressed {
                    background-color: #2c2c2c;
                }
            """)
            
            progress.show()
            
            # 在新執行緒中執行字幕生成
            def run_transcription():
                try:
                    from ai import transcribe_to_srt
                    transcribe_to_srt(self.current_video_path, output_file, model_size, language)
                    QMetaObject.invokeMethod(progress, "close", Qt.QueuedConnection)
                    QMessageBox.information(self, '完成', f'字幕已生成：{output_file}')
                except Exception as e:
                    QMetaObject.invokeMethod(progress, "close", Qt.QueuedConnection)
                    QMessageBox.critical(self, '錯誤', f'生成字幕時發生錯誤：{str(e)}')
            
            thread = QThread()
            thread.run = run_transcription
            thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, '錯誤', f'生成字幕時發生錯誤：{str(e)}')

    def on_video_surface_resize(self, event):
        """處理影片播放區域大小變化事件"""
        if self.media_player and self.media_player.get_media():
            # 重新設置VLC視窗句柄以適應新的尺寸
            try:
                if sys.platform.startswith('win'):
                    self.media_player.set_hwnd(self.video_surface.winId())
                elif sys.platform.startswith('linux'):
                    self.media_player.set_xid(self.video_surface.winId())
                elif sys.platform.startswith('darwin'):
                    self.media_player.set_nsobject(int(self.video_surface.winId()))
                
                # 調整影片寬高比
                self.adjust_video_aspect_ratio()
                
                self.log(f'影片播放區域大小已調整為: {event.size().width()}x{event.size().height()}', 'debug')
            except Exception as e:
                self.log(f'調整影片播放區域大小時發生錯誤: {str(e)}', 'error')
        event.accept()

    def on_main_window_resize(self, event):
        """處理主視窗大小變化事件"""
        self.log(f'主視窗大小已調整為: {event.size().width()}x{event.size().height()}', 'debug')

    def adjust_video_aspect_ratio(self):
        """調整影片播放區域的寬高比"""
        if not self.media_player or not self.media_player.get_media():
            return
            
        try:
            # 獲取影片的原始尺寸
            media = self.media_player.get_media()
            if media:
                # 嘗試獲取影片的寬高比
                # 注意：VLC Python綁定可能不直接提供這個信息
                # 我們可以通過設置VLC的aspect ratio選項來處理
                
                # 設置VLC的寬高比為自動，讓它根據視窗大小自動調整
                self.media_player.video_set_aspect_ratio(None)  # None表示自動
                self.log('影片寬高比已設置為自動調整', 'debug')
        except Exception as e:
            self.log(f'調整影片寬高比時發生錯誤: {str(e)}', 'error')

    def resizeEvent(self, event):
        """處理主視窗大小變化事件"""
        self.log(f'主視窗大小已調整為: {event.size().width()}x{event.size().height()}', 'debug')
        # 調用父類的 resizeEvent 方法
        super().resizeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = YTDLPDownloader()
    window.show()
    sys.exit(app.exec_())