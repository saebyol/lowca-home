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

SITE_URL = 'https://lowca.pages.dev/'  # 실제 주소가 정해지면 바꾸기 (끝에 / 포함)

# ---------- FAQ ----------
def faq_item(x):
    ans = x["a"].replace('<br>', ' <br>')  # 휴대폰에서 줄바꿈을 숨길 때 띄어쓰기가 붙지 않게
    return f'<details class="faq-item"><summary>{x["q"]}</summary><div class="a"><p>{ans}</p></div></details>'
faq_full = '\n'.join(
    f'<div class="faq-cat" id="faq-{c["key"]}"><div class="faq-cat-h"><p class="en">{c["en"]}</p><h2>{c["name"]}</h2></div>'
    f'<div class="faq-list">{"".join(faq_item(x) for x in c["items"])}</div></div>' for c in faq['cats'])
faq_home = ''.join(faq_item(x) for c in faq['cats'] for x in c['items'] if x.get('home'))
src = src.replace('<!--@FAQ_FULL-->', faq_full).replace('<!--@FAQ_HOME-->', faq_home)
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
 "name": "로우카 쉐어하우스", "alternateName": ["LOWCA Sharehouse", "로우카 셰어하우스", "강릉 로우카"],
 "description": "강릉역 도보 5분, 교동 건물 꼭대기층을 리모델링한 주거형 단기 임대 쉐어하우스예요. 1인실 3개와 2인 셰어룸 1개, 최소 6박부터 최대 6개월까지 지낼 수 있어요.",
 "url": SITE_URL, "telephone": "+82-507-1489-0869", "image": SITE_URL + "images/og.jpg",
 "hasMap": "https://map.naver.com/p/entry/place/1327156673",
 "address": {"@type": "PostalAddress", "streetAddress": "강릉대로 250", "addressLocality": "강릉시", "addressRegion": "강원특별자치도", "postalCode": "", "addressCountry": "KR"},
 "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in
                    ["와이파이", "공용 주방", "세탁기", "건조기", "옥상정원", "방별 도어락", "공용 공간 CCTV", "남녀 분리 화장실"]],
 "sameAs": ["https://blog.naver.com/lowca_sharehouse", "https://www.instagram.com/lowca_house/", "https://map.naver.com/p/entry/place/1327156673"]}
del biz["address"]["postalCode"]

KEYWORDS = "강릉 쉐어하우스, 강릉 셰어하우스, 강릉 한달살기, 강릉 일주일 살기, 강릉 단기임대, 강릉 단기 원룸, 강릉 한달살기 숙소, 강릉 병원 실습 숙소, 강릉아산병원 실습, 강릉역 쉐어하우스, 강릉 워케이션, 강릉 출장, 교동 쉐어하우스, 로우카"

# (폴더, data-start, 제목, 설명, 대표 사진)
PAGES = [
 ('', '', '강릉 한달살기 · 단기임대 쉐어하우스 로우카 | 강릉역 도보 5분',
  '강릉역 도보 5분 교동 쉐어하우스 로우카 · 1인실 3개와 2인 셰어룸 · 최소 6박부터 최대 6개월 · 일주일 살기, 한 달 살기, 병원 실습, 출장, 워케이션을 위한 주거형 단기 임대 · 공과금과 관리비 포함', 'og.jpg'),
 ('jeumeu', 'room-jeumeu', '즈므 1인실 · 강릉 단기임대 쉐어하우스 로우카',
  '강릉역 도보 5분 쉐어하우스 로우카의 1인실 즈므 · 노을이 스며드는 창이 있는 혼자만의 방 · 방 사진과 입주 가능일을 확인해 보세요 · 최소 6박부터 최대 6개월', 'jeumeu-1.jpg'),
 ('sinami', 'room-sinami', '시나미 1인실 · 강릉 단기임대 쉐어하우스 로우카',
  '강릉역 도보 5분 쉐어하우스 로우카의 1인실 시나미 · 부드러운 빛이 드는 조용한 방 · 방 사진과 입주 가능일을 확인해 보세요 · 최소 6박부터 최대 6개월', 'sinami-1.jpg'),
 ('yunseul', 'room-yunseul', '윤슬 1인실 · 강릉 단기임대 쉐어하우스 로우카',
  '강릉역 도보 5분 쉐어하우스 로우카의 1인실 윤슬 · 차분하고 아늑한 혼자만의 방 · 방 사진과 입주 가능일을 확인해 보세요 · 최소 6박부터 최대 6개월', 'yunseul-1.jpg'),
 ('haseulla', 'room-haseulla', '하슬라 2인 셰어룸 · 강릉 단기임대 쉐어하우스 로우카',
  '강릉역 도보 5분 쉐어하우스 로우카의 2인 셰어룸 하슬라 · 임대료는 1인 기준, 일행과 함께 계약하면 할인 · 같은 성별의 입주자와 함께 쓰는 방 · 방 사진과 입주 가능일을 확인해 보세요', 'haseulla-1.jpg'),
 ('facilities', 'facilities', '공용 공간 · 강릉 쉐어하우스 로우카 | 거실 · 주방 · 세탁실 · 옥상정원',
  '강릉 쉐어하우스 로우카의 공용 거실, 주방, 남녀 분리 화장실·샤워실, 세탁기와 건조기가 있는 세탁실, 옥상정원 사진을 둘러보세요 · 공용 공간은 주 1회 정기 청소', 'living-1.jpg'),
 ('faq', 'faq', '자주 묻는 질문 · 강릉 쉐어하우스 로우카 | 한달살기 · 병원 실습 · 단기임대',
  '강릉 쉐어하우스 로우카 입주 전 자주 묻는 질문 · 임대료와 보증금, 포함 항목, 준비물, 보안, 강릉아산병원 실습과 출장, 차 없이 지내기까지 한 번에 확인해 보세요', 'kitchen-1.jpg'),
]
SECTIONS = {'about', 'for-you', 'rooms', 'facility-preview', 'availability', 'guide', 'process', 'faq-preview', 'check', 'location'}

def link(t, start, rootp):
    """JS의 link()와 같은 규칙"""
    if t.startswith('room-'): return rootp + t[5:] + '/'
    if t == 'facilities': return rootp + 'facilities/'
    if t.startswith('fac-'): return ('#' + t) if start == 'facilities' else rootp + 'facilities/#' + t
    if t == 'faq': return rootp + 'faq/'
    if t == 'home': return rootp if start else '#home'
    return (rootp if start else '') + '#' + t

def page(folder, start, title, desc, ogimg):
    rootp = '../' if folder else ''
    url = SITE_URL + (folder + '/' if folder else '')
    lds = [biz] + ([faq_ld] if start == 'faq' else [])
    seo = f'''<meta name="description" content="{html.escape(desc)}">
<meta name="keywords" content="{KEYWORDS}">
<meta name="naver-site-verification" content="ac5804994360720ee1ff4a7de1af9a650e8bdc6e">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="로우카 쉐어하우스">
<meta property="og:locale" content="ko_KR">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}images/{ogimg}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
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
