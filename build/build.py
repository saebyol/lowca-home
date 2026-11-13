"""로우카 홈페이지 빌드
src.html + photos.json + faq.json → site/ 폴더(페이지별 폴더 구조)와 미리보기용 artifact.html
빌드 뒤에 prerender.py를 돌리면 화면에 그려진 내용이 HTML 안에 미리 들어가요(네이버 검색용)
"""
import json, pathlib, html, re, shutil, datetime
root = pathlib.Path(__file__).resolve().parent.parent
SITE = root / 'site'
src = (root/'build/src.html').read_text(encoding='utf-8')
photos = json.loads((root/'build/photos.json').read_text())
faq = json.loads((root/'build/faq.json').read_text(encoding='utf-8'))
src = src.replace('/*@PHOTOS*/{}', json.dumps(photos, separators=(',',':')))

SITE_URL = 'https://lowca.pages.dev/'
GA_ID = 'G-FPXVGSQXRM'  # 구글 애널리틱스 측정 ID  # 실제 주소가 정해지면 바꾸기 (끝에 / 포함)

# ---------- FAQ ----------
def faq_item(x):
    ans = x["a"].replace('<br>', ' <br>')  # 휴대폰에서 줄바꿈을 숨길 때 띄어쓰기가 붙지 않게
    return f'<details class="faq-item"><summary>{x["q"]}</summary><div class="a"><p>{ans}</p></div></details>'
faq_full = '\n'.join(
    f'<div class="faq-cat" id="faq-{c["key"]}"><div class="faq-cat-h"><p class="en">{c["en"]}</p><h2>{c["name"]}</h2></div>'
    f'<div class="faq-list">{"".join(faq_item(x) for x in c["items"])}</div></div>' for c in faq['cats'])
faq_home = ''.join(faq_item(x) for c in faq['cats'] for x in c['items'] if x.get('home'))
src = src.replace('<!--@FAQ_FULL-->', faq_full).replace('<!--@FAQ_HOME-->', faq_home)
src = src.replace('/*@FAQ*/{}', json.dumps(faq, ensure_ascii=False, separators=(',',':')))
def plain(t): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<br\s*/?>', ' ', re.sub(r'<(?!br)[^>]+>', '', t)))).strip()
faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": x['q'], "acceptedAnswer": {"@type": "Answer", "text": plain(x['a'])}}
    for c in faq['cats'] for x in c['items']]}

head, body = src.split('<!--@BODY-->')
# 미리보기(artifact)는 설정이 들어간 한 파일 그대로
(root/'build/artifact.html').write_text((head + body).replace('/*@CONFIG_START*/\n', '').replace('/*@CONFIG_END*/\n', ''), encoding='utf-8')

# 홈페이지용: 설정은 config.js 한 곳에서 고쳐요
cfg = re.search(r'/\*@CONFIG_START\*/\n(.*?)/\*@CONFIG_END\*/\n', body, re.S)
config_js = '/* 로우카 홈페이지 설정 이 파일만 고치면 모든 페이지에 반영돼요 */\n' + cfg.group(1)
body_site = body.replace(cfg.group(0), '')

biz = {"@context": "https://schema.org", "@type": "LocalBusiness", "@id": SITE_URL + "#lowca",
 "name": "로우카 쉐어하우스", "logo": SITE_URL + "favicon-192.png", "alternateName": ["LOWCA Sharehouse", "로우카 셰어하우스", "강릉 로우카"],
 "description": "강릉역 도보 5분, 교동 건물 꼭대기층을 리모델링한 주거형 단기 임대 쉐어하우스예요. 1인실 3개와 2인 셰어룸 1개, 최소 6박부터 최대 6개월까지 지낼 수 있어요.",
 "url": SITE_URL, "telephone": "+82-507-1489-0869",
 "image": [SITE_URL + "images/" + f for f in ["og-home.jpg", "og-jeumeu.jpg", "og-sinami.jpg", "og-yunseul.jpg", "og-haseulla.jpg", "og-monthly.jpg"]],
 "hasMap": "https://map.naver.com/p/entry/place/1327156673",
 "address": {"@type": "PostalAddress", "streetAddress": "강릉대로 250", "addressLocality": "강릉시", "addressRegion": "강원특별자치도", "postalCode": "", "addressCountry": "KR"},
 "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in
                    ["와이파이", "공용 주방", "세탁기", "건조기", "옥상정원", "방별 도어락", "공용 공간 CCTV", "남녀 분리 화장실"]],
 "sameAs": ["https://blog.naver.com/lowca_sharehouse", "https://www.instagram.com/lowca_house/", "https://map.naver.com/p/entry/place/1327156673"]}
del biz["address"]["postalCode"]
# 검색 결과에 'pages.dev' 대신 사이트 이름이 나오도록
site_ld = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE_URL + "#website", "name": "로우카 쉐어하우스",
           "alternateName": ["로우카", "LOWCA", "로우카 셰어하우스"], "url": SITE_URL, "inLanguage": "ko-KR", "publisher": {"@id": SITE_URL + "#lowca"}}

KEYWORDS = "강릉 단기임대, 강릉 달방, 강릉 한달살기, 강릉 한 달 살기, 강릉 일주일살기, 강릉 일주일 살기, 강릉 쉐어하우스, 강릉 셰어하우스, 강릉 병원 실습, 강릉아산병원 실습, 강릉의료원 실습, 강릉 출장, 강릉 단기 원룸, 강릉 월세 단기, 강릉역 쉐어하우스, 강릉 워케이션, 교동 쉐어하우스, 로우카"

# (폴더, data-start, 제목, 설명, 대표 사진)
PAGES = [
 ('', '', '로우카 쉐어하우스 | 강릉역 도보 5분 한달살기 · 단기임대 쉐어하우스',
  '강릉역 도보 5분, 교동의 주거형 단기 임대 쉐어하우스예요. 1인실 3개와 2인 셰어룸에서 6박부터 6개월까지 지낼 수 있어요.', 'og-home.jpg', '로우카 1인실 시나미'),
 ('jeumeu', 'room-jeumeu', '즈므 1인실 | 로우카 쉐어하우스',
  '해가 저무는 마을이라는 뜻의 1인실 즈므예요. 노을이 드는 방의 사진과 입주 가능일을 확인해 보세요.', 'og-jeumeu.jpg', '로우카 1인실 즈므'),
 ('sinami', 'room-sinami', '시나미 1인실 | 로우카 쉐어하우스',
  '강릉 말로 ‘천천히’라는 뜻의 1인실 시나미예요. 조용하고 밝은 방의 사진과 입주 가능일을 확인해 보세요.', 'og-sinami.jpg', '로우카 1인실 시나미'),
 ('yunseul', 'room-yunseul', '윤슬 1인실 | 로우카 쉐어하우스',
  '반짝이는 물결을 뜻하는 1인실 윤슬이에요. 차분하고 아늑한 방의 사진과 입주 가능일을 확인해 보세요.', 'og-yunseul.jpg', '로우카 1인실 윤슬'),
 ('haseulla', 'room-haseulla', '하슬라 2인 셰어룸 | 로우카 쉐어하우스',
  '강릉의 옛 지명에서 이름을 딴 2인 셰어룸 하슬라예요. 방 사진과 입주 가능일을 확인해 보세요.', 'og-haseulla.jpg', '로우카 2인 셰어룸 하슬라'),
 ('facilities', 'facilities', '공용 공간 | 로우카 쉐어하우스',
  '로우카의 공용 거실과 주방, 남녀 화장실, 세탁실, 옥상정원을 사진으로 둘러보세요.', 'og-facilities.jpg', '로우카 공용 거실'),
 ('short-term', 'for-short-term', '강릉 단기임대, 한 달 단위로 지낼 방 | 로우카 쉐어하우스',
  '강릉역 도보 5분 쉐어하우스 로우카예요. 공과금과 인터넷 포함, 6박부터 6개월까지 계약할 수 있어요.', 'og-short-term.jpg', '로우카 공용 거실'),
 ('hospital', 'for-hospital', '강릉 병원 실습 단기 임대 숙소 | 로우카 쉐어하우스',
  '강릉아산병원, 강릉의료원까지 차로 5~15분이에요. 실습 일정에 맞춰 6박부터 계약할 수 있어요.', 'og-hospital.jpg', '로우카 공용 거실'),
 ('business', 'for-business', '강릉 출장 · 교육 기간 지낼 곳 | 로우카 쉐어하우스',
  'KTX 강릉역에서 걸어서 5분이에요. 와이파이와 방마다 책상이 있어 출장·교육 기간에 지내기 좋아요.', 'og-business.jpg', '로우카 공용 거실'),
 ('monthly', 'for-monthly', '강릉 한달살기 · 일주일살기 | 로우카 쉐어하우스',
  '월화거리는 걸어서 5분, 바다는 차로 15분이에요. 로우카에서 강릉 한 달 살기를 시작해 보세요.', 'og-monthly.jpg', '로우카 공용 거실'),
 ('faq', 'faq', '자주 묻는 질문 | 로우카 쉐어하우스',
  '임대료와 보증금, 포함 항목, 준비물, 보안까지 로우카 입주 전 많이 묻는 질문을 모았어요.', 'og-faq.jpg', '로우카 공용 거실'),
]
SECTIONS = {'about', 'for-you', 'rooms', 'facility-preview', 'availability', 'guide', 'process', 'faq-preview', 'check', 'location'}

def link(t, start, rootp):
    """JS의 link()와 같은 규칙"""
    if t.startswith('room-'): return rootp + t[5:] + '/'
    if t == 'facilities': return rootp + 'facilities/'
    if t.startswith('fac-'): return ('#' + t) if start == 'facilities' else rootp + 'facilities/#' + t
    if t == 'faq': return rootp + 'faq/'
    if t.startswith('for-'): return rootp + t[4:] + '/'
    if t == 'home': return rootp if start else '#home'
    return (rootp if start else '') + '#' + t

def page(folder, start, title, desc, ogimg, ogalt):
    rootp = '../' if folder else ''
    url = SITE_URL + (folder + '/' if folder else '')
    img_url = SITE_URL + 'images/' + ogimg
    web_ld = {"@context": "https://schema.org", "@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc, "inLanguage": "ko-KR",
              "isPartOf": {"@id": SITE_URL + "#website"}, "about": {"@id": SITE_URL + "#lowca"},
              "primaryImageOfPage": {"@type": "ImageObject", "url": img_url, "width": 1200, "height": 630}, "image": img_url}
    lds = [site_ld, biz, web_ld] + ([faq_ld] if start == 'faq' else [])
    seo = f'''<meta name="description" content="{html.escape(desc)}">
<meta name="keywords" content="{KEYWORDS}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="naver-site-verification" content="ac5804994360720ee1ff4a7de1af9a650e8bdc6e">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="로우카 쉐어하우스">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{img_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{html.escape(ogalt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{img_url}">
<link rel="image_src" href="{img_url}">
<meta name="theme-color" content="#ffffff">
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag("js",new Date());gtag("config","{GA_ID}");</script>
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
<link rel="icon" type="image/png" sizes="48x48" href="/favicon-48.png">
<link rel="icon" type="image/png" sizes="96x96" href="/favicon-96.png">
<link rel="icon" type="image/png" sizes="192x192" href="/favicon-192.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
''' + ''.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>\n' for x in lds)
    h = head.replace('<title>로우카 쉐어하우스</title>', f'<title>{html.escape(title)}</title>\n' + seo)
    b = body_site
    b = re.sub(r'href="#([a-z0-9-]+)"', lambda m: f'href="{link(m.group(1), start, rootp)}"', b)
    b = b.replace('src="images/', f'src="{rootp}images/')
    b = b.replace('<script>\n/* ===== 설정', f'<script src="{rootp}config.js"></script>\n<script>\n/* ===== 설정', 1)
    return f'<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n{h}</head>\n<body data-start="{start}" data-root="{rootp}">{b}</body>\n</html>\n'

# 예전 방식(jeumeu.html 같은 파일)은 지워요
for old in ['jeumeu.html', 'sinami.html', 'yunseul.html', 'haseulla.html', 'facilities.html']:
    (SITE/old).unlink(missing_ok=True)
for folder, *rest in PAGES:
    out = SITE/folder/'index.html' if folder else SITE/'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(folder, *rest), encoding='utf-8')
(SITE/'config.js').write_text(config_js, encoding='utf-8')
(SITE/'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n', encoding='utf-8')
today = datetime.date.today().isoformat()
urls = ''.join(f'  <url><loc>{SITE_URL}{f + "/" if f else ""}</loc><lastmod>{today}</lastmod></url>\n' for f, *_ in PAGES)
(SITE/'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding='utf-8')
print('build ok')
