"""
命令行接口
"""

import argparse
import keyword
import re
import sys
from pathlib import Path

from .generator import ProjectGenerator

# Windows 保留名（不区分大小写）
# 参考: https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file
WINDOWS_RESERVED_NAMES = frozenset(
    {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "COM2",
        "COM3",
        "COM4",
        "COM5",
        "COM6",
        "COM7",
        "COM8",
        "COM9",
        "LPT1",
        "LPT2",
        "LPT3",
        "LPT4",
        "LPT5",
        "LPT6",
        "LPT7",
        "LPT8",
        "LPT9",
    }
)


def validate_name(name: str, name_type: str = "项目") -> str:
    """
    验证名称是否合法

    Args:
        name: 要验证的名称
        name_type: 名称类型（用于错误消息）

    Returns:
        验证通过的名称

    Raises:
        ValueError: 名称不合法时抛出
    """
    # 检查是否为空
    if not name or not name.strip():
        raise ValueError(f"{name_type}名称不能为空")

    name = name.strip()

    # 检查长度
    if len(name) > 50:
        raise ValueError(f"{name_type}名称不能超过50个字符")

    if len(name) < 2:
        raise ValueError(f"{name_type}名称至少需要2个字符")

    # 检查格式：只允许字母、数字、下划线和横线，且必须以字母开头
    pattern = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
    if not re.match(pattern, name):
        raise ValueError(f"{name_type}名称 '{name}' 不合法。要求：以字母开头，只能包含字母、数字、下划线(_)和横线(-)")

    # 检查是否是 Python 保留字
    if keyword.iskeyword(name):
        raise ValueError(f"{name_type}名称 '{name}' 是 Python 保留字，请换一个名称")

    # 检查是否是 Windows 保留名
    if name.upper() in WINDOWS_RESERVED_NAMES:
        raise ValueError(f"{name_type}名称 '{name}' 是 Windows 系统保留名，请换一个名称")

    # 检查路径遍历字符（安全检查）
    if ".." in name or "/" in name or "\\" in name:
        raise ValueError(f"{name_type}名称包含非法路径字符")

    return name


def validate_version(version: str) -> str:
    """验证 API 版本格式"""
    pattern = r"^v\d+$"
    if not re.match(pattern, version):
        raise ValueError(f"API版本格式不正确: '{version}'。正确格式示例: v1, v2, v3")
    return version


def main():
    parser = argparse.ArgumentParser(
        description="ANQ Scaff - 企业级FastAPI项目脚手架生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  anq-scaff new myproject              # 创建新项目
  anq-scaff new myproject --db mysql   # 指定数据库类型
  anq-scaff new myproject --redis      # 启用Redis
  anq-scaff new myproject --celery     # 启用Celery
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # new 命令
    new_parser = subparsers.add_parser("new", help="创建新项目")
    new_parser.add_argument("project_name", help="项目名称")
    new_parser.add_argument(
        "--db", choices=["sqlite", "mysql", "postgresql"], default="sqlite", help="数据库类型 (默认: sqlite)"
    )
    new_parser.add_argument("--redis", action="store_true", help="启用Redis缓存")
    new_parser.add_argument("--celery", action="store_true", help="启用Celery异步任务")
    new_parser.add_argument("--output-dir", type=str, default=".", help="项目输出目录 (默认: 当前目录)")

    # add 命令
    add_parser = subparsers.add_parser("add", help="添加API模块")
    add_parser.add_argument("module_name", help="模块名称")
    add_parser.add_argument("--path", type=str, default=".", help="项目路径 (默认: 当前目录)")
    add_parser.add_argument("--version", type=str, default="v1", help="API版本 (默认: v1)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "new":
            # 验证项目名称
            project_name = validate_name(args.project_name, "项目")

            generator = ProjectGenerator(
                project_name=project_name,
                db_type=args.db,
                enable_redis=args.redis,
                enable_celery=args.celery,
                output_dir=Path(args.output_dir),
            )
            generator.generate()
            print(f"\n✅ 项目 '{project_name}' 创建成功！")
            print(f"\n📁 项目路径: {generator.project_path}")
            print("\n🚀 快速开始:")
            print(f"  cd {project_name}")
            print("\n  # 使用 uv（推荐）")
            print("  uv venv                    # 创建虚拟环境")
            print("  uv pip install -r requirements.txt")
            print("  uv run python runserver.py")
            print("\n  # 或使用标准 venv")
            print("  python -m venv .venv")
            print("  pip install -r requirements.txt")
            print("  python runserver.py")

        elif args.command == "add":
            from .module_generator import ModuleGenerator

            # 验证模块名称和版本
            module_name = validate_name(args.module_name, "模块")
            version = validate_version(args.version)

            generator = ModuleGenerator(module_name=module_name, project_path=Path(args.path), version=version)
            generator.generate()
            print(f"\n✅ API模块 '{module_name}' 添加成功！")

    except ValueError as e:
        # 验证错误
        print(f"\n❌ 验证错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
