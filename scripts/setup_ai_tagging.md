# AI 视觉模型自动打标签 - 配置指南

## 方案选择

### 推荐方案：Claude Vision API
- **优点**：对生物识别准确率高，支持中文输出
- **费用**：约 $0.01-0.03/张（44张约 $0.5-1.5）
- **速度**：约 2-3秒/张

### 备选方案：GPT-4V
- **优点**：识别速度快
- **费用**：约 $0.01-0.02/张

---

## 配置步骤

### 1. 获取 API Key

**Claude Vision (Anthropic)**:
1. 访问 https://console.anthropic.com
2. 注册/登录
3. 创建 API Key
4. 复制保存（格式：`sk-ant-...`）

**GPT-4V (OpenAI)**:
1. 访问 https://platform.openai.com/api-keys
2. 创建 API Key
3. 复制保存（格式：`sk-...`）

---

### 2. 安装依赖

```bash
cd /Users/iris/WorkBuddy/20260524184406/underwater-gallery/scripts

# Claude Vision
pip install anthropic

# 或 GPT-4V
pip install openai
```

---

### 3. 运行自动打标签

#### 方式A：Claude Vision（推荐）

```bash
export ANTHROPIC_API_KEY="sk-ant-你的key"

python3 tag_pipeline.py \
  --api anthropic \
  --limit 44
```

#### 方式B：GPT-4V

```bash
export OPENAI_API_KEY="sk-你的key"

python3 tag_pipeline.py \
  --api openai \
  --limit 44
```

#### 方式C：分步测试（先跑5张试试）

```bash
export ANTHROPIC_API_KEY="sk-ant-你的key"

python3 tag_pipeline.py \
  --api anthropic \
  --limit 5
```

---

### 4. 标签字段说明

AI 会自动识别并填充：

| 字段 | 说明 | 示例 |
|------|------|------|
| `species_cn` | 中文俗名 | "安娜多彩海牛" |
| `species_latin` | 拉丁学名 | "Chromodoris annae" |
| `category` | 生物分类 | "海兔" / "鱼" / "虾" / "螃蟹" |
| `primary_colors` | 主色调 | ["蓝紫", "橙黄"] |
| `behavior` | 行为状态 | "游动" / "静止" / "进食" |
| `composition` | 构图类型 | "正面" / "侧面" / "特写" |
| `confidence` | 识别信心值 | 0.0-1.0 |

---

### 5. 标签完成后

重新生成画廊（注入新标签）：

```bash
cd /Users/iris/WorkBuddy/20260524184406/underwater-gallery

# 重新注入数据到 HTML
python3 scripts/inject_data.py
```

然后刷新浏览器即可看到标签！

---

## 常见问题

### Q: API 调用失败？
- 检查 API Key 是否正确
- 检查网络（可能需要代理）
- 检查账户余额是否充足

### Q: 识别不准确？
- 这是正常的，AI 对水下微距的识别率约 70-85%
- 可以在生成的 `photos_metadata.json` 中手动修正
- 运行 `python3 tag_pipeline.py --manual` 进行交互式修正

### Q: 想省钱？
- 先跑 `--limit 5` 测试效果
- 只对最满意的照片打标签
- 或者选择手动标注（更准确）

---

## 下一步：部署到 GitHub Pages

标签打完、画廊满意后，运行：

```bash
cd /Users/iris/WorkBuddy/20260524184406/underwater-gallery
bash scripts/deploy_github.sh
```

详细步骤见 `scripts/deploy_github.md`
