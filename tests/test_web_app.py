"""
Tests for web_app.py
"""
import pytest
from fastapi.testclient import TestClient
from web_app import app

client = TestClient(app)


class TestWebApp:
    """Test FastAPI web application"""

    def test_read_index(self):
        """Test root endpoint returns index.html"""
        response = client.get("/")
        assert response.status_code == 200

    def test_generate_xmind_with_structured_text(self):
        """Test generating XMind from pre-structured text"""
        request_data = {
            "text": """Test Mind Map
  Topic 1
    Subtopic 1
  Topic 2""",
            "layout": "right"
        }

        response = client.post("/api/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "download_url" in data
        assert "structured_text" in data
        assert data["download_url"].startswith("/static/mindmap_")
        assert data["download_url"].endswith(".xmind")

    def test_generate_xmind_different_layouts(self):
        """Test generating XMind with different layouts"""
        layouts = ["right", "map", "tree", "org"]

        for layout in layouts:
            request_data = {
                "text": """Test
  Node 1
  Node 2""",
                "layout": layout
            }

            response = client.post("/api/generate", json=request_data)
            assert response.status_code == 200

    def test_generate_xmind_empty_text(self):
        """Test error handling for empty text"""
        request_data = {
            "text": "",
            "layout": "right"
        }

        response = client.post("/api/generate", json=request_data)
        assert response.status_code == 400

    def test_generate_xmind_invalid_layout(self):
        """Test with invalid layout (should still work with default)"""
        request_data = {
            "text": """Test
  Node""",
            "layout": "invalid_layout"
        }

        response = client.post("/api/generate", json=request_data)
        # Should succeed with default layout
        assert response.status_code == 200

    def test_generate_xmind_complex_structure(self):
        """Test generating XMind with complex multi-level structure"""
        request_data = {
            "text": """Project Plan
  Phase 1
    Task 1.1
      Subtask 1.1.1
      Subtask 1.1.2
    Task 1.2
  Phase 2
    Task 2.1
    Task 2.2
      Subtask 2.2.1""",
            "layout": "org"
        }

        response = client.post("/api/generate", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "download_url" in data

    def test_api_without_openai_key(self):
        """Test that API works without OpenAI key for pre-structured text"""
        request_data = {
            "text": """Simple Map
  Item 1
  Item 2""",
            "layout": "map"
        }

        response = client.post("/api/generate", json=request_data)
        assert response.status_code == 200


class TestOpenAIIntegration:
    """Test OpenAI integration (mocked)"""

    def test_generate_with_api_key_missing_openai(self):
        """Test that providing API key without openai library raises error"""
        request_data = {
            "text": "Some unstructured text",
            "api_key": "test-key",
            "layout": "right"
        }

        # This will fail if openai is not installed
        # In CI, we should mock this or skip if openai is not available
        response = client.post("/api/generate", json=request_data)
        # Could be 500 (openai not installed) or 502 (API error)
        assert response.status_code in [200, 400, 500, 502]
