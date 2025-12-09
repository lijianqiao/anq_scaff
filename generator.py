"""
项目生成器

用于生成 FastAPI 项目的脚手架工具。
"""

import logging
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

from anq_scaff.template_engine import TemplateEngine

# 配置日志记录器
logger = logging.getLogger(__name__)

# ========== 常量定义 ==========
DEFAULT_DB_TYPE = "sqlite"
DEFAULT_ENCODING = "utf-8"
SUPPORTED_DB_TYPES = {"sqlite", "mysql", "postgresql"}

# 数据库依赖映射
DB_DEPENDENCIES: dict[str, list[str]] = {
    "sqlite": ["aiosqlite==0.21.0"],
    "mysql": ["aiomysql==0.2.0", "pymysql==1.1.0"],
    "postgresql": ["asyncpg==0.29.0", "psycopg2-binary==2.9.9"],
}

REDIS_DEPENDENCY = "redis==7.1.0"

# 项目目录结构配置
PROJECT_STRUCTURE = {
    "api": {
        "versions": ["v1"],
        "default": True,
    },
    "layers": {
        "initializer": True,
        "middleware": True,
        "models": True,
        "schemas": True,
        "services": True,
        "utils": True,
        "cache": True,  # 始终启用，自动降级为内存缓存
    },
    "docs": True,
    "logs": True,
    "tests": True,
    "celery": False,  # 可选，由 enable_celery 控制
}

# 模板到目标文件的映射规则
# 格式: (目标路径, 条件函数或None)
TEMPLATE_MAPPING: dict[str, tuple[str, Callable[[dict[str, Any]], bool] | None]] = {
    # Initializer 文件
    "initializer_init.py": ("app/initializer/__init__.py", None),  # 始终包含缓存支持
    "pydantic_settings_config.py": ("app/initializer/_settings.py", None),
    "initializer_db.py": ("app/initializer/_db.py", None),
    "initializer_log.py": ("app/initializer/_log.py", None),
    "initializer_redis.py": ("app/initializer/_redis.py", None),
    "initializer_snow.py": ("app/initializer/_snow.py", None),
    "initializer_context.py": ("app/initializer/context.py", None),
    # Cache 文件
    "cache_init.py": ("app/cache/__init__.py", None),
    "cache_manager.py": ("app/cache/manager.py", None),
    # Middleware 文件
    "middleware_init.py": ("app/middleware/__init__.py", None),
    "middleware_cors.py": ("app/middleware/cors.py", None),
    "middleware_exceptions.py": ("app/middleware/exceptions.py", None),
    "middleware_http.py": ("app/middleware/http.py", None),
    # Utils 文件
    "utils_jwt.py": ("app/utils/jwt_util.py", None),
    "utils_db_async.py": ("app/utils/db_async_util.py", None),
    "utils_api_key.py": ("app/utils/api_key_util.py", None),
    # API 文件
    "api_init.py": ("app/api/__init__.py", None),
    "api_dependencies.py": ("app/api/dependencies.py", None),
    "api_exceptions.py": ("app/api/exceptions.py", None),
    "api_responses.py": ("app/api/responses.py", None),
    "api_status.py": ("app/api/status.py", None),
    "api_ping.py": ("app/api/default/ping.py", None),
    # Models/Schemas 文件
    "models_init.py": ("app/models/__init__.py", None),
    "schemas_init.py": ("app/schemas/__init__.py", None),
    # Enterprise features
    "unified_router.py": ("app/api/unified_router.py", None),
    "exception_system.py": ("app/api/exceptions_enterprise.py", None),
    "context_logging.py": ("app/utils/context_logging.py", None),
    "logging_fastcrud.py": ("app/utils/logging_fastcrud.py", None),
    "lifespan_manager.py": ("app/core/lifespan.py", None),
}


class ProjectGenerator:
    """
    项目生成器

    用于生成完整的 FastAPI 项目结构，包括配置、代码模板、测试文件等。

    Attributes:
        project_name: 项目名称
        db_type: 数据库类型（sqlite/mysql/postgresql）
        enable_redis: 是否启用 Redis
        enable_celery: 是否启用 Celery
        output_dir: 输出目录
        project_path: 项目完整路径
        template_engine: 模板引擎实例
    """

    def __init__(
        self,
        project_name: str,
        db_type: str = "sqlite",
        enable_redis: bool = False,
        enable_celery: bool = False,
        output_dir: Path = Path("."),
    ) -> None:
        """
        初始化项目生成器

        Args:
            project_name: 项目名称
            db_type: 数据库类型，可选值：sqlite, mysql, postgresql
            enable_redis: 是否启用 Redis 缓存
            enable_celery: 是否启用 Celery 异步任务
            output_dir: 项目输出目录，默认为当前目录
        """
        self.project_name = project_name
        self.db_type = db_type
        self.enable_redis = enable_redis
        self.enable_celery = enable_celery
        self.output_dir = output_dir
        self.project_path = output_dir / project_name
        self.template_engine = TemplateEngine()

    def _build_directory_list(self) -> list[str]:
        """
        根据配置构建目录列表

        Returns:
            目录路径列表
        """
        directories: list[str] = []

        # API 目录
        if PROJECT_STRUCTURE["api"]["default"]:
            directories.append("app/api/default")
        for version in PROJECT_STRUCTURE["api"]["versions"]:
            directories.append(f"app/api/{version}")

        # 各层目录
        for layer_name, enabled in PROJECT_STRUCTURE["layers"].items():
            if enabled:
                directories.append(f"app/{layer_name}")

        # 其他目录
        for dir_name, enabled in [
            ("docs", PROJECT_STRUCTURE["docs"]),
            ("logs", PROJECT_STRUCTURE["logs"]),
            ("tests", PROJECT_STRUCTURE["tests"]),
        ]:
            if enabled:
                directories.append(dir_name)

        # Celery 目录
        if PROJECT_STRUCTURE["celery"] and self.enable_celery:
            directories.append("app_celery")

        return directories

    def _get_template_target_path(self, template_name: str, context: dict[str, Any]) -> Path | None:
        """
        根据模板映射规则获取目标文件路径

        Args:
            template_name: 模板名称
            context: 上下文字典

        Returns:
            目标文件路径，如果不存在映射则返回 None
        """
        mapping = TEMPLATE_MAPPING.get(template_name)
        if mapping:
            target_path, condition = mapping
            if condition is None or condition(context):
                return self.project_path / target_path
        return None

    def _get_template_name(self, template_name: str) -> str:
        """
        获取正确的模板名称（处理 .py 文件的扩展名问题）

        Args:
            template_name: 原始模板名称（可能带 .py 扩展名）

        Returns:
            正确的模板名称（.py 文件去掉扩展名，其他文件保持原样）
        """
        # 对于 .py 文件，模板引擎使用 stem（去掉扩展名）
        if template_name.endswith(".py"):
            return template_name[:-3]  # 去掉 .py
        return template_name

    def _validate_template_exists(self, template_name: str) -> None:
        """
        验证模板文件是否存在

        Args:
            template_name: 模板名称（可能带 .py 扩展名）

        Raises:
            ValueError: 如果模板不存在
        """
        actual_name = self._get_template_name(template_name)
        if actual_name not in self.template_engine.templates:
            available = ", ".join(sorted(self.template_engine.templates.keys()))
            raise ValueError(f"模板 '{template_name}' (实际名称: '{actual_name}') 不存在。\n可用模板: {available}")

    def _render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """
        渲染模板（自动处理模板名称转换）

        Args:
            template_name: 模板名称（可能带 .py 扩展名）
            context: 上下文字典

        Returns:
            渲染后的内容
        """
        actual_name = self._get_template_name(template_name)
        return self.template_engine.render(actual_name, context)

    def generate(self) -> None:
        """
        生成完整的项目结构

        Raises:
            ValueError: 如果项目目录已存在
            OSError: 如果文件系统操作失败
        """
        logger.info(
            f"开始生成项目: {self.project_name} (数据库: {self.db_type}, Redis: {self.enable_redis}, Celery: {self.enable_celery})"
        )

        if self.project_path.exists():
            error_msg = f"项目目录 '{self.project_path}' 已存在"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # 创建项目目录
            logger.debug(f"创建项目目录: {self.project_path}")
            self.project_path.mkdir(parents=True, exist_ok=True)

            # 生成项目结构
            logger.debug("生成项目目录结构")
            self._create_directory_structure()

            # 生成核心代码文件
            logger.debug("生成核心代码文件")
            self._generate_core_files()

            # 生成初始化文件
            logger.debug("生成初始化文件")
            self._generate_initializer_files()

            # 生成中间件文件
            logger.debug("生成中间件文件")
            self._generate_middleware_files()

            # 生成工具文件
            logger.debug("生成工具文件")
            self._generate_utils_files()

            # 生成缓存文件（始终生成，自动降级为内存缓存）
            logger.debug("生成缓存文件")
            self._generate_cache_files()

            # 生成API示例
            logger.debug("生成API示例")
            self._generate_api_example()

            # 生成服务示例
            logger.debug("生成服务示例")
            self._generate_service_example()

            # 生成模型示例
            logger.debug("生成模型示例")
            self._generate_model_example()

            # 生成Schema示例
            logger.debug("生成Schema示例")
            self._generate_schema_example()

            # 生成企业级特性文件
            logger.debug("生成企业级特性文件")
            self._generate_enterprise_features()

            # 生成测试文件
            logger.debug("生成测试文件")
            self._generate_test_files()

            # 生成文档文件
            logger.debug("生成文档文件")
            self._generate_docs_files()

            # 生成其他文件
            logger.debug("生成其他文件")
            self._generate_other_files()

            logger.info(f"项目 '{self.project_name}' 生成成功: {self.project_path}")
        except Exception as e:
            # 如果生成失败，尝试清理已创建的目录
            logger.error(f"项目生成失败: {e}", exc_info=True)
            if self.project_path.exists():
                try:
                    logger.debug(f"清理已创建的项目目录: {self.project_path}")
                    shutil.rmtree(self.project_path)
                except Exception as cleanup_error:
                    logger.warning(f"清理目录失败: {cleanup_error}")
            raise RuntimeError(f"项目生成失败: {e}") from e

    def _create_directory_structure(self) -> None:
        """
        创建项目目录结构

        Raises:
            OSError: 如果目录创建失败
        """
        directories = self._build_directory_list()

        for directory in directories:
            try:
                (self.project_path / directory).mkdir(parents=True, exist_ok=True)
                # 创建 __init__.py
                init_file = self.project_path / directory / "__init__.py"
                if not init_file.exists():
                    init_file.write_text('"""\n"""\n', encoding=DEFAULT_ENCODING)
            except OSError as e:
                raise OSError(f"创建目录失败: {directory}, 错误: {e}") from e

    def _generate_core_files(self) -> None:
        """
        生成核心文件

        生成 main.py 和 app/__init__.py 等核心文件。
        """
        context = {
            "project_name": self.project_name,
            "enable_redis": self.enable_redis,
        }

        # main.py
        try:
            self._validate_template_exists("main.py")
            content = self._render_template("main.py", context)
            (self.project_path / "app" / "main.py").write_text(content, encoding=DEFAULT_ENCODING)
        except Exception as e:
            raise RuntimeError(f"生成 main.py 失败: {e}") from e

        # __init__.py
        try:
            self._validate_template_exists("app_init.py")
            content = self._render_template("app_init.py", context)
            (self.project_path / "app" / "__init__.py").write_text(content, encoding=DEFAULT_ENCODING)
        except Exception as e:
            raise RuntimeError(f"生成 app/__init__.py 失败: {e}") from e

    def _generate_initializer_files(self) -> None:
        """
        生成初始化文件

        生成数据库、日志、Redis、Snowflake ID 等初始化文件。
        """
        context = {
            "project_name": self.project_name,
            "db_type": self.db_type,
            "enable_redis": self.enable_redis,
        }

        files = [
            "pydantic_settings_config.py",
            "initializer_db.py",
            "initializer_log.py",
            "initializer_redis.py",
            "initializer_snow.py",
            "initializer_context.py",
        ]

        # 始终使用包含缓存支持的 initializer_init.py
        files.insert(0, "initializer_init.py")

        for file_template in files:
            try:
                self._validate_template_exists(file_template)
                content = self._render_template(file_template, context)
                target_path = self._get_template_target_path(file_template, context)
                if target_path:
                    target_path.write_text(content, encoding=DEFAULT_ENCODING)
                else:
                    # 回退到旧逻辑（兼容性）
                    if file_template == "initializer_init_with_cache.py":
                        target_file = "__init__.py"
                    else:
                        target_file = file_template.replace("initializer_", "_").replace(".py", ".py")
                    (self.project_path / "app" / "initializer" / target_file).write_text(
                        content, encoding=DEFAULT_ENCODING
                    )
            except Exception as e:
                raise RuntimeError(f"生成初始化文件失败: {file_template}, 错误: {e}") from e

        # 缓存初始化已移至 _generate_cache_files() 方法

    def _generate_middleware_files(self) -> None:
        """
        生成中间件文件

        生成 CORS、异常处理、HTTP 等中间件文件。
        """
        context = {"project_name": self.project_name}

        files = [
            "middleware_init.py",
            "middleware_cors.py",
            "middleware_exceptions.py",
            "middleware_http.py",
        ]

        for file_template in files:
            try:
                self._validate_template_exists(file_template)
                content = self._render_template(file_template, context)
                target_path = self._get_template_target_path(file_template, context)
                if target_path:
                    target_path.write_text(content, encoding=DEFAULT_ENCODING)
                else:
                    # 回退到旧逻辑（兼容性）
                    target_file = file_template.replace("middleware_", "").replace(".py", ".py")
                    (self.project_path / "app" / "middleware" / target_file).write_text(
                        content, encoding=DEFAULT_ENCODING
                    )
            except Exception as e:
                raise RuntimeError(f"生成中间件文件失败: {file_template}, 错误: {e}") from e

    def _generate_utils_files(self) -> None:
        """
        生成工具文件

        生成 JWT、数据库异步操作、API Key 等工具文件。
        """
        context = {
            "project_name": self.project_name,
            "enable_redis": self.enable_redis,
        }

        files = [
            "utils_jwt.py",
            "utils_db_async.py",
            "utils_api_key.py",
        ]

        for file_template in files:
            try:
                self._validate_template_exists(file_template)
                content = self._render_template(file_template, context)
                target_path = self._get_template_target_path(file_template, context)
                if target_path:
                    target_path.write_text(content, encoding=DEFAULT_ENCODING)
                else:
                    # 回退到旧逻辑（兼容性）
                    target_file = file_template.replace("utils_", "").replace(".py", ".py")
                    (self.project_path / "app" / "utils" / target_file).write_text(content, encoding=DEFAULT_ENCODING)
            except Exception as e:
                raise RuntimeError(f"生成工具文件失败: {file_template}, 错误: {e}") from e

    def _generate_cache_files(self) -> None:
        """
        生成缓存文件

        始终生成缓存模块，自动降级为内存缓存（如果 Redis 不可用）。
        """
        try:
            # cache/__init__.py
            self._validate_template_exists("cache_init.py")
            content = self._render_template("cache_init.py", {})
            (self.project_path / "app" / "cache" / "__init__.py").write_text(content, encoding=DEFAULT_ENCODING)

            # cache/manager.py
            self._validate_template_exists("cache_manager.py")
            content = self._render_template("cache_manager.py", {})
            (self.project_path / "app" / "cache" / "manager.py").write_text(content, encoding=DEFAULT_ENCODING)
        except Exception as e:
            raise RuntimeError(f"生成缓存文件失败: {e}") from e

    def _generate_api_example(self) -> None:
        """
        生成API示例

        生成 API 路由、依赖、响应、状态码等文件。
        """
        try:
            # API __init__.py (路由注册)
            self._validate_template_exists("api_init.py")
            content = self._render_template("api_init.py", {"project_name": self.project_name})
            target_path = self._get_template_target_path("api_init.py", {"project_name": self.project_name})
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "api" / "__init__.py").write_text(content, encoding=DEFAULT_ENCODING)

            # API 依赖文件
            self._validate_template_exists("api_dependencies.py")
            content = self._render_template(
                "api_dependencies.py",
                {
                    "project_name": self.project_name,
                    "enable_redis": self.enable_redis,
                },
            )
            target_path = self._get_template_target_path("api_dependencies.py", {"project_name": self.project_name})
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "api" / "dependencies.py").write_text(content, encoding=DEFAULT_ENCODING)

            # API 异常、响应、状态码
            for file_template in ["api_exceptions.py", "api_responses.py", "api_status.py"]:
                try:
                    self._validate_template_exists(file_template)
                    content = self._render_template(file_template, {"project_name": self.project_name})
                    target_path = self._get_template_target_path(file_template, {"project_name": self.project_name})
                    if target_path:
                        target_path.write_text(content, encoding=DEFAULT_ENCODING)
                    else:
                        target_file = file_template.replace("api_", "").replace(".py", ".py")
                        (self.project_path / "app" / "api" / target_file).write_text(content, encoding=DEFAULT_ENCODING)
                except Exception as e:
                    raise RuntimeError(f"生成 API 文件失败: {file_template}, 错误: {e}") from e

            # 默认ping接口
            self._validate_template_exists("api_ping.py")
            content = self._render_template("api_ping.py", {})
            target_path = self._get_template_target_path("api_ping.py", {})
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "api" / "default" / "ping.py").write_text(
                    content, encoding=DEFAULT_ENCODING
                )
        except Exception as e:
            raise RuntimeError(f"生成 API 示例失败: {e}") from e

    def _generate_service_example(self) -> None:
        """
        生成服务示例

        生成服务层的初始化文件。
        """
        # services __init__.py
        content = '"""\n业务逻辑层\n"""\n'
        (self.project_path / "app" / "services" / "__init__.py").write_text(content, encoding=DEFAULT_ENCODING)

    def _generate_model_example(self) -> None:
        """
        生成模型示例

        生成数据库模型层的初始化文件。
        """
        # models __init__.py
        content = self._render_template("models_init.py", {})
        (self.project_path / "app" / "models" / "__init__.py").write_text(content, encoding=DEFAULT_ENCODING)

    def _generate_schema_example(self) -> None:
        """
        生成Schema示例

        生成 Pydantic Schema 层的初始化文件。
        """
        # schemas __init__.py
        self._validate_template_exists("schemas_init.py")
        content = self._render_template("schemas_init.py", {})
        target_path = self._get_template_target_path("schemas_init.py", {})
        if target_path:
            target_path.write_text(content, encoding=DEFAULT_ENCODING)
        else:
            (self.project_path / "app" / "schemas" / "__init__.py").write_text(content, encoding=DEFAULT_ENCODING)

    def _generate_enterprise_features(self) -> None:
        """
        生成企业级特性文件

        生成统一路由、异常处理、上下文日志等企业级特性文件。
        """
        context = {
            "project_name": self.project_name,
            "enable_redis": self.enable_redis,
        }

        try:
            # 统一路由接口
            self._validate_template_exists("unified_router.py")
            content = self._render_template("unified_router.py", context)
            target_path = self._get_template_target_path("unified_router.py", context)
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "api" / "unified_router.py").write_text(content, encoding=DEFAULT_ENCODING)

            # 异常处理系统
            self._validate_template_exists("exception_system.py")
            content = self._render_template("exception_system.py", context)
            target_path = self._get_template_target_path("exception_system.py", context)
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "api" / "exceptions_enterprise.py").write_text(
                    content, encoding=DEFAULT_ENCODING
                )

            # 上下文感知日志
            self._validate_template_exists("context_logging.py")
            content = self._render_template("context_logging.py", context)
            target_path = self._get_template_target_path("context_logging.py", context)
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "utils" / "context_logging.py").write_text(
                    content, encoding=DEFAULT_ENCODING
                )

            # LoggingFastCRUD
            self._validate_template_exists("logging_fastcrud.py")
            content = self._render_template("logging_fastcrud.py", context)
            target_path = self._get_template_target_path("logging_fastcrud.py", context)
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "utils" / "logging_fastcrud.py").write_text(
                    content, encoding=DEFAULT_ENCODING
                )

            # Pydantic Settings配置
            self._validate_template_exists("pydantic_settings_config.py")
            content = self._render_template("pydantic_settings_config.py", context)
            target_path = self._get_template_target_path("pydantic_settings_config.py", context)
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "initializer" / "_settings.py").write_text(
                    content, encoding=DEFAULT_ENCODING
                )

            # 创建core目录（必须在写入lifespan.py之前）
            (self.project_path / "app" / "core").mkdir(parents=True, exist_ok=True)
            (self.project_path / "app" / "core" / "__init__.py").write_text(
                '"""\n核心模块\n"""\n', encoding=DEFAULT_ENCODING
            )

            # 生命周期管理
            self._validate_template_exists("lifespan_manager.py")
            content = self._render_template("lifespan_manager.py", context)
            target_path = self._get_template_target_path("lifespan_manager.py", context)
            if target_path:
                target_path.write_text(content, encoding=DEFAULT_ENCODING)
            else:
                (self.project_path / "app" / "core" / "lifespan.py").write_text(content, encoding=DEFAULT_ENCODING)
        except Exception as e:
            raise RuntimeError(f"生成企业级特性文件失败: {e}") from e

    def _generate_test_files(self) -> None:
        """
        生成测试文件

        生成包括 conftest.py、测试示例、pytest配置等测试相关文件。
        """
        context = {
            "project_name": self.project_name,
            "db_type": self.db_type,
            "enable_redis": self.enable_redis,
            "enable_celery": self.enable_celery,
        }

        try:
            # 测试基础类（pytest 标准：conftest.py）
            self._validate_template_exists("conftest.py")
            content = self._render_template("conftest.py", {})
            (self.project_path / "tests" / "conftest.py").write_text(content, encoding=DEFAULT_ENCODING)

            # 测试示例
            self._validate_template_exists("test_example.py")
            content = self._render_template("test_example.py", {})
            (self.project_path / "tests" / "test_example.py").write_text(content, encoding=DEFAULT_ENCODING)

            # pytest配置
            self._validate_template_exists("pytest.ini")
            content = self._render_template("pytest.ini", {})
            (self.project_path / "pytest.ini").write_text(content, encoding=DEFAULT_ENCODING)

            # 代码生成脚本
            self._validate_template_exists("generate_code.js")
            content = self._render_template("generate_code.js", {})
            (self.project_path / "generate_code.js").write_text(content, encoding=DEFAULT_ENCODING)

            # package.json
            self._validate_template_exists("package.json")
            content = self._render_template("package.json", {})
            (self.project_path / "package.json").write_text(content, encoding=DEFAULT_ENCODING)

            # uv.toml（如果使用uv）
            if self._should_use_uv():
                self._validate_template_exists("uv.toml")
                content = self._render_template("uv.toml", context)
                (self.project_path / "uv.toml").write_text(content, encoding=DEFAULT_ENCODING)
        except Exception as e:
            raise RuntimeError(f"生成测试文件失败: {e}") from e

        # .env.example
        try:
            self._validate_template_exists("env_example")
            content = self._render_template("env_example", {})
            (self.project_path / ".env.example").write_text(content, encoding=DEFAULT_ENCODING)
        except Exception as e:
            raise RuntimeError(f"生成 .env.example 失败: {e}") from e

    def _should_use_uv(self) -> bool:
        """
        检查是否应该使用uv

        Returns:
            如果系统安装了uv则返回True，否则返回False
        """
        has_uv = shutil.which("uv") is not None
        logger.debug(f"检查uv工具: {'已安装' if has_uv else '未安装'}")
        return has_uv

    def _generate_docs_files(self) -> None:
        """
        生成文档文件

        生成 API 文档、开发指南、部署指南等文档。
        """
        docs_dir = self.project_path / "docs"

        try:
            # API 文档
            self._validate_template_exists("docs_api.md")
            content = self._render_template("docs_api.md", {})
            (docs_dir / "api.md").write_text(content, encoding=DEFAULT_ENCODING)

            # 开发指南
            self._validate_template_exists("docs_development.md")
            content = self._render_template("docs_development.md", {})
            (docs_dir / "development.md").write_text(content, encoding=DEFAULT_ENCODING)

            # 部署指南
            self._validate_template_exists("docs_deployment.md")
            content = self._render_template("docs_deployment.md", {})
            (docs_dir / "deployment.md").write_text(content, encoding=DEFAULT_ENCODING)

        except Exception as e:
            logger.warning(f"生成文档文件失败: {e}")

    def _generate_other_files(self) -> None:
        """
        生成其他文件

        生成 requirements.txt、pyproject.toml、README.md、Dockerfile 等项目配置文件。
        """
        context = {
            "project_name": self.project_name,
            "db_type": self.db_type,
            "enable_redis": self.enable_redis,
            "enable_celery": self.enable_celery,
        }

        # requirements.txt
        # 根据选项生成不同的依赖
        db_deps_list = DB_DEPENDENCIES.get(self.db_type, DB_DEPENDENCIES[DEFAULT_DB_TYPE])
        db_deps = "\n".join(db_deps_list)
        redis_deps = REDIS_DEPENDENCY if self.enable_redis else ""

        context.update(
            {
                "redis_deps": redis_deps,
                "db_deps": db_deps,
            }
        )
        try:
            self._validate_template_exists("requirements.txt")
            content = self._render_template("requirements.txt", context)
            (self.project_path / "requirements.txt").write_text(content, encoding=DEFAULT_ENCODING)

            # pyproject.toml - 让项目可以独立创建虚拟环境
            self._validate_template_exists("pyproject.toml")
            content = self._render_template("pyproject.toml", context)
            (self.project_path / "pyproject.toml").write_text(content, encoding=DEFAULT_ENCODING)

            # runserver.py
            self._validate_template_exists("runserver.py")
            content = self._render_template("runserver.py", {})
            (self.project_path / "runserver.py").write_text(content, encoding=DEFAULT_ENCODING)

            # README.md
            self._validate_template_exists("README.md")
            content = self._render_template("README.md", context)
            (self.project_path / "README.md").write_text(content, encoding=DEFAULT_ENCODING)

            # .gitignore
            self._validate_template_exists("gitignore")
            content = self._render_template("gitignore", {})
            (self.project_path / ".gitignore").write_text(content, encoding=DEFAULT_ENCODING)

            # .dockerignore
            self._validate_template_exists("dockerignore")
            content = self._render_template("dockerignore", {})
            (self.project_path / ".dockerignore").write_text(content, encoding=DEFAULT_ENCODING)

            # Dockerfile
            self._validate_template_exists("Dockerfile")
            content = self._render_template("Dockerfile", context)
            (self.project_path / "Dockerfile").write_text(content, encoding=DEFAULT_ENCODING)

            # docker-compose.yaml
            self._validate_template_exists("docker_compose.yaml")
            content = self._render_template("docker_compose.yaml", context)
            (self.project_path / "docker-compose.yaml").write_text(content, encoding=DEFAULT_ENCODING)
        except Exception as e:
            raise RuntimeError(f"生成项目配置文件失败: {e}") from e
