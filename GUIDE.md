# 水下微距画廊 — 维护指南

> 给未来的自己：当你有新的水下照片想加入画廊时，看这篇就够了。

---

## 🗺 架构概览

```
                    ┌─────────────────────┐
                    │  photos_metadata.json │ ← 唯一数据源
                    │  (data/)              │
                    └──────┬──────────────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
   gallery-data.js   stories-data.js   photo_kb.js
   (首页画廊)         (故事线)         (AI对话)
```

**核心原则**：`data/photos_metadata.json` 是唯一的真相来源。所有 web/ 下的 JS 文件都由它自动生成，**永远不要手动编辑**。

---

## ➕ 添加新照片（完整流程）

### 前提条件
- 照片已修图完成，放在 `/Volumes/IRIS/2026/已修图/` 目录下
- 外置硬盘已连接（或照片已拷贝到本机）

### 第一步：提取 EXIF 元数据

```bash
cd underwater-gallery
python scripts/extract_metadata.py
```

这会扫描 `/Volumes/IRIS/2026/已修图/` 下所有 JPG，提取拍摄日期、相机参数、光圈、ISO 等，写入 `data/photos_metadata.json`。

### 第二步：AI 物种识别

```bash
python scripts/tag_pipeline.py --api openrouter --limit 10
```

- `--api openrouter`：使用 OpenRouter API（推荐，目前用 Qwen VL 72B）
- `--limit 10`：先测试前 10 张，确认效果后再去掉 --limit 全量跑
- `--api manual`：如果你不确定 AI 结果，用这个模式手动标注

### 第三步：AI 诗意标题

```bash
python scripts/poetic_titles.py --api openrouter
```

为每张照片生成诗意标题（如「幽暗中的繁星」「深海烈焰之心」）。

### 第四步：生成 Web 图片

```bash
python scripts/generate_thumbnails.py
```

从原图生成两种尺寸：
- **缩略图**（400px）：`web/images/thumbnails/`，用于卡片网格
- **展示图**（1400px）：`web/images/full/`，用于 Lightbox 大图

### 第五步：生成 JS 数据文件

```bash
# 画廊数据 → index.html 使用
python scripts/data_to_js.py

# 故事线 → stories.html 使用
python scripts/build_stories.py

# AI 对话知识库 → 聊天功能使用
python scripts/build_photo_kb.py
```

---

## ⚡ 快速模式

如果你只加了少量新照片，且之前在 metadata 里已标注过：

```bash
# 只更新图片和 JS，跳过 AI 步骤
python scripts/rebuild.py --quick
```

这会执行：提取元数据 → 生成图片 → 生成 JS（跳过 AI 标注）。

---

## 🔄 一键全量构建

```bash
python scripts/rebuild.py
```

相当于依次运行：`extract → tag → poetic → thumbnails → data_to_js → stories → photo_kb`。

---

## 🧪 测试预览

```bash
cd web
python3 -m http.server 9876
```

浏览器打开 `http://localhost:9876/index.html`

---

## 📁 文件地图

| 文件 | 作用 | 手动编辑？ |
|------|------|:---:|
| `data/photos_metadata.json` | 唯一数据源，包含 EXIF + AI标签 + 图片路径 | ✅ 是 |
| `web/gallery-data.js` | 首页 PHOTOS 数组 | ❌ 自动生成 |
| `web/stories-data.js` | 故事线数据 | ❌ 自动生成 |
| `web/photo_kb.js` | AI 对话知识库 | ❌ 自动生成 |
| `web/index.html` | 首页 HTML | ✅ 是（只改布局） |
| `web/stories.html` | 故事页 HTML | ✅ 是（只改布局） |
| `web/gallery-i18n.js` | 多语言翻译表 | ✅ 是 |
| `web/gallery-themes.css` | 主题样式 | ✅ 是 |

---

## 🔧 常见问题

### Q: 新照片加了但首页不显示？
A: 确保跑了 `python scripts/data_to_js.py`，它会把 metadata 转成 `gallery-data.js`。

### Q: 故事页数量不对？
A: 跑 `python scripts/build_stories.py` 重新生成。注意：至少 3 张照片才构成一个时间线故事，至少 2 张才构成物种/色彩图鉴。

### Q: AI 标注不准怎么办？
A: 运行 `python scripts/tag_pipeline.py --manual` 进入交互式手动标注模式。

### Q: 换了新电脑，照片在外置硬盘上？
A: 修改 `scripts/extract_metadata.py` 顶部的 `PHOTO_DIR` 路径。如果照片不在手边但有 `photos_metadata.json` 和 `web/images/`，直接跑 `data_to_js.py` + `build_stories.py` + `build_photo_kb.py` 即可。

### Q: 想加新潜点的照片？
A: 修改 `scripts/extract_metadata.py` 中的 `KNOWN_LOCATION` 字典，以及 `scripts/tag_pipeline.py` 中的 `TULAMBEN_SPECIES_CONTEXT`（添加新潜点的常见物种）。

---

## 📝 版本历史

- **v2.1**（2026-05-24）：重构数据管线，消除 index.html 内联 JSON
  - 新增 `data_to_js.py`、`rebuild.py`
  - 修复 `build_stories.py` 缩略图路径 bug 和地点名称 bug
  - 新增本文档

---

_下次潜水回来，带上新照片，对着这篇跑一遍就好。_
