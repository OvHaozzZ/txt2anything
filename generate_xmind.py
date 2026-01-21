"""
多格式思维导图生成工具
支持 XMind、Markdown 等多种输出格式
"""

import os
import sys
from core.parser import parse_text
from format_manager import get_format_manager


def main():
    """主函数"""
    print("=" * 60)
    print("多格式思维导图生成工具")
    print("=" * 60)
    print()

    # 获取格式管理器
    manager = get_format_manager()

    # 默认参数
    layout = "right"
    output_format = "xmind"
    txt_file = None

    # 解析命令行参数
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        arg = args[i]

        if arg == "--layout":
            if i + 1 < len(args):
                layout = args[i + 1]
                i += 2
            else:
                print("[错误] --layout 参数需要指定值")
                sys.exit(1)

        elif arg == "--format":
            if i + 1 < len(args):
                output_format = args[i + 1]
                i += 2
            else:
                print("[错误] --format 参数需要指定值")
                sys.exit(1)

        elif arg == "--list-formats":
            print("支持的输出格式:")
            print()
            for fmt in manager.list_formats():
                print(f"  {fmt['name']:12} {fmt['extension']:8} - {fmt['description']}")
            print()
            sys.exit(0)

        elif arg in ["-h", "--help"]:
            show_help(manager)
            sys.exit(0)

        else:
            # 假设是文件路径
            txt_file = arg
            i += 1

    # 如果没有指定文件，显示帮助
    if not txt_file:
        show_help(manager)
        sys.exit(0)

    # 检查文件是否存在
    if not os.path.exists(txt_file):
        print(f"[错误] 文件不存在: {txt_file}")
        sys.exit(1)

    # 检查格式是否支持
    if not manager.is_format_supported(output_format):
        print(f"[错误] 不支持的格式: {output_format}")
        print()
        print("支持的格式:")
        for fmt in manager.list_formats():
            print(f"  - {fmt['name']}")
        sys.exit(1)

    # 对于 XMind 格式，验证布局参数
    if output_format == "xmind":
        valid_layouts = ["right", "map", "tree", "org"]
        if layout not in valid_layouts:
            print(f"[错误] 无效的布局参数: {layout}")
            print(f"[提示] 可用的布局: {', '.join(valid_layouts)}")
            sys.exit(1)

    try:
        # 解析文本文件
        print(f"[读取] 正在解析文件: {txt_file}")
        print(f"[格式] {output_format}")
        if output_format == "xmind":
            print(f"[布局] {layout}")

        title, tree_nodes = parse_text(txt_file=txt_file)

        # 生成输出文件名
        base_name = os.path.splitext(txt_file)[0]
        formatter = manager.get_formatter(output_format)
        output_file = base_name + formatter.file_extension

        # 导出文件
        options = {}
        if output_format == "xmind":
            options["layout"] = layout

        manager.export(output_format, title, tree_nodes, output_file, **options)

    except Exception as e:
        print(f"[错误] 处理失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def show_help(manager):
    """显示帮助信息"""
    print("[用法] python generate_xmind.py <txt文件路径> [选项]")
    print()
    print("选项:")
    print("  --format <格式>    输出格式（默认: xmind）")
    print("  --layout <布局>    XMind 布局类型（默认: right）")
    print("  --list-formats     列出所有支持的格式")
    print("  -h, --help         显示此帮助信息")
    print()
    print("支持的输出格式:")
    for fmt in manager.list_formats():
        print(f"  {fmt['name']:12} {fmt['extension']:8} - {fmt['description']}")
    print()
    print("XMind 布局类型:")
    print("  right - 向右展开（逻辑图）[默认]")
    print("  map   - 中心辐射（思维导图）")
    print("  tree  - 树状图（向右）")
    print("  org   - 组织结构图（向下）")
    print()
    print("示例:")
    print("  python generate_xmind.py example.txt")
    print("  python generate_xmind.py example.txt --format markdown")
    print("  python generate_xmind.py example.txt --format xmind --layout map")
    print("  python generate_xmind.py example.txt --list-formats")
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


if __name__ == "__main__":
    main()
