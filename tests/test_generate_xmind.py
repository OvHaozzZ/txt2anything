"""
Tests for generate_xmind.py
"""
import os
import json
import zipfile
import pytest
from core.parser import parse_text
from formatters.xmind import XMindFormatter


class TestParseText:
    """Test parse_text function"""

    def test_parse_simple_structure(self):
        """Test parsing a simple two-level structure"""
        content = """Root Node
  Child 1
  Child 2"""

        title, structure = parse_text(content=content)

        assert title == "Root Node"
        assert len(structure) == 2
        assert structure[0]["text"] == "Child 1"
        assert structure[1]["text"] == "Child 2"

    def test_parse_multi_level_structure(self):
        """Test parsing a multi-level structure"""
        content = """Main Topic
  Level 1 - A
    Level 2 - A1
    Level 2 - A2
  Level 1 - B
    Level 2 - B1"""

        title, structure = parse_text(content=content)

        assert title == "Main Topic"
        assert len(structure) == 2
        assert structure[0]["text"] == "Level 1 - A"
        assert len(structure[0]["children"]) == 2
        assert structure[0]["children"][0]["text"] == "Level 2 - A1"
        assert structure[1]["text"] == "Level 1 - B"
        assert len(structure[1]["children"]) == 1

    def test_parse_deep_nesting(self):
        """Test parsing deeply nested structure"""
        content = """Root
  L1
    L2
      L3
        L4"""

        title, structure = parse_text(content=content)

        assert title == "Root"
        assert structure[0]["text"] == "L1"
        assert structure[0]["children"][0]["text"] == "L2"
        assert structure[0]["children"][0]["children"][0]["text"] == "L3"
        assert structure[0]["children"][0]["children"][0]["children"][0]["text"] == "L4"

    def test_parse_empty_content(self):
        """Test parsing empty content"""
        with pytest.raises(ValueError):
            parse_text(content="")

    def test_parse_with_tabs(self):
        """Test parsing with tab indentation"""
        content = "Root\n\tChild 1\n\tChild 2"

        title, structure = parse_text(content=content)

        assert title == "Root"
        assert len(structure) == 2
        assert structure[0]["text"] == "Child 1"

    def test_parse_mixed_indentation(self):
        """Test parsing with mixed spaces and tabs"""
        content = "Root\n  Child 1\n\tChild 2"

        title, structure = parse_text(content=content)

        assert title == "Root"
        assert len(structure) == 2


class TestXMindFormatter:
    """Test XMindFormatter class"""

    def test_format_simple_content(self):
        """Test formatting simple XMind content"""
        formatter = XMindFormatter()
        tree_nodes = [
            {"text": "Node 1", "children": []},
            {"text": "Node 2", "children": []}
        ]

        content = formatter.format("Test Title", tree_nodes)

        assert "content" in content
        assert len(content["content"]) == 1
        assert content["content"][0]["title"] == "画布 1"
        assert content["content"][0]["rootTopic"]["title"] == "Test Title"
        assert len(content["content"][0]["rootTopic"]["children"]["attached"]) == 2

    def test_format_nested_content(self):
        """Test formatting nested XMind content"""
        formatter = XMindFormatter()
        tree_nodes = [
            {
                "text": "Parent",
                "children": [
                    {"text": "Child", "children": []}
                ]
            }
        ]

        content = formatter.format("Test", tree_nodes)

        root_topic = content["content"][0]["rootTopic"]
        assert root_topic["children"]["attached"][0]["title"] == "Parent"
        assert root_topic["children"]["attached"][0]["children"]["attached"][0]["title"] == "Child"

    def test_different_layouts(self):
        """Test different layout options"""
        formatter = XMindFormatter()
        tree_nodes = [{"text": "Node", "children": []}]

        layouts = {
            "right": "org.xmind.ui.logic.right",
            "map": "org.xmind.ui.map.unbalanced",
            "tree": "org.xmind.ui.tree.right",
            "org": "org.xmind.ui.org.down"
        }

        for layout_key, expected_class in layouts.items():
            content = formatter.format("Test", tree_nodes, layout=layout_key)
            assert content["content"][0]["rootTopic"]["structureClass"] == expected_class

    def test_save_xmind_file(self, tmp_path):
        """Test saving XMind file"""
        formatter = XMindFormatter()
        filename = tmp_path / "test.xmind"
        title = "Test Mind Map"
        structure = [
            {"text": "Node 1", "children": []},
            {"text": "Node 2", "children": []}
        ]

        formatter.export(title, structure, str(filename))

        # Verify file exists
        assert filename.exists()

        # Verify it's a valid ZIP file
        assert zipfile.is_zipfile(filename)

        # Verify contents
        with zipfile.ZipFile(filename, 'r') as zipf:
            files = zipf.namelist()
            assert "content.json" in files
            assert "metadata.json" in files
            assert "manifest.json" in files

            # Verify content.json structure
            content_data = json.loads(zipf.read("content.json"))
            assert len(content_data) == 1
            assert content_data[0]["rootTopic"]["title"] == title

    def test_save_with_different_layouts(self, tmp_path):
        """Test saving with different layouts"""
        formatter = XMindFormatter()
        structure = [{"text": "Node", "children": []}]

        for layout in ["right", "map", "tree", "org"]:
            filename = tmp_path / f"test_{layout}.xmind"
            formatter.export("Test", structure, str(filename), layout=layout)
            assert filename.exists()
