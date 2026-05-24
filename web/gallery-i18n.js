/* ============================================
   Gallery i18n — Species, categories, labels
   Used by both index.html and stories.html
   ============================================ */

const GALLERY_I18N = {

  /* ── Species Chinese → English/Japanese ── */
  species: {
    '橙色海兔，疑似Flabellina属': { en: 'Orange Nudibranch (Flabellina sp.)', ja: 'オレンジ色のウミウシ（Flabellina属）' },
    '疑似橙色海兔': { en: 'Orange Nudibranch', ja: 'オレンジ色のウミウシ' },
    '橙色海兔，疑似Chromodoris属': { en: 'Orange Nudibranch (Chromodoris sp.)', ja: 'オレンジ色のウミウシ（Chromodoris属）' },
    '未知海兔，疑似Flabellina属': { en: 'Unknown Nudibranch (Flabellina sp.)', ja: '不明なウミウシ（Flabellina属）' },
    '疑似古巴纳海牛': { en: 'Nembrotha kubaryana (probable)', ja: 'Nembrotha kubaryana（推定）' },
    '橙色海兔': { en: 'Orange Nudibranch', ja: 'オレンジ色のウミウシ' },
    '疑似橙色海兔（疑似Chromodoris属）': { en: 'Orange Nudibranch (Chromodoris sp.)', ja: 'オレンジ色のウミウシ（Chromodoris属）' },
    '翅膀海牛': { en: 'Flabellina Nudibranch', ja: 'Flabellina ウミウシ' },
    '疑似翅膀海牛': { en: 'Flabellina Nudibranch (probable)', ja: 'Flabellina ウミウシ（推定）' },
    '翅膀海牛（Flabellina 属（疑似））': { en: 'Flabellina Nudibranch', ja: 'Flabellina ウミウシ' },
    '黑斑鸠海牛': { en: 'Jorunna funebris', ja: 'Jorunna funebris' },
    '安娜多彩海牛': { en: "Anna's Chromodoris", ja: 'Chromodoris annae' },
    '古巴纳海牛': { en: 'Nembrotha kubaryana', ja: 'Nembrotha kubaryana' },
    '紫海牛': { en: 'Hypselodoris bullocki', ja: 'Hypselodoris bullocki' },
    '疑似伊丽莎白多彩海牛': { en: "Elisabeth's Chromodoris (probable)", ja: 'Chromodoris elisabethina（推定）' },
    '疑似丘疹叶海牛': { en: 'Phyllidiella pustulosa (probable)', ja: 'Phyllidiella pustulosa（推定）' },
    '软珊瑚蟹': { en: 'Soft Coral Crab (Hoplophrys oatesi)', ja: 'ソフトコーラルクラブ（Hoplophrys oatesi）' },
    '疑似瓷蟹': { en: 'Porcelain Crab (probable)', ja: 'カニダマシ（推定）' },
    '帝王虾': { en: 'Emperor Shrimp', ja: 'エンペラーシュリンプ' },
    '海葵虾': { en: 'Anemone Shrimp', ja: 'イソギンチャクエビ' },
    '虾虎鱼': { en: 'Goby', ja: 'ハゼ' },
    '海洋生物（疑似虾虎鱼）': { en: 'Marine Life (prob. Goby)', ja: '海洋生物（ハゼ推定）' },
    '无法确定具体物种': { en: 'Unidentified Species', ja: '未確認種' },
    '不确定的箱鲀': { en: 'Boxfish (probable)', ja: 'ハコフグ（推定）' },
    '青蛙鱼': { en: 'Frogfish', ja: 'カエルアンコウ' },
    '黑双锯鱼': { en: 'Blackfoot Anemonefish', ja: 'クマノミ（Amphiprion nigripes）' },
    '不确定，可能是软珊瑚或其他': { en: 'Soft Coral / Unknown', ja: 'ソフトコーラル／不明' },
    '未能确定具体类别': { en: 'Unidentified', ja: '未確認' },
    '疑似苔藓虫': { en: 'Hydroid (probable)', ja: 'ヒドロ虫（推定）' },
  },

  /* ── Categories ── */
  categories: {
    '海兔': { en: 'Nudibranch', ja: 'ウミウシ' },
    '鱼': { en: 'Fish', ja: '魚' },
    '虾': { en: 'Shrimp', ja: 'エビ' },
    '螃蟹': { en: 'Crab', ja: 'カニ' },
    '其他': { en: 'Other', ja: 'その他' },
  },

  /* ── Behaviors ── */
  behaviors: {
    '静止': { en: 'Resting', ja: '静止' },
    '伪装': { en: 'Camouflage', ja: '擬態' },
    '产卵': { en: 'Spawning', ja: '産卵' },
    '栖息在海葵中，与海葵共生': { en: 'Hosted in anemone', ja: 'イソギンチャクと共生' },
  },

  /* ── Colors ── */
  colors: {
    '半透明白': { en: 'Translucent', ja: '半透明' },
    '橙色': { en: 'Orange', ja: 'オレンジ' },
    '橙黄': { en: 'Orange-Yellow', ja: '橙黄色' },
    '粉红': { en: 'Pink', ja: 'ピンク' },
    '红色': { en: 'Red', ja: '赤' },
    '荧光红': { en: 'Fluorescent Red', ja: '蛍光レッド' },
    '白色': { en: 'White', ja: '白' },
    '墨黑': { en: 'Jet Black', ja: '漆黒' },
    '黑色': { en: 'Black', ja: '黒' },
    '蓝紫': { en: 'Blue-Purple', ja: '青紫' },
    '荧光紫': { en: 'Fluorescent Purple', ja: '蛍光パープル' },
    '紫红': { en: 'Purple-Red', ja: '紫紅' },
    '荧光橙': { en: 'Fluorescent Orange', ja: '蛍光オレンジ' },
    '荧光黄': { en: 'Fluorescent Yellow', ja: '蛍光イエロー' },
    '黄色': { en: 'Yellow', ja: '黄色' },
    '绿色': { en: 'Green', ja: '緑' },
    '蓝色': { en: 'Blue', ja: '青' },
    '淡蓝': { en: 'Pale Blue', ja: '淡青' },
    '棕色': { en: 'Brown', ja: '茶色' },
    '红褐': { en: 'Red-Brown', ja: '赤褐色' },
    '金黄': { en: 'Gold', ja: '金色' },
    '紫色': { en: 'Purple', ja: '紫' },
  },

  /* ── Composition ── */
  compositions: {
    '特写': { en: 'Close-up', ja: 'クローズアップ' },
    '正面': { en: 'Frontal', ja: '正面' },
    '侧面': { en: 'Side view', ja: '側面' },
    '俯视': { en: 'Top-down', ja: '俯瞰' },
  },

  /* ── Poetic Titles (42 unique) ── */
  poeticTitles: {
    '珊瑚上的晨曦': { en: 'Coral Dawn', ja: '珊瑚の夜明け' },
    '幽暗中的繁星': { en: 'Stars in the Abyss', ja: '暗闇の星々' },
    '幽暗中的红宝石': { en: 'Ruby in the Deep', ja: '深海のルビー' },
    '幽暗中的触须': { en: 'Tendrils of Darkness', ja: '暗がりの触手' },
    '幽影与霓虹': { en: 'Shadows & Neon', ja: '影と霓虹' },
    '星点绽放': { en: 'Stardust Bloom', ja: '星屑の開花' },
    '紫翼幻影': { en: 'Purple Wing Mirage', ja: '紫翼の幻影' },
    '夜影之光': { en: 'Light in Night\'s Shadow', ja: '夜影の光' },
    '暗蓝之舞': { en: 'Dark Blue Dance', ja: '暗藍の舞' },
    '黑星凝视': { en: 'Black Star Gaze', ja: '黒星の凝視' },
    '珊瑚巢里的宝玉': { en: 'Gem in a Coral Nest', ja: '珊瑚の巣の宝玉' },
    '珊瑚花园的守望者': { en: 'Guardian of the Coral Garden', ja: '珊瑚庭園の守護者' },
    '透明之舞': { en: 'Translucent Dance', ja: '透明の舞' },
    '红白舞者的邂逅': { en: 'Red & White Encounter', ja: '紅白の踊り子の邂逅' },
    '深海的印记': { en: 'Mark of the Deep', ja: '深海の刻印' },
    '暗夜之花': { en: 'Nocturnal Bloom', ja: '闇夜の花' },
    '月夜轻咏': { en: 'Moonlit Whisper', ja: '月夜の詠唱' },
    '夜色中的金色梦': { en: 'A Gilded Dream in Night', ja: '夜色の金色の夢' },
    '水下梦境的轮廓': { en: 'Silhouette of an Underwater Dream', ja: '水中夢の輪郭' },
    '焕彩 whispers': { en: 'Radiant Whispers', ja: '光彩の囁き' },
    '幽光藏影': { en: 'Hidden in Bioluminescence', ja: '幽光に隠れて' },
    '晨光中的柔羽': { en: 'Soft Feathers at Dawn', ja: '朝光の柔羽' },
    '橙影轻舞': { en: 'Orange Shadow Dance', ja: '橙影の軽やかな舞' },
    '深海烈焰之心': { en: 'Heart of Deep-Sea Flame', ja: '深海の焔の心' },
    '橙色面具': { en: 'Orange Mask', ja: 'オレンジの仮面' },
    '深渊之瞳': { en: 'Eye of the Abyss', ja: '深淵の瞳' },
    '金色沉思': { en: 'Golden Contemplation', ja: '金色の瞑想' },
    '幽光之舞': { en: 'Bioluminescent Dance', ja: '幽光の舞' },
    '幽光羽翼': { en: 'Wings of Bioluminescence', ja: '幽光の羽根' },
    '暗夜之烛': { en: 'Candle in the Dark', ja: '闇夜の灯火' },
    '金色梦游者': { en: 'Golden Sleepwalker', ja: '金色の夢遊者' },
    '蓝夜的秘密': { en: 'Secret of the Blue Night', ja: '青夜の秘密' },
    '深蓝之眸': { en: 'Deep Blue Gaze', ja: '深青の眸' },
    '点点星光的追寻': { en: 'Chasing Starlight', ja: '星明かりを追って' },
    '粉红幕后的两个梦境': { en: 'Two Dreams Behind Pink Curtains', ja: 'ピンクの幕裏の二つの夢' },
    '红色梦境里的灵魂': { en: 'Soul in a Crimson Dream', ja: '紅い夢の中の魂' },
    '深渊中的画家': { en: 'Painter of the Abyss', ja: '深淵の画家' },
    '溶洞深处的守望者': { en: 'Watcher in the Deep Cavern', ja: '洞窟の奥の見守り者' },
    '橙色韵律的舞者': { en: 'Dancer of Orange Rhythm', ja: 'オレンジの律動の踊り子' },
    'Amber Whisper': { en: 'Amber Whisper', ja: '琥珀の囁き' },
    '金色穹顶下的隐者': { en: 'Hermit Under a Golden Dome', ja: '金色の穹頂の下の隠者' },
  },

  /* ── Static UI labels ── */
  ui: {
    gallery: { en: 'Gallery', zh: '画廊', ja: 'ギャラリー' },
    stories: { en: 'Stories', zh: '故事', ja: '物語' },
    admin: { en: 'Admin', zh: '管理', ja: '管理' },
    scroll: { en: 'Scroll', zh: '滑动', ja: 'スクロール' },
    collection: { en: 'The Collection', zh: '藏品集', ja: 'コレクション' },
    moments: { en: '44 Moments Beneath', zh: '水下 · 四十四瞬', ja: '水中の四十四の瞬間' },
    deeper: { en: 'Deeper', zh: '更深处', ja: 'より深く' },
    macro: { en: 'Macro Cosmos', zh: '微距宇宙', ja: 'マクロの宇宙' },
    footer_desc_en: { en: 'Underwater Macro Photography\nTulamben, Bali · 2026', zh: '水下微距摄影作品集\n图蓝本，巴厘岛 · 2026', ja: '水中マクロ写真集\nトゥランベン、バリ島 · 2026' },
    copyright: { en: 'All Rights Reserved · All Photos by Iris', zh: '版权所有 · Iris 摄影', ja: '全著作権所有 · Iris 撮影' },
    location: { en: 'Tulamben, Bali · February 2026', zh: '图蓝本，巴厘岛 · 2026年2月', ja: 'トゥランベン、バリ島 · 2026年2月' },
    gear: { en: 'Olympus E-M1 II & Sony A7R IV', zh: 'Olympus E-M1 II & Sony A7R IV', ja: 'Olympus E-M1 II & Sony A7R IV' },
  },

  /* ── Quote ── */
  quote: {
    en: {
      text: '"The sea, once it casts its spell,<br>holds one in its net of wonder<br>forever."',
      author: '— Jacques Cousteau',
    },
    zh: {
      text: '"大海一旦施展它的魔力，<br>便会将你永远困在<br>它的奇妙之网中。"',
      author: '— 雅克·库斯托',
    },
    ja: {
      text: '"海はいったんその魔法をかけると、<br>人を永遠に不思議の網の中に<br>閉じ込めてしまう。"',
      author: '— ジャック・クストー',
    },
  },
};

/* ── Helper: translate species info ── */
function ti18n(cnName) {
  const entry = GALLERY_I18N.species[cnName];
  if (!entry) return cnName;
  const lang = (localStorage.getItem('iris-lang') || 'en');
  return entry[lang] || entry.en || cnName;
}

function ci18n(cnCat) {
  const entry = GALLERY_I18N.categories[cnCat];
  if (!entry) return cnCat;
  const lang = (localStorage.getItem('iris-lang') || 'en');
  return entry[lang] || entry.en || cnCat;
}

function bi18n(cnBeh) {
  const entry = GALLERY_I18N.behaviors[cnBeh];
  if (!entry) return cnBeh;
  const lang = (localStorage.getItem('iris-lang') || 'en');
  return entry[lang] || entry.en || cnBeh;
}

function colori18n(cnColor) {
  const entry = GALLERY_I18N.colors[cnColor];
  if (!entry) return cnColor;
  const lang = (localStorage.getItem('iris-lang') || 'en');
  return entry[lang] || entry.en || cnColor;
}

function compi18n(cnComp) {
  const entry = GALLERY_I18N.compositions[cnComp];
  if (!entry) return cnComp;
  const lang = (localStorage.getItem('iris-lang') || 'en');
  return entry[lang] || entry.en || cnComp;
}

function ui18n(key) {
  const entry = GALLERY_I18N.ui[key];
  if (!entry) return key;
  const lang = (localStorage.getItem('iris-lang') || 'en');
  return entry[lang] || entry.en || key;
}

function ptitle18n(cnTitle) {
  const entry = GALLERY_I18N.poeticTitles[cnTitle];
  if (!entry) return cnTitle;
  const lang = (localStorage.getItem('iris-lang') || 'en');
  return entry[lang] || entry.en || cnTitle;
}

function quote18n() {
  const lang = (localStorage.getItem('iris-lang') || 'en');
  return GALLERY_I18N.quote[lang] || GALLERY_I18N.quote.en;
}
