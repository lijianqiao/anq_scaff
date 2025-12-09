"""
模块生成器 - 用于添加新的API模块
"""

import logging
from pathlib import Path
from typing import Dict

from anq_scaff.template_engine import TemplateEngine

# 常量定义
DEFAULT_ENCODING = "utf-8"

# 配置日志记录器
logger = logging.getLogger(__name__)


class ModuleGenerator:
    """
    API模块生成器

    用于为现有项目添加新的API模块，包括API路由、Service、Model、Schema等文件。

    Attributes:
        module_name: 模块名称
        project_path: 项目路径
        version: API版本（默认: v1）
        template_engine: 模板引擎实例
    """

    def __init__(self, module_name: str, project_path: Path, version: str = "v1") -> None:
        """
        初始化模块生成器

        Args:
            module_name: 模块名称
            project_path: 项目路径
            version: API版本，格式应为 v1, v2 等
        """
        self.module_name = module_name
        self.project_path = project_path
        self.version = version
        self.template_engine = TemplateEngine()

    def generate(self) -> None:
        """
        生成API模块

        生成包括API路由、Service、Model、Schema在内的完整模块文件。

        Raises:
            ValueError: 如果项目路径无效或模板不存在
            RuntimeError: 如果文件生成失败
        """
        logger.info(f"开始生成API模块: {self.module_name} (版本: {self.version})")

        # 检查项目路径
        if not (self.project_path / "app").exists():
            error_msg = f"项目路径 '{self.project_path}' 不是有效的FastAPI项目"
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # 创建模块目录
            api_version_dir = self.project_path / "app" / "api" / self.version
            logger.debug(f"创建API版本目录: {api_version_dir}")
            api_version_dir.mkdir(parents=True, exist_ok=True)

            # 生成API路由文件
            logger.debug(f"生成API路由文件: {self.module_name}.py")
            self._generate_api_file(api_version_dir)

            # 生成Service文件
            logger.debug(f"生成Service文件: {self.module_name}.py")
            self._generate_service_file()

            # 生成Model文件
            logger.debug(f"生成Model文件: {self.module_name}.py")
            self._generate_model_file()

            # 生成Schema文件
            logger.debug(f"生成Schema文件: {self.module_name}.py")
            self._generate_schema_file()

            logger.info(f"API模块 '{self.module_name}' 生成成功")
        except Exception as e:
            logger.error(f"API模块生成失败: {e}", exc_info=True)
            raise

    def _get_context(self) -> Dict[str, str]:
        """
        获取模板上下文

        Returns:
            包含模块名称和类名的上下文字典
        """
        return {
            "module_name": self.module_name,
            "ModuleName": self.module_name.capitalize(),
        }

    def _generate_api_file(self, api_dir: Path) -> None:
        """
        生成API路由文件

        Args:
            api_dir: API版本目录路径

        Raises:
            RuntimeError: 如果模板不存在或文件写入失败
        """
        template_name = "api_module"  # 不带 .py 后缀
        if template_name not in self.template_engine.templates:
            raise ValueError(f"模板 '{template_name}' 不存在")

        context = self._get_context()
        content = self.template_engine.render(template_name, context)
        api_file = api_dir / f"{self.module_name}.py"
        api_file.write_text(content, encoding=DEFAULT_ENCODING)

    def _generate_service_file(self) -> None:
        """
        生成Service文件

        Raises:
            RuntimeError: 如果模板不存在或文件写入失败
        """
        template_name = "service_module"  # 不带 .py 后缀
        if template_name not in self.template_engine.templates:
            raise ValueError(f"模板 '{template_name}' 不存在")

        context = self._get_context()
        content = self.template_engine.render(template_name, context)

        # 确保 services 目录存在
        services_dir = self.project_path / "app" / "services"
        services_dir.mkdir(parents=True, exist_ok=True)

        service_file = services_dir / f"{self.module_name}.py"
        service_file.write_text(content, encoding=DEFAULT_ENCODING)

    def _generate_model_file(self) -> None:
        """
        生成Model文件

        Raises:
            RuntimeError: 如果模板不存在或文件写入失败
        """
        template_name = "model_module"  # 不带 .py 后缀
        if template_name not in self.template_engine.templates:
            raise ValueError(f"模板 '{template_name}' 不存在")

        context = self._get_context()
        content = self.template_engine.render(template_name, context)

        # 确保 models 目录存在
        models_dir = self.project_path / "app" / "models"
        models_dir.mkdir(parents=True, exist_ok=True)

        model_file = models_dir / f"{self.module_name}.py"
        model_file.write_text(content, encoding=DEFAULT_ENCODING)

    def _generate_schema_file(self) -> None:
        """
        生成Schema文件

        Raises:
            RuntimeError: 如果模板不存在或文件写入失败
        """
        template_name = "schema_module"  # 不带 .py 后缀
        if template_name not in self.template_engine.templates:
            raise ValueError(f"模板 '{template_name}' 不存在")

        context = self._get_context()
        content = self.template_engine.render(template_name, context)

        # 确保 schemas 目录存在
        schemas_dir = self.project_path / "app" / "schemas"
        schemas_dir.mkdir(parents=True, exist_ok=True)

        schema_file = schemas_dir / f"{self.module_name}.py"
        schema_file.write_text(content, encoding=DEFAULT_ENCODING)
