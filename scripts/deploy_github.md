# 部署到 GitHub Pages — 完整指南

## 前置准备

### 1. 安装 GitHub CLI（推荐）

```bash
# macOS
brew install gh

# 或下载：https://cli.github.com/
```

### 2. 登录 GitHub

```bash
gh auth login
# 按提示操作（浏览器授权）
```

---

## 一键部署（推荐）

### 方式A：使用自动脚本

```bash
cd /Users/iris/WorkBuddy/20260524184406/underwater-gallery

bash scripts/deploy_github.sh
```

脚本会自动：
1. 创建 GitHub 仓库（如 `underwater-macro`）
2. 推送代码
3. 启用 GitHub Pages
4. 返回你的公开访问链接

---

### 方式B：手动操作

#### 步骤1：在 GitHub 创建新仓库
1. 访问 https://github.com/new
2. 仓库名：`underwater-macro`（或其他喜欢的名字）
3. **不要**勾选 "Initialize with README"
4. 点击 "Create repository"

#### 步骤2：推送代码

```bash
cd /Users/iris/WorkBuddy/20260524184406/underwater-gallery

# 初始化 git
git init
git add .
git commit -m "Initial commit: underwater macro gallery"

# 关联远程仓库（替换 USERNAME 和 REPO_NAME）
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

#### 步骤3：启用 GitHub Pages
1. 进入仓库页面
2. 点击 "Settings"
3. 左侧菜单找到 "Pages"
4. Source 选择 "Deploy from a branch"
5. Branch 选择 `main` 和 `/ (root)`
6. 点击 Save

#### 步骤4：访问你的画廊！

几分钟后，访问：
```
https://USERNAME.github.io/REPO_NAME/
```

---

## 自定义域名（可选）

如果想用自己域名（如 `gallery.yourdomain.com`）：

1. 在域名服务商添加 CNAME 记录：
   ```
   类型：CNAME
   名称：gallery
   值：USERNAME.github.io.
   ```

2. 在 `web/` 目录下创建 `CNAME` 文件：
   ```bash
   echo "gallery.yourdomain.com" > web/CNAME
   ```

3. 在 GitHub 仓库 Settings > Pages > Custom domain 填写域名

---

## 更新画廊

每次修改后，重新注入数据并推送：

```bash
cd /Users/iris/WorkBuddy/20260524184406/underwater-gallery

# 重新注入数据（如果照片元数据有更新）
python3 scripts/inject_data.py

# 推送更新
git add .
git commit -m "Update gallery"
git push
```

---

## 常见问题

### Q: 页面显示 404？
- 检查仓库是否为**公开**（Private 仓库需要 GitHub Pro 才能用 Pages）
- 检查 `index.html` 是否在根目录
- 等待 2-3 分钟，GitHub Pages 需要时间构建

### Q: 图片加载不出来？
- 检查 `images/` 目录是否正确推送
- 检查 `index.html` 中的图片路径是否为相对路径

### Q: 想绑定自己的域名？
- 见上方「自定义域名」章节

---

## 费用

✅ **完全免费**
- GitHub Pages：免费
- 带宽：无限
- 存储空间：1GB（对44张压缩后的照片绰绰有余）

---

## 下一步

部署成功后，可以：
1. 在小红书分享链接
2. 生成二维码方便手机访问
3. 添加 Google Analytics 统计访问量
