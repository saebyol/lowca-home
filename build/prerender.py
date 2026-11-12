"""site 폴더의 각 페이지를 브라우저로 열어, 화면에 그려진 내용을 HTML 안에 미리 저장해요
(네이버 검색 로봇이 자바스크립트를 실행하지 않아도 방 이름, 설명, FAQ를 읽을 수 있게)
실행: python3 build/build.py && python3 build/prerender.py
"""
import pathlib, re, subprocess, sys, time, socket
from playwright.sync_api import sync_playwright

SITE = pathlib.Path(__file__).resolve().parent.parent / 'site'
PAGES = ['', 'jeumeu/', 'sinami/', 'yunseul/', 'haseulla/', 'facilities/', 'short-term/', 'hospital/', 'business/', 'monthly/', 'faq/']

CLEAN = r"""(title) => {
  const active = [...document.querySelectorAll('[data-view]')].find((v) => !v.hidden);
  // 지금 페이지가 아닌 화면의 h1은 h2로 (페이지마다 대표 제목은 하나)
  document.querySelectorAll('h1').forEach((h) => {
    if (active && active.contains(h)) return;
    const n = document.createElement('h2');
    for (const a of h.attributes) n.setAttribute(a.name, a.value);
    n.innerHTML = h.innerHTML; h.replaceWith(n);
  });
  // 날짜에 따라 바뀌는 입주 현황은 비워 두고, 열릴 때 새로 그려요
  ['#cal', '#picked', '#monthLabel', '#checkList', '#kakaoMsg', '#nights'].forEach((s) => { const e = document.querySelector(s); if (e) e.innerHTML = ''; });
  document.querySelectorAll('.state').forEach((e) => (e.innerHTML = ''));
  document.querySelectorAll('.avail-wait').forEach((e) => e.remove());
  document.body.classList.remove('no-avail');
  document.querySelectorAll('script[src*="map.naver.com"]').forEach((e) => e.remove());
  document.querySelectorAll('[aria-current]').forEach((e) => e.removeAttribute('aria-current'));
  document.title = title;
  return '<!doctype html>\n' + document.documentElement.outerHTML + '\n';
}"""

def free_port():
    s = socket.socket(); s.bind(('127.0.0.1', 0)); p = s.getsockname()[1]; s.close(); return p

port = free_port()
srv = subprocess.Popen([sys.executable, '-m', 'http.server', str(port), '--bind', '127.0.0.1', '--directory', str(SITE)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
try:
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        for p in PAGES:
            f = SITE / p / 'index.html'
            raw = f.read_text(encoding='utf-8')
            if 'data-prerendered' in raw:
                sys.exit(f'{f} 는 이미 미리 저장된 파일이에요 build.py부터 다시 실행해 주세요')
            title = re.search(r'<title>(.*?)</title>', raw, re.S).group(1)
            import html as _h
            title = _h.unescape(title)
            pg = b.new_page(viewport={'width': 1280, 'height': 900})
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(f'http://127.0.0.1:{port}/{p}', wait_until='networkidle')
            pg.wait_for_timeout(300)
            if errs: sys.exit(f'{p}: {errs}')
            out = pg.evaluate(CLEAN, title)
            out = out.replace('<html lang="ko">', '<html lang="ko" data-prerendered="1">', 1)
            f.write_text(out, encoding='utf-8')
            pg.close()
            print('prerendered', p or 'index')
        b.close()
finally:
    srv.terminate()
