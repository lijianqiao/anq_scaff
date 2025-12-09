"""
模板引擎
"""

import logging
import string
from pathlib import Path
from typing import Any

# 常量定义
DEFAULT_DB_TYPE = "sqlite"
DEFAULT_ENCODING = "utf-8"

# 配置日志记录器
logger = logging.getLogger(__name__)


class ConfigBuilder:
    """
    配置构建器

    用于构建不同环境的配置文件内容。
    """

    def __init__(self, env: str, context: dict[str, Any]) -> None:
        """
        初始化配置构建器

        Args:
            env: 环境名称（dev/test/prod）
            context: 上下文字典，包含项目名称、数据库类型等
        """
        self.env = env
        self.context = context
        self.db_type = context.get("db_type", DEFAULT_DB_TYPE)
        self.enable_redis = context.get("enable_redis", False)
        self.project_name = context.get("project_name", "")

    def _get_db_config(self) -> dict[str, str]:
        """
        获取数据库配置

        Returns:
            包含 db_url 和 db_async_url 的字典
        """
        db_configs = {
            "sqlite": {
                "db_url": f"sqlite:///app_{self.env}.sqlite",
                "db_async_url": f"sqlite+aiosqlite:///app_{self.env}.sqlite",
            },
            "mysql": {
                "db_url": f"mysql+pymysql://user:password@localhost:3306/app_{self.env}?charset=utf8mb4",
                "db_async_url": f"mysql+aiomysql://user:password@localhost:3306/app_{self.env}?charset=utf8mb4",
            },
            "postgresql": {
                "db_url": f"postgresql://user:password@localhost:5432/app_{self.env}",
                "db_async_url": f"postgresql+asyncpg://user:password@localhost:5432/app_{self.env}",
            },
        }
        return db_configs.get(self.db_type, db_configs[DEFAULT_DB_TYPE])

    def _build_app_config(self) -> str:
        """
        构建应用配置部分

        Returns:
            应用配置的YAML字符串
        """
        return f"""# {self.project_name} - {self.env}环境配置
# 请根据自身需求修改

app_title: {self.project_name}-{self.env}
app_summary: {self.project_name} {self.env}环境
app_description: {self.project_name} {self.env}环境配置
app_version: 1.0.0
app_debug: {"true" if self.env == "dev" else "false"}
app_log_serialize: false
app_log_basedir: ./logs
app_disable_docs: {"false" if self.env == "dev" else "true"}
app_allow_credentials: true
app_allow_origins:
  - '*'
app_allow_methods:
  - '*'
app_allow_headers:
  - '*'
# #"""

    def _build_db_config(self) -> str:
        """
        构建数据库配置部分

        Returns:
            数据库配置的YAML字符串
        """
        db_config = self._get_db_config()
        return f"""db_url: {db_config["db_url"]}
db_async_url: {db_config["db_async_url"]}"""

    def _build_redis_config(self) -> str:
        """
        构建Redis配置部分

        Returns:
            Redis配置的YAML字符串
        """
        if self.enable_redis:
            return """redis_host: localhost
redis_port: 6379
redis_db: 0
redis_password:
redis_max_connections: 10"""
        else:
            return """redis_host:
redis_port:
redis_db:
redis_password:
redis_max_connections:"""

    def build(self) -> str:
        """
        构建完整的配置内容

        Returns:
            完整的YAML配置字符串
        """
        parts = [
            self._build_app_config(),
            self._build_db_config(),
            self._build_redis_config(),
        ]
        return "\n".join(parts)


class TemplateEngine:
    """简单的模板引擎"""

    def __init__(self) -> None:
        self.templates_dir = Path(__file__).parent / "templates"
        self.templates: dict[str, str] = {}
        self._load_templates()

    def _load_templates(self) -> None:
        """
        加载模板文件

        从模板目录加载所有模板文件到内存中。
        """
        if not self.templates_dir.exists():
            # 如果模板目录不存在，使用内联模板
            logger.warning(f"模板目录不存在: {self.templates_dir}，使用内联模板")
            self.templates = self._get_inline_templates()
        else:
            # 加载所有 .py 文件（排除 __init__.py）
            py_count = 0
            for template_file in self.templates_dir.glob("*.py"):
                if template_file.name == "__init__.py":
                    continue
                template_name = template_file.stem
                self.templates[template_name] = template_file.read_text(encoding=DEFAULT_ENCODING)
                py_count += 1

            # 也加载其他类型的模板文件
            other_count = 0
            for ext in ["*.txt", "*.md", "*.ini", "*.toml", "*.yaml", "*.json", "*.js"]:
                for template_file in self.templates_dir.glob(ext):
                    template_name = template_file.name
                    self.templates[template_name] = template_file.read_text(encoding=DEFAULT_ENCODING)
                    other_count += 1

            # 加载无扩展名的特殊文件（如 Dockerfile, gitignore, env_example 等）
            special_files = ["Dockerfile", "gitignore", "dockerignore", "env_example"]
            for filename in special_files:
                template_file = self.templates_dir / filename
                if template_file.exists():
                    self.templates[filename] = template_file.read_text(encoding=DEFAULT_ENCODING)
                    other_count += 1

            logger.debug(f"加载模板文件完成: {py_count} 个Python文件, {other_count} 个其他文件")

    def render(self, template_name: str, context: dict[str, Any]) -> str:
        """渲染模板"""
        template = self.templates.get(template_name)
        if not template:
            # 如果模板不存在，使用内联模板
            inline_templates = self._get_inline_templates()
            template = inline_templates.get(template_name, "")

        if not template:
            return f"# Template {template_name} not found\n"

        # 简单的字符串替换
        return string.Template(template).safe_substitute(**context)

    def render_config(self, env: str, context: dict[str, Any]) -> str:
        """
        渲染配置文件

        Args:
            env: 环境名称（dev/test/prod）
            context: 上下文字典，包含项目名称、数据库类型等

        Returns:
            渲染后的配置文件内容（YAML格式）
        """
        config_builder = ConfigBuilder(env, context)
        return config_builder.build()

    def _get_inline_templates(self) -> dict[str, str]:
        """获取内联模板（当模板文件不存在时使用）"""
        # 尝试从当前项目的admin-fastapi目录读取模板
        # 尝试从当前项目的admin-fastapi目录读取模板
        base_dir = Path(__file__).parent.parent.parent
        admin_fastapi_dir = base_dir / "admin-fastapi"

        if admin_fastapi_dir.exists():
            return self._load_from_existing_project(admin_fastapi_dir)

        return {}

    def _load_from_existing_project(self, project_dir: Path) -> dict[str, str]:
        """从现有项目加载模板"""
        templates = {}

        # 映射模板名称到实际文件路径
        template_mapping = {
            "main.py": project_dir / "app" / "main.py",
            "app_init.py": project_dir / "app" / "__init__.py",
            "runserver.py": project_dir / "runserver.py",
            "api_init.py": project_dir / "app" / "api" / "__init__.py",
            "api_dependencies.py": project_dir / "app" / "api" / "dependencies.py",
            "api_exceptions.py": project_dir / "app" / "api" / "exceptions.py",
            "api_responses.py": project_dir / "app" / "api" / "responses.py",
            "api_status.py": project_dir / "app" / "api" / "status.py",
            "api_ping.py": project_dir / "app" / "api" / "default" / "ping.py",
            "models_init.py": project_dir / "app" / "models" / "__init__.py",
            "schemas_init.py": project_dir / "app" / "schemas" / "__init__.py",
            "initializer_init.py": project_dir / "app" / "initializer" / "__init__.py",
            "initializer_conf.py": project_dir / "app" / "initializer" / "_conf.py",
            "initializer_db.py": project_dir / "app" / "initializer" / "_db.py",
            "initializer_log.py": project_dir / "app" / "initializer" / "_log.py",
            "initializer_redis.py": project_dir / "app" / "initializer" / "_redis.py",
            "initializer_snow.py": project_dir / "app" / "initializer" / "_snow.py",
            "initializer_context.py": project_dir / "app" / "initializer" / "context.py",
            "middleware_init.py": project_dir / "app" / "middleware" / "__init__.py",
            "middleware_cors.py": project_dir / "app" / "middleware" / "cors.py",
            "middleware_exceptions.py": project_dir / "app" / "middleware" / "exceptions.py",
            "middleware_http.py": project_dir / "app" / "middleware" / "http.py",
            "utils_jwt.py": project_dir / "app" / "utils" / "jwt_util.py",
            "utils_db_async.py": project_dir / "app" / "utils" / "db_async_util.py",
            "utils_api_key.py": project_dir / "app" / "utils" / "api_key_util.py",
        }

        for template_name, file_path in template_mapping.items():
            if file_path.exists():
                try:
                    templates[template_name] = file_path.read_text(encoding=DEFAULT_ENCODING)
                except Exception:
                    pass

        return templates
