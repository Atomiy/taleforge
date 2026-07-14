# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **数据丢失问题**：修复生成内容保存时大纲(outline)和角色(characters)数据永久丢失的问题。前端现在从 SSE `complete` 事件中完整提取所有字段，并在保存时传递给后端。
- **重复保存问题**：修复多次保存导致重复记录的问题。`HistoryManager.save_story()` 改为 upsert 模式（存在则更新，不存在则插入），前端保存时传递已保存的故事 ID。
- **空字符串 ID 问题**：修复首次保存时 ID 为空字符串的问题。后端改为 `story_data.get("id") or generate_id()`，确保空值时自动生成 UUID。
- **字数统计不准确**：修复中文故事字数统计偏低的问题。改用 `_calculate_word_count()` 方法，正确区分中文字符和英文单词。
- **保存失败无反馈**：修复保存失败时用户无感知的问题。添加错误提示 toast，让用户及时了解保存状态。
- **死代码清理**：移除 `polisher && status === 'writing'` 的无效检查，该分支永远不会触发。