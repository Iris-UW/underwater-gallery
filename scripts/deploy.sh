#!/bin/bash
# 一键部署到 GitHub Pages
# 用法：bash scripts/deploy.sh [仓库名]
# 示例：bash scripts/deploy.sh underwater-macro

set -e

REPO_NAME=${1:-underwater-macro}
WEB_DIR="$(cd "$(dirname "$0")/../web" && pwd)"
TEMP_DIR=$(mktemp -d)

echo "🚀 开始部署到 GitHub Pages..."
echo "   仓库名：$REPO_NAME"
echo ""

# 检查 gh CLI
if ! command -v gh &> /dev/null; then
    echo "❌ 未安装 GitHub CLI"
    echo "   请先安装：brew install gh"
    echo "   或手动部署，见 scripts/deploy_github.md"
    exit 1
fi

# 检查 gh 登录状态
if ! gh auth status &> /dev/null; then
    echo "❌ 未登录 GitHub"
    echo "   请先运行：gh auth login"
    exit 1
fi

# 获取用户名
USERNAME=$(gh api user --jq '.login')
echo "✅ GitHub 用户：$USERNAME"
echo ""

# 创建仓库（如果不存在）
echo "📦 创建仓库 $REPO_NAME..."
gh repo create "$REPO_NAME" --public --source=. --push 2>/dev/null || echo "   (仓库已存在，跳过创建)"

# 进入临时目录，准备部署内容
echo "📁 准备部署文件..."
cp -R "$WEB_DIR"/* "$TEMP_DIR/"
cd "$TEMP_DIR"

# 初始化 git 并推送
echo "📤 推送到 GitHub..."
git init
git add .
git commit -m "Deploy: underwater macro gallery"
git branch -M main
git remote add origin "https://github.com/$USERNAME/$REPO_NAME.git"
git push -u origin main --force

# 启用 GitHub Pages
echo "⚙️  启用 GitHub Pages..."
gh repo edit "$USERNAME/$REPO_NAME" --enable-pages --pages-source-branch main --pages-source-path "/"

echo ""
echo "✅ 部署完成！"
echo ""
echo "🌐 你的画廊地址："
echo "   https://$USERNAME.github.io/$REPO_NAME/"
echo ""
echo "⏳ 请等待 2-3 分钟，GitHub Pages 需要时间构建"
echo ""
echo "💡 提示："
echo "   - 每次更新后，重新运行此脚本即可"
echo "   - 或手动推送：cd $TEMP_DIR && git add . && git commit -m 'update' && git push"
