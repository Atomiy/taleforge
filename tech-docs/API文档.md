# TaleForge API 文档

基础地址：`http://127.0.0.1:8080/api/v1`

---

## 健康检查

```
GET /health
```

**响应**：`{"status": "ok", "timestamp": "..."}`

---

## 故事生成

```
POST /story/generate
```

使用 SSE (Server-Sent Events) 流式返回生成过程。

**请求体**：

```json
{
  "theme": "故事主题",
  "genre": "短篇小说",
  "style": "温馨",
  "length": 2000,
  "background": "故事背景描述",
  "perspective": "第三人称全知",
  "conflict": "人与人",
  "mood": "轻松愉快",
  "outline": "故事梗概",
  "characters": [{"name": "角色名", "identity": "身份", ...}],
  "api_key": "sk-xxx",
  "previous_story_id": "",
  "continuation_mode": "next_chapter",
  "world_setting": "世界观设定",
  "foreshadowings": ["伏笔1", "伏笔2"]
}
```

**SSE 事件格式**：

```
data: {"agent": "planner", "status": "running", "message": "正在策划故事大纲..."}
data: {"agent": "writer", "status": "writing", "data": "章节内容..."}
data: {"agent": "orchestrator", "status": "complete", "data": {"title": "故事标题", "content": "完整内容"}}
```

---

## 保存故事

```
POST /story/save
```

**请求体**：

```json
{
  "title": "故事标题",
  "content": "故事内容",
  "theme": "主题",
  "genre": "短篇小说",
  "style": "温馨",
  "world_setting": "世界观",
  "foreshadowings": ["伏笔1"],
  "previous_story_id": ""
}
```

**响应**：`{"success": true, "story_id": "abc12345"}`

---

## 获取故事详情

```
GET /story/{story_id}
```

**响应**：完整 Story 对象

---

## 获取历史记录

```
GET /history/
```

**查询参数**：

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页数量 |
| search | string | "" | 搜索关键词（标题/内容） |
| genre | string | "" | 按体裁筛选 |
| favorite | string | "" | "true" 仅显示收藏，"false" 仅显示未收藏 |

**响应**：

```json
{
  "stories": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "total_pages": 5
}
```

---

## 删除故事

```
DELETE /history/{story_id}
```

**响应**：`{"success": true}`

---

## 切换收藏状态

```
PUT /history/{story_id}/favorite
```

**响应**：

```json
{
  "story": {...},
  "favorite": true
}
```

---

## 更新故事内容

```
PUT /history/{story_id}
```

**请求体**（支持部分更新）：

```json
{
  "content": "新内容",
  "title": "新标题"
}
```

**响应**：更新后的完整 Story 对象

---

## 导出故事

```
GET /history/export/{story_id}?format=markdown
```

**format 参数**：`markdown` 或 `text`

**响应**：文件下载（Content-Type: text/markdown 或 text/plain）

---

## 保存 API Key

```
POST /config/api-key
```

**请求体**：

```json
{
  "api_key": "sk-xxx"
}
```

**响应**：`{"success": true, "message": "API Key saved"}`

---

## 作品管理

### 创建作品

```
POST /works/
```

**请求体**：

```json
{
  "title": "作品标题",
  "genre": "奇幻",
  "style": "史诗",
  "world_setting": "世界观设定",
  "outline": "故事大纲",
  "foreshadowings": ["伏笔1"]
}
```

**响应**：`{"work_id": "abc12345"}`

---

### 作品列表

```
GET /works/
```

**响应**：

```json
{
  "works": [
    {
      "id": "abc12345",
      "title": "铁血王座",
      "chapter_ids": ["story1", "story2"],
      "chapter_count": 2,
      ...
    }
  ]
}
```

---

### 作品详情（含章节内容）

```
GET /works/{work_id}
```

**响应**：

```json
{
  "work": { "title": "铁血王座", ... },
  "chapters": [
    { "id": "story1", "title": "第一章标题", "content": "内容...", "word_count": 1500 },
    { "id": "story2", "title": "第二章标题", "content": "内容...", "word_count": 1800 }
  ]
}
```

---

### 更新作品

```
PUT /works/{work_id}
```

**请求体**（支持部分更新）：

```json
{
  "title": "新标题",
  "summary": "内容概要"
}
```

**响应**：更新后的 Work 对象

---

### 删除作品

```
DELETE /works/{work_id}
```

**响应**：`{"success": true}`

---

### 添加章节

```
POST /works/{work_id}/chapters
```

**请求体**：`{"story_id": "故事ID"}`

**响应**：`{"success": true, "chapter_ids": [...]}`

---

### 删除章节

```
DELETE /works/{work_id}/chapters/{story_id}
```

**响应**：`{"success": true, "chapter_ids": [...]}`

---

### 生成内容概要

```
POST /works/{work_id}/summary
```

**请求体**：`{"summary": "概要内容"}`

**响应**：更新后的 Work 对象
