# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **CHANGELOG.md**：新增版本变更记录文档，规范记录项目迭代历史
- **scripts/**：新增测试脚本目录，包含多个故事生成测试样例
- **guide file/**：新增学习指南和实验报告模板目录
- **tech-docs/**：新增技术文档目录，包含 API 文档和开发者文档

### Changed

- **文档结构重组**：将 `docs/` 目录下的文档迁移至 `tech-docs/`，清理冗余文档
- **README.md**：技术架构图改用 Mermaid 替代 ASCII 框图，提升可读性
- **requirements.txt**：更新依赖版本

### Fixed

- **数据丢失问题**：修复生成内容保存时大纲(outline)和角色(characters)数据永久丢失的问题
- **重复保存问题**：修复多次保存导致重复记录的问题，改为 upsert 模式
- **空字符串 ID 问题**：修复首次保存时 ID 为空字符串的问题
- **字数统计不准确**：修复中文故事字数统计偏低的问题
- **保存失败无反馈**：添加错误提示 toast，让用户及时了解保存状态
- **死代码清理**：移除无效的 polisher 状态检查
- **LLMClient 异步请求**：改用 httpx 实现真正的异步请求
- **并发数据损坏**：HistoryManager / WorkManager 加文件锁防并发数据损坏
- **API Key 更新**：修复 works.py 全局 LLMClient 不更新 API Key 的问题
- **API Key 安全**：清除测试脚本中硬编码的真实 API Key，替换为占位符

## [0.1.0] - 2026-07-XX

### Added

- **项目初始化**：TaleForge 智能故事生成器初始提交
- **多智能体架构**：实现 Planner、Character、Writer、Polisher 四个智能体协作
- **故事生成功能**：支持多种体裁、风格、字数的故事生成
- **前端界面**：Vue 3 + Tailwind CSS 单页应用
- **后端服务**：FastAPI + Uvicorn 后端服务
- **数据持久化**：JSON 文件存储故事和作品数据
- **一键启动器**：`start.py` 自动创建虚拟环境、安装依赖、配置 API Key