"""
文本解析模块
负责将缩进文本解析为树形结构
"""


def parse_text(txt_file=None, content=None):
    """
    解析缩进格式的 txt 文件或文本内容

    格式示例:
    根节点
      子节点1
        孙节点1
        孙节点2
      子节点2
        孙节点3

    参数:
        txt_file: 文本文件路径
        content: 文本内容字符串

    返回:
        (title, tree_nodes) - 标题和树形结构节点列表
        tree_nodes 格式: [{"text": "节点文本", "children": [...]}, ...]
    """
    if content:
        lines = content.splitlines()
    elif txt_file:
        with open(txt_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        raise ValueError("必须提供 txt_file 或 content 参数")

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
        raw_len = len(line)
        lstrip_len = len(line.lstrip())
        indent_char_count = raw_len - lstrip_len

        # 统计制表符和空格
        # 1个 tab = 1级，2个 space = 1级
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

    return title, root_children
