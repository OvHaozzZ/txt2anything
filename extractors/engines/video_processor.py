"""
视频处理器模块
使用 ffmpeg 进行视频帧提取和音频提取
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import subprocess
import tempfile
import os
import re


class VideoProcessor:
    """视频处理工具"""

    def __init__(self, ffmpeg_path: str = 'ffmpeg'):
        """
        初始化视频处理器

        参数:
            ffmpeg_path: ffmpeg 可执行文件路径
        """
        self._ffmpeg = ffmpeg_path
        self._ffprobe = ffmpeg_path.replace('ffmpeg', 'ffprobe')

    def check_ffmpeg(self) -> bool:
        """检查 ffmpeg 是否可用"""
        try:
            subprocess.run(
                [self._ffmpeg, '-version'],
                capture_output=True,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _ensure_ffmpeg(self):
        """确保 ffmpeg 可用"""
        if not self.check_ffmpeg():
            raise RuntimeError(
                "ffmpeg 未找到。请安装 ffmpeg 并确保其在 PATH 中。\n"
                "Windows: https://ffmpeg.org/download.html\n"
                "或使用: choco install ffmpeg / winget install ffmpeg"
            )

    def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        获取视频信息

        参数:
            video_path: 视频文件路径

        返回:
            视频信息字典，包含 duration, width, height 等
        """
        self._ensure_ffmpeg()

        cmd = [
            self._ffmpeg, '-i', video_path,
            '-hide_banner'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)

        info = {
            'path': video_path,
            'duration': self._parse_duration(result.stderr),
            'has_audio': 'Audio:' in result.stderr
        }

        # 解析分辨率
        resolution_match = re.search(r'(\d{2,5})x(\d{2,5})', result.stderr)
        if resolution_match:
            info['width'] = int(resolution_match.group(1))
            info['height'] = int(resolution_match.group(2))

        return info

    def _parse_duration(self, ffmpeg_output: str) -> float:
        """从 ffmpeg 输出解析时长"""
        match = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})', ffmpeg_output)
        if match:
            h, m, s, ms = map(int, match.groups())
            return h * 3600 + m * 60 + s + ms / 100
        return 0.0

    def extract_frames(
        self,
        video_path: str,
        output_dir: Optional[str] = None,
        interval: float = 5.0,
        max_frames: int = 50
    ) -> List[Dict[str, Any]]:
        """
        按固定间隔提取视频帧

        参数:
            video_path: 视频文件路径
            output_dir: 输出目录（如果不提供则使用临时目录）
            interval: 帧间隔（秒）
            max_frames: 最大帧数

        返回:
            帧信息列表，每项包含:
            - path: 帧图片路径
            - timestamp: 时间戳（秒）
        """
        self._ensure_ffmpeg()

        # 创建输出目录
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix='txt2xmind_frames_')
        else:
            os.makedirs(output_dir, exist_ok=True)

        # 获取视频时长
        info = self.get_video_info(video_path)
        duration = info['duration']

        if duration <= 0:
            return []

        # 计算实际帧数
        num_frames = min(int(duration / interval) + 1, max_frames)

        frames = []
        for i in range(num_frames):
            timestamp = i * interval
            if timestamp > duration:
                break

            output_path = os.path.join(output_dir, f'frame_{i:04d}.jpg')

            cmd = [
                self._ffmpeg,
                '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '2',
                '-y',
                output_path
            ]

            try:
                subprocess.run(cmd, capture_output=True, check=True)
                if os.path.exists(output_path):
                    frames.append({
                        'path': output_path,
                        'timestamp': timestamp
                    })
            except subprocess.CalledProcessError:
                continue

        return frames

    def extract_audio(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        sample_rate: int = 16000
    ) -> str:
        """
        从视频中提取音频

        参数:
            video_path: 视频文件路径
            output_path: 输出音频路径（如果不提供则使用临时文件）
            sample_rate: 采样率（默认 16000，适合语音识别）

        返回:
            音频文件路径
        """
        self._ensure_ffmpeg()

        if output_path is None:
            fd, output_path = tempfile.mkstemp(suffix='.wav', prefix='txt2xmind_audio_')
            os.close(fd)

        cmd = [
            self._ffmpeg,
            '-i', video_path,
            '-vn',  # 不处理视频
            '-acodec', 'pcm_s16le',  # PCM 16-bit
            '-ar', str(sample_rate),  # 采样率
            '-ac', '1',  # 单声道
            '-y',
            output_path
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return output_path
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"音频提取失败: {e.stderr.decode() if e.stderr else str(e)}")

    def cleanup_frames(self, frames: List[Dict[str, Any]]):
        """
        清理提取的帧文件

        参数:
            frames: extract_frames 返回的帧列表
        """
        for frame in frames:
            path = frame.get('path')
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass

        # 尝试删除目录
        if frames:
            frame_dir = os.path.dirname(frames[0].get('path', ''))
            if frame_dir and os.path.exists(frame_dir):
                try:
                    os.rmdir(frame_dir)
                except OSError:
                    pass
