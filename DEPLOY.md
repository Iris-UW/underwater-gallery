# Deploy Guide — Iris Underwater Gallery

## 1. GitHub Pages (Gallery Hosting)

### One-time setup (Iris does this once):

```bash
# In the underwater-gallery/ folder:
git remote add origin https://github.com/Iris-UW/underwater-gallery.git
git branch -M main
git push -u origin main
```

Then in GitHub:
1. Go to `https://github.com/Iris-UW/underwater-gallery/settings/pages`
2. Source → **GitHub Actions**
3. Wait ~1 min → live at `https://iris-uw.github.io/underwater-gallery/`

---

## 2. Cloudflare Worker (Chat Backend)

The chat feature needs a CORS-enabled proxy to call OpenRouter (API key must not be exposed).

### One-time setup:

```bash
# Install Wrangler CLI
npm install -g wrangler

# Log in to Cloudflare
wrangler login

# Set your OpenRouter API key as a secret (never commit it!)
wrangler secret put OPENROUTER_KEY
# ↑ paste your sk-or-v1-... key when prompted

# Deploy the worker
cd worker/
wrangler deploy
# ↑ copies the worker URL from output, e.g.:
#   https://iris-uw-chat.your-subdomain.workers.dev
```

### Update the chat API URL:

Edit `web/chat.js`, line ~3:
```js
apiUrl: 'https://iris-uw-chat.your-subdomain.workers.dev/api/chat',
```

Then commit & push:
```bash
git add web/chat.js
git commit -m "config: point chat to CF Worker"
git push
```

---

## 3. Add New Photos (百度网盘 import)

After you download photos from Baidu Netdisk to a local folder:

```bash
cd underwater-gallery

# 1. Put new .jpg/.arw/.cr3 files into a folder, e.g. data/new_photos/

# 2. Run the pipeline:
python3 scripts/extract_metadata.py data/new_photos/   # extract EXIF
python3 scripts/generate_thumbnails.py data/new_photos/  # make webp + thumbnails
python3 scripts/tag_pipeline.py --api openrouter  # AI tag new photos
python3 scripts/poetic_titles.py --api openrouter  # generate poetic titles
python3 scripts/build_stories.py   # rebuild story lines
python3 scripts/build_photo_kb.py    # rebuild chat knowledge base

# 3. Inject updated data into HTML:
# (already done by build_stories.py and build_photo_kb.py)

# 4. Commit & push
git add web/
git commit -m "feat: add new photos"
git push
```

---

## File Structure

```
underwater-gallery/
├── data/
│   ├── photos_metadata.json   # ← master data (44+ photos)
│   └── stories.json           # ← story line definitions
├── scripts/
│   ├── extract_metadata.py
│   ├── generate_thumbnails.py
│   ├── tag_pipeline.py
│   ├── poetic_titles.py
│   ├── build_stories.py
│   └── build_photo_kb.py    # ← rebuilds chat KB
├── web/                       # ← GitHub Pages serves THIS folder
│   ├── index.html
│   ├── stories.html
│   ├── chat.css
│   ├── chat.js
│   ├── photo_kb.js            # ← auto-generated
│   ├── stories-data.js
│   ├── images/
│   │   ├── full/               # ← optimized webp (served by GH Pages)
│   │   └── thumbnails/        # ← small previews
│   └── ...
├── worker/
│   ├── index.js               # ← Cloudflare Worker
│   └── wrangler.toml
└── .github/workflows/
    └── deploy.yml             # ← auto-deploy on git push
```
