"""
Tests for extractors module - 多模态内容提取器测试
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestExtractorManager:
    """Test ExtractorManager class"""

    def test_manager_initialization(self):
        """Test manager initializes with default extractors"""
        from extractors import ExtractorManager
        manager = ExtractorManager()

        extractors = manager.list_extractors()
        assert len(extractors) >= 2  # image and video

        names = [e['name'] for e in extractors]
        assert 'image' in names
        assert 'video' in names

    def test_list_supported_formats(self):
        """Test listing supported formats"""
        from extractors import ExtractorManager
        manager = ExtractorManager()

        formats = manager.list_supported_formats()

        assert 'image' in formats
        assert 'video' in formats
        assert '.jpg' in formats['image']
        assert '.mp4' in formats['video']

    def test_is_supported(self):
        """Test file support checking"""
        from extractors import ExtractorManager
        manager = ExtractorManager()

        # Supported formats
        assert manager.is_supported('test.jpg') is True
        assert manager.is_supported('test.png') is True
        assert manager.is_supported('test.mp4') is True
        assert manager.is_supported('test.avi') is True

        # Unsupported formats
        assert manager.is_supported('test.txt') is False
        assert manager.is_supported('test.pdf') is False
        assert manager.is_supported('test.doc') is False

    def test_get_extractor_for_file(self):
        """Test getting extractor by file type"""
        from extractors import ExtractorManager, ImageExtractor, VideoExtractor
        manager = ExtractorManager()

        img_extractor = manager.get_extractor_for_file('photo.jpg')
        assert isinstance(img_extractor, ImageExtractor)

        vid_extractor = manager.get_extractor_for_file('video.mp4')
        assert isinstance(vid_extractor, VideoExtractor)

        none_extractor = manager.get_extractor_for_file('doc.txt')
        assert none_extractor is None

    def test_extract_unsupported_file_raises_error(self):
        """Test extracting unsupported file raises ValueError"""
        from extractors import ExtractorManager
        manager = ExtractorManager()

        with pytest.raises(ValueError) as exc_info:
            manager.extract('test.xyz')

        assert '不支持的文件类型' in str(exc_info.value)


class TestImageExtractor:
    """Test ImageExtractor class"""

    def test_supported_formats(self):
        """Test image extractor supported formats"""
        from extractors import ImageExtractor
        extractor = ImageExtractor()

        formats = extractor.supported_formats
        assert '.jpg' in formats
        assert '.jpeg' in formats
        assert '.png' in formats
        assert '.bmp' in formats
        assert '.webp' in formats

    def test_supports_method(self):
        """Test supports method"""
        from extractors import ImageExtractor
        extractor = ImageExtractor()

        assert extractor.supports('image.jpg') is True
        assert extractor.supports('image.PNG') is True  # case insensitive
        assert extractor.supports('video.mp4') is False


class TestVideoExtractor:
    """Test VideoExtractor class"""

    def test_supported_formats(self):
        """Test video extractor supported formats"""
        from extractors import VideoExtractor
        extractor = VideoExtractor()

        formats = extractor.supported_formats
        assert '.mp4' in formats
        assert '.avi' in formats
        assert '.mov' in formats
        assert '.mkv' in formats
        assert '.webm' in formats

    def test_supports_method(self):
        """Test supports method"""
        from extractors import VideoExtractor
        extractor = VideoExtractor()

        assert extractor.supports('video.mp4') is True
        assert extractor.supports('video.AVI') is True  # case insensitive
        assert extractor.supports('image.jpg') is False


class TestOCREngine:
    """Test OCREngine class"""

    def test_is_available_without_dependency(self):
        """Test is_available returns False when rapidocr not installed"""
        from extractors.engines.ocr_engine import OCREngine

        engine = OCREngine()
        # This will depend on whether rapidocr is installed
        # Just test that the method exists and returns a boolean
        result = engine.is_available()
        assert isinstance(result, bool)


class TestSpeechEngine:
    """Test SpeechEngine class"""

    def test_list_models(self):
        """Test listing available models"""
        from extractors.engines.speech_engine import SpeechEngine

        engine = SpeechEngine()
        models = engine.list_models()

        assert 'tiny' in models
        assert 'base' in models
        assert 'small' in models
        assert 'medium' in models

    def test_is_available_without_dependency(self):
        """Test is_available returns False when faster-whisper not installed"""
        from extractors.engines.speech_engine import SpeechEngine

        engine = SpeechEngine()
        result = engine.is_available()
        assert isinstance(result, bool)


class TestVideoProcessor:
    """Test VideoProcessor class"""

    def test_check_ffmpeg(self):
        """Test ffmpeg availability check"""
        from extractors.engines.video_processor import VideoProcessor

        processor = VideoProcessor()
        result = processor.check_ffmpeg()
        # Returns True if ffmpeg is installed, False otherwise
        assert isinstance(result, bool)


class TestGlobalExtractorManager:
    """Test global extractor manager singleton"""

    def test_get_extractor_manager_singleton(self):
        """Test get_extractor_manager returns same instance"""
        from extractors import get_extractor_manager

        manager1 = get_extractor_manager()
        manager2 = get_extractor_manager()

        assert manager1 is manager2
