"""
Tests for generate_xmind.py
"""
import os
import json
import zipfile
import pytest
from generate_xmind import parse_txt_file, create_xmind_content, save_xmind


class TestParseTxtFile:
    """Test parse_txt_file function"""

    def test_parse_simple_structure(self):
        """Test parsing a simple two-level structure"""
        content = """Root Node
  Child 1
  Child 2"""

        title, structure = parse_txt_file(content=content)

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

        title, structure = parse_txt_file(content=content)

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

        title, structure = parse_txt_file(content=content)

        assert title == "Root"
        assert structure[0]["text"] == "L1"
        assert structure[0]["children"][0]["text"] == "L2"
        assert structure[0]["children"][0]["children"][0]["text"] == "L3"
        assert structure[0]["children"][0]["children"][0]["children"][0]["text"] == "L4"

    def test_parse_empty_content(self):
        """Test parsing empty content"""
        with pytest.raises(ValueError):
            parse_txt_file(content="")

    def test_parse_with_tabs(self):
        """Test parsing with tab indentation"""
        content = "Root\n\tChild 1\n\tChild 2"

        title, structure = parse_txt_file(content=content)

        assert title == "Root"
        assert len(structure) == 2
        assert structure[0]["text"] == "Child 1"

    def test_parse_mixed_indentation(self):
        """Test parsing with mixed spaces and tabs"""
        content = "Root\n  Child 1\n\tChild 2"

        title, structure = parse_txt_file(content=content)

        assert title == "Root"
        assert len(structure) == 2


class TestCreateXmindContent:
    """Test create_xmind_content function"""

    def test_create_simple_content(self):
        """Test creating simple XMind content"""
        tree_nodes = [
            {"text": "Node 1", "children": []},
            {"text": "Node 2", "children": []}
        ]

        content = create_xmind_content("Test Title", tree_nodes)

        assert len(content) == 1
        assert content[0]["title"] == "画布 1"
        assert content[0]["rootTopic"]["title"] == "Test Title"
        assert len(content[0]["rootTopic"]["children"]["attached"]) == 2

    def test_create_nested_content(self):
        """Test creating nested XMind content"""
        tree_nodes = [
            {
                "text": "Parent",
                "children": [
                    {"text": "Child", "children": []}
                ]
            }
        ]

        content = create_xmind_content("Test", tree_nodes)

        root_topic = content[0]["rootTopic"]
        assert root_topic["children"]["attached"][0]["title"] == "Parent"
        assert root_topic["children"]["attached"][0]["children"]["attached"][0]["title"] == "Child"

    def test_different_layouts(self):
        """Test different layout options"""
        tree_nodes = [{"text": "Node", "children": []}]

        layouts = {
            "right": "org.xmind.ui.logic.right",
            "map": "org.xmind.ui.map.unbalanced",
            "tree": "org.xmind.ui.tree.right",
            "org": "org.xmind.ui.org.down"
        }

        for layout_key, expected_class in layouts.items():
            content = create_xmind_content("Test", tree_nodes, layout=layout_key)
            assert content[0]["rootTopic"]["structureClass"] == expected_class


class TestSaveXmind:
    """Test save_xmind function"""

    def test_save_xmind_file(self, tmp_path):
        """Test saving XMind file"""
        filename = tmp_path / "test.xmind"
        title = "Test Mind Map"
        structure = [
            {"text": "Node 1", "children": []},
            {"text": "Node 2", "children": []}
        ]

        save_xmind(str(filename), title, structure)

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
        structure = [{"text": "Node", "children": []}]

        for layout in ["right", "map", "tree", "org"]:
            filename = tmp_path / f"test_{layout}.xmind"
            save_xmind(str(filename), "Test", structure, layout=layout)
            assert filename.exists()
