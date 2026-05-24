/* ============================================
   AI Chat — Iris Underwater Gallery
   Persona: Iris (the photographer) answers as herself
   ============================================ */

const CHAT_CONFIG = {
  // Cloudflare Worker URL — update after deploying worker
  apiUrl: '/api/chat',          // relative = same domain (GH Pages + CF Worker route)
  // Fallback: use OpenRouter directly (dev only, exposes key)
  openrouterKey: '',             // set only for local dev
  model: 'qwen/qwen2.5-vl-72b-instruct',
};

// ── State ──
let chatOpen = false;
let chatHistory = [];          // [{role, content}]

// ── i18n copy ──
const CHAT_I18N = {
  en: {
    header: 'Ask Iris',
    status_online: 'Online · answers as Iris',
    status_typing: 'Iris is typing…',
    placeholder: 'Ask about the photos, marine life, diving…',
    suggested: ['Tell me about this nudibranch', 'What camera do you use?', 'Best dive site in Bali?', 'How do you light macro shots?'],
    welcome: "Hi! I'm Iris. I shot all the photos in this gallery during my February 2026 trip to Tulamben, Bali. Feel free to ask me anything about the critters, the dive sites, or underwater photography — I'd love to share!",
  },
  zh: {
    header: '问问 Iris',
    status_online: '在线 · 以 Iris 的身份回答',
    status_typing: 'Iris 正在输入…',
    placeholder: '问关于照片、海洋生物、潜水的问题…',
    suggested: ['给我讲讲这只海兔', '你用什么相机？', '巴厘岛最好的潜点？', '水下微距怎么打光？'],
    welcome: '嗨！我是 Iris。这个画廊里所有的照片，都是我 2026 年 2 月在巴厘岛图蓝本潜水时拍的。随便问我关于这些小生物、潜点、或者水下摄影的问题吧 — 我很乐意分享！',
  },
  ja: {
    header: 'Iris に聞く',
    status_online: 'オンライン · Iris として答える',
    status_typing: 'Iris が入力中…',
    placeholder: '写真、海の生き物、ダイビングについて聞いて…',
    suggested: ['このウミウシについて教えて', 'どんなカメラを使ってる？', 'バリで一番のダイブサイトは？', 'マクロ撮影のライティングは？'],
    welcome: 'こんにちは！Irisです。このギャラリーのすべての写真は、2026年2月にバリ島トゥランベンで撮影したものです。生き物やダイブサイト、水中マクロ撮影について、何でも聞いてください — お答えします！',
  },
};

function getLang() {
  return (localStorage.getItem('iris-lang') || 'en');
}

// ── Build photo knowledge base from pre-built JS variable ──
function getPhotoKB() {
  if (typeof PHOTO_KB !== 'undefined') return PHOTO_KB;
  // Fallback: build from PHOTOS array if available
  if (typeof PHOTOS === 'undefined') return '';
  const lines = PHOTOS.map((p, i) => {
    const t = p.ai_tags || {};
    return `#${i+1} ${t.species_cn || '?'}${t.species_latin ? ' (' + t.species_latin + ')' : ''} — ${t.category || '?'} — ${p.date || '?'} — ${t.poetic_title || ''} — f/${p.f_number} ISO${p.iso}`;
  });
  return lines.join('\n');
}

// ── Inject chat UI into page ──
function injectChatUI() {
  // Already injected?
  if (document.getElementById('chatFab')) return;

  // Fab button
  const fab = document.createElement('button');
  fab.id = 'chatFab';
  fab.className = 'chat-fab';
  fab.innerHTML = `<span class="pulse-ring"></span><span>💬</span>`;
  fab.setAttribute('aria-label', 'Chat with Iris');
  fab.onclick = toggleChat;
  document.body.appendChild(fab);

  // Panel
  const panel = document.createElement('div');
  panel.id = 'chatPanel';
  panel.className = 'chat-panel';
  panel.innerHTML = `
    <div class="chat-header">
      <div class="avatar">I</div>
      <div class="info">
        <div class="name" data-chat="header">Ask Iris</div>
        <div class="status" data-chat="status">Online · answers as Iris</div>
      </div>
      <button class="close-btn" id="chatCloseBtn">✕</button>
    </div>
    <div class="chat-messages" id="chatMessages"></div>
    <div class="chat-suggestions" id="chatSuggestions"></div>
    <div class="chat-input-area">
      <textarea id="chatInput" rows="1" placeholder="Ask about the photos, marine life, diving…"></textarea>
      <button class="send-btn" id="chatSendBtn">➤</button>
    </div>`;
  document.body.appendChild(panel);

  // Events
  document.getElementById('chatCloseBtn').onclick = toggleChat;
  document.getElementById('chatSendBtn').onclick = sendMessage;
  const input = document.getElementById('chatInput');
  input.addEventListener('input', autoResizeTextarea);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
  });

  updateChatI18n();
  showSuggestions();
}

function autoResizeTextarea(e) {
  const el = e.target;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 100) + 'px';
}

// ── Toggle ──
function toggleChat() {
  chatOpen = !chatOpen;
  document.getElementById('chatFab').classList.toggle('open', chatOpen);
  document.getElementById('chatPanel').classList.toggle('open', chatOpen);
  if (chatOpen && chatHistory.length === 0) {
    addMessage('iris', CHAT_I18N[getLang()].welcome, true);
  }
  if (chatOpen) {
    const input = document.getElementById('chatInput');
    input.focus();
    scrollChatToBottom();
  }
}

// ── i18n update ──
function updateChatI18n() {
  const lang = getLang();
  const t = CHAT_I18N[lang] || CHAT_I18N.en;
  const panel = document.getElementById('chatPanel');
  if (!panel) return;
  panel.querySelector('[data-chat="header"]').textContent = t.header;
  panel.querySelector('[data-chat="status"]').textContent = t.status_online;
  panel.querySelector('#chatInput').placeholder = t.placeholder;
  // Refresh suggestions if visible
  const sugg = document.getElementById('chatSuggestions');
  if (sugg && sugg.children.length > 0) showSuggestions();
}

// ── Suggestions ──
function showSuggestions() {
  const lang = getLang();
  const t = CHAT_I18N[lang] || CHAT_I18N.en;
  const container = document.getElementById('chatSuggestions');
  if (!container) return;
  container.innerHTML = t.suggested.map(s =>
    `<button class="chat-chip" data-msg="${s.replace(/"/g, '&quot;')}">${s}</button>`
  ).join('');
  container.querySelectorAll('.chat-chip').forEach(btn => {
    btn.onclick = () => {
      const msg = btn.dataset.msg;
      document.getElementById('chatInput').value = msg;
      sendMessage();
    };
  });
}

// ── Messages ──
function addMessage(role, content, isWelcome) {
  const container = document.getElementById('chatMessages');
  const lang = getLang();
  const t = CHAT_I18N[lang] || CHAT_I18N.en;
  const msg = document.createElement('div');
  msg.className = `chat-msg ${role}`;
  const meta = role === 'iris'
    ? (isWelcome ? 'Iris · ' + (lang === 'zh' ? '摄影师' : lang === 'ja' ? '写真家' : 'Photographer') : 'Iris')
    : (lang === 'zh' ? '你' : lang === 'ja' ? 'あなた' : 'You');
  msg.innerHTML = `<div class="meta">${meta}</div><div>${escapeHTML(content).replace(/\n/g, '<br>')}</div>`;
  container.appendChild(msg);
  scrollChatToBottom();
  return msg;
}

function showTyping() {
  const container = document.getElementById('chatMessages');
  const existing = document.getElementById('chatTyping');
  if (existing) return;
  const el = document.createElement('div');
  el.className = 'chat-typing';
  el.id = 'chatTyping';
  el.innerHTML = '<span></span><span></span><span></span>';
  container.appendChild(el);
  scrollChatToBottom();
}

function removeTyping() {
  const el = document.getElementById('chatTyping');
  if (el) el.remove();
}

function scrollChatToBottom() {
  const container = document.getElementById('chatMessages');
  if (container) container.scrollTop = container.scrollHeight;
}

function escapeHTML(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── Send ──
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  // Clear suggestions
  document.getElementById('chatSuggestions').innerHTML = '';

  // Show user message
  addMessage('visitor', text);
  chatHistory.push({ role: 'user', content: text });
  input.value = '';
  input.style.height = 'auto';

  // Disable input
  const sendBtn = document.getElementById('chatSendBtn');
  sendBtn.disabled = true;
  input.disabled = true;

  // Show typing
  const lang = getLang();
  const t = CHAT_I18N[lang] || CHAT_I18N.en;
  document.querySelector('[data-chat="status"]').textContent = t.status_typing;
  showTyping();

  try {
    const reply = await callAPI(text);
    removeTyping();
    document.querySelector('[data-chat="status"]').textContent = t.status_online;
    addMessage('iris', reply);
    chatHistory.push({ role: 'assistant', content: reply });
  } catch (err) {
    removeTyping();
    document.querySelector('[data-chat="status"]').textContent = t.status_online;
    const errMsg = lang === 'zh' ? '抱歉，出了点问题，请再试一次。' : lang === 'ja' ? 'すみません、エラーが発生しました。もう一度お試しください。' : 'Sorry, something went wrong. Please try again.';
    addMessage('iris', errMsg);
  } finally {
    sendBtn.disabled = false;
    input.disabled = false;
    input.focus();
  }
}

// ── API Call ──
async function callAPI(userMessage) {
  const lang = getLang();
  const photoKB = getPhotoKB();

  const systemPrompt = `You are Iris — a passionate underwater macro photographer. You are warm, poetic, and knowledgeable about marine life. You answer visitors' questions as YOURSELF (first person).

CRITICAL RULES:
- Never say "As an AI" — you ARE Iris, a real person and photographer
- Answer in ${lang === 'zh' ? 'Chinese (Simplified)' : lang === 'ja' ? 'Japanese' : 'English'}
- Be conversational, warm, not too long (2-4 sentences is often enough)
- If asked about a specific photo, reference the poetic title and species info from the gallery data
- Share your personal diving experience from Tulamben, Bali (Feb 14-22, 2026)
- You shoot with Olympus E-M1 II (60mm F2.8 Macro) and Sony A7R IV (90mm F2.8 Macro G OSS)
- If you don't know something, say so warmly ("I haven't encountered that yet, but here's what I do know...")

YOUR GALLERY DATA (${photoKB.split('\n').length} photos, Feb 14-22, 2026, Tulamben Bali):
${photoKB}

When relevant, mention specific photos by their poetic title.`;

  const messages = [
    { role: 'system', content: systemPrompt },
    ...chatHistory.slice(-8),   // last 8 messages for context
    { role: 'user', content: userMessage },
  ];

  // Try Cloudflare Worker first (production)
  const apiUrl = CHAT_CONFIG.apiUrl;

  try {
    const res = await fetch(apiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });
    if (res.ok) {
      const data = await res.json();
      return data.choices?.[0]?.message?.content || '(no response)';
    }
    // If worker fails, try direct OpenRouter (dev only, needs key)
    if (CHAT_CONFIG.openrouterKey) {
      return await callOpenRouterDirect(messages);
    }
    throw new Error('API call failed: ' + res.status);
  } catch (err) {
    if (CHAT_CONFIG.openrouterKey) {
      return await callOpenRouterDirect(messages);
    }
    throw err;
  }
}

async function callOpenRouterDirect(messages) {
  const res = await fetch('https://openrouter.ai/api/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${CHAT_CONFIG.openrouterKey}`,
      'Content-Type': 'application/json',
      'HTTP-Referer': 'https://iris-uw.github.io',
      'X-Title': 'Iris Underwater Chat',
    },
    body: JSON.stringify({
      model: CHAT_CONFIG.model,
      messages,
      max_tokens: 600,
      temperature: 0.85,
    }),
  });
  const data = await res.json();
  return data.choices?.[0]?.message?.content || '(no response)';
}

// ── Init: watch for lang changes + inject UI ──
(function initChat() {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectChatUI);
  } else {
    injectChatUI();
  }

  // Re-check lang on storage change (multi-tab) and on focus
  window.addEventListener('focus', () => {
    if (document.getElementById('chatPanel')) updateChatI18n();
  });
})();
