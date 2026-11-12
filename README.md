# 로우카 쉐어하우스 홈페이지

강릉역 도보 5분 주거형 단기 임대 쉐어하우스 로우카의 홈페이지예요

## 폴더
- `site/` 실제 홈페이지 (Cloudflare Pages 출력 폴더)
  - `config.js` 구글 시트 주소(API_URL), 카카오톡 주소 같은 설정
- `build/` 원본 (`src.html` 화면과 문구, `faq.json` 자주 묻는 질문, `photos.json` 사진 목록)
- `extras/` 구글 시트 연결 스크립트와 설치 안내

## 고치는 방법
`build/`의 원본을 고친 뒤 아래를 실행하면 `site/`가 새로 만들어져요

```
python3 build/build.py && python3 build/prerender.py
```

`prerender.py`는 화면에 그려진 내용을 HTML에 미리 저장해서 네이버 검색 로봇이 방 이름과 설명, FAQ를 읽을 수 있게 해요 (Playwright 필요)
