"""
生成 XMind 格式的思维导图
支持多层次结构，无需手动导入
"""

import json
import zipfile
import os
from datetime import datetime
import re

def parse_txt_file(txt_file=None, content=None):
    """
    解析缩进格式的 txt 文件 或 文本内容

    格式示例:
    根节点
      子节点1
        孙节点1
        孙节点2
      子节点2
        孙节点3

    返回: (title, tree_nodes) - 标题和树形结构节点列表
    """
    if content:
        lines = content.splitlines()
    elif txt_file:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        raise ValueError("必须提供 txt_file 或 content")

    if not lines:
        raise ValueError("内容为空")

    # 移除空行并保留原始缩进
    lines = [line for line in lines if line.strip()]

    if not lines:
        return "无标题", []

    # 第一行作为标题
    title = lines[0].strip()

    # 解析层级结构
    def get_indent_level(line):
        """计算缩进级别（每2个空格或1个制表符为一级）"""
        # 计算行首空白字符
        raw_len = len(line)
        lstrip_len = len(line.lstrip())
        indent_char_count = raw_len - lstrip_len
        
        # 简单处理：统计 \t 和 空格
        # 假设：1个 tab = 1级，2个 space = 1级
        # 为了兼容混合缩进，我们需要重新计算
        prefix = line[:indent_char_count]
        tabs = prefix.count('\t')
        spaces = prefix.count(' ')
        return tabs + spaces // 2

    # 构建树形结构
    root_children = []
    # 栈结构：[(level, children_list)]
    stack = [(-1, root_children)]

    # 从第二行开始遍历
    for i in range(1, len(lines)):
        line = lines[i]

        level = get_indent_level(line)
        text = line.strip()

        # 找到当前节点应该添加到哪个父节点
        # 回退到合适的父节点层级
        while len(stack) > 1 and stack[-1][0] >= level:
            stack.pop()

        # 创建当前节点
        node = {"text": text, "children": []}
        stack[-1][1].append(node)

        # 将当前节点的 children 列表加入栈，供下一层级使用
        stack.append((level, node["children"]))

    # 直接返回树形结构，支持任意深度
    return title, root_children

def create_xmind_content(title, tree_nodes, layout="right"):
    """
    创建 XMind 内容（支持任意深度层级）

    tree_nodes 格式:
    [
        {"text": "节点1", "children": [
            {"text": "子节点1", "children": [...]},
            ...
        ]},
        ...
    ]

    layout 参数:
    - "right": 向右展开（逻辑图）
    - "map": 中心辐射（思维导图）
    - "tree": 树状图（向右）
    - "org": 组织结构图（向下）
    """

    # 布局样式映射
    layout_map = {
        "right": "org.xmind.ui.logic.right",
        "map": "org.xmind.ui.map.unbalanced",
        "tree": "org.xmind.ui.tree.right",
        "org": "org.xmind.ui.org.down"
    }

    structure_class = layout_map.get(layout, "org.xmind.ui.logic.right")

    # 生成唯一 ID
    def gen_id():
        import random
        return ''.join(random.choices('0123456789abcdef', k=26))

    # 构建单个节点
    def build_node(text, children=None):
        node = {
            "id": gen_id(),
            "title": text,
            "structureClass": structure_class
        }

        if children:
            node["children"] = {
                "attached": children
            }

        return node

    # 递归构建任意深度的节点树
    def build_tree(nodes):
        result = []
        for node in nodes:
            children = build_tree(node["children"]) if node["children"] else None
            result.append(build_node(node["text"], children))
        return result

    # 构建所有子节点
    attached_nodes = build_tree(tree_nodes)

    # 构建根节点
    root_topic = build_node(title, attached_nodes)

    # 完整的 XMind 结构
    content = [{
        "id": gen_id(),
        "title": "画布 1",
        "rootTopic": root_topic
    }]

    return content

def save_xmind(filename, title, structure, layout="right"):
    """保存为 .xmind 文件"""

    # 创建临时目录
    temp_dir = "temp_xmind"
    os.makedirs(temp_dir, exist_ok=True)

    # 1. 创建 content.json
    content = create_xmind_content(title, structure, layout)
    with open(f"{temp_dir}/content.json", "w", encoding="utf-8") as f:
        json.dump(content, f, ensure_ascii=False, indent=2)

    # 2. 创建 metadata.json
    metadata = {
        "creator": {
            "name": "Claude Code",
            "version": "1.0"
        },
        "created": int(datetime.now().timestamp() * 1000)
    }
    with open(f"{temp_dir}/metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # 3. 创建 manifest.json
    manifest = {
        "file-entries": {
            "content.json": {},
            "metadata.json": {}
        }
    }
    with open(f"{temp_dir}/manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    # 4. 打包成 .xmind 文件（实际上是 ZIP）
    with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(f"{temp_dir}/content.json", "content.json")
        zipf.write(f"{temp_dir}/metadata.json", "metadata.json")
        zipf.write(f"{temp_dir}/manifest.json", "manifest.json")

    # 5. 清理临时文件
    for file in ["content.json", "metadata.json", "manifest.json"]:
        os.remove(f"{temp_dir}/{file}")
    os.rmdir(temp_dir)

    print(f"[OK] XMind 文件生成成功: {filename}")
    print(f"[提示] 直接用 XMind 打开即可，支持完整的多层次结构！")

# ============ 主函数 ============
if __name__ == "__main__":
    print("=" * 60)
    print("XMind 思维导图生成工具")
    print("=" * 60)
    print()

    # 检查是否有命令行参数指定 txt 文件
    import sys

    # 默认布局
    layout = "right"
    txt_file = None

    # 解析命令行参数
    if len(sys.argv) > 1:
        # 检查是否有 --layout 参数
        if "--layout" in sys.argv:
            layout_index = sys.argv.index("--layout")
            if layout_index + 1 < len(sys.argv):
                layout = sys.argv[layout_index + 1]
                # 移除 --layout 和其值
                sys.argv.pop(layout_index)
                sys.argv.pop(layout_index)

        # 获取 txt 文件路径
        if len(sys.argv) > 1:
            txt_file = sys.argv[1]

    if txt_file:
        if not os.path.exists(txt_file):
            print(f"[错误] 文件不存在: {txt_file}")
            sys.exit(1)

        # 验证布局参数
        valid_layouts = ["right", "map", "tree", "org"]
        if layout not in valid_layouts:
            print(f"[错误] 无效的布局参数: {layout}")
            print(f"[提示] 可用的布局: {', '.join(valid_layouts)}")
            sys.exit(1)

        try:
            print(f"[读取] 正在解析 txt 文件: {txt_file}")
            print(f"[布局] {layout}")
            title, structure = parse_txt_file(txt_file)

            # 生成输出文件名
            output_file = os.path.splitext(txt_file)[0] + ".xmind"
            save_xmind(output_file, title, structure, layout)

        except Exception as e:
            print(f"[错误] 解析失败: {e}")
            sys.exit(1)

    else:
        # 没有指定文件，显示帮助信息
        print("[提示] 未指定 txt 文件")
        print("[用法] python generate_xmind.py <txt文件路径> [--layout <布局类型>]")
        print()
        print("布局类型:")
        print("  right - 向右展开（逻辑图）[默认]")
        print("  map   - 中心辐射（思维导图）")
        print("  tree  - 树状图（向右）")
        print("  org   - 组织结构图（向下）")
        print()
        print("示例:")
        print("  python generate_xmind.py example.txt")
        print("  python generate_xmind.py example.txt --layout map")
        print("  python generate_xmind.py example.txt --layout tree")
        print()
        print("txt 文件格式:")
        print("-" * 60)
        print("思维导图标题")
        print("  一级节点1")
        print("    二级节点1")
        print("    二级节点2")
        print("  一级节点2")
        print("    二级节点3")
        print("-" * 60)