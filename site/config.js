/* 로우카 홈페이지 설정 이 파일만 고치면 모든 페이지에 반영돼요 */
const CONFIG = {
  // 구글 시트 Apps Script 웹 앱 주소 비워 두면 아래 SAMPLE 예시로 보여 줘요
  API_URL: "",
  // 카카오톡 채널 채팅 주소(https://pf.kakao.com/_xxxx/chat). 지금은 기존 오픈채팅 주소예요
  KAKAO_URL: "https://open.kakao.com/me/Lowca",
  // 네이버 톡톡 주소(https://talk.naver.com/...). 넣으면 상담 버튼이 하나 더 생겨요
  NAVER_TALK_URL: "",
  // 네이버 지도 API Client ID(네이버 클라우드 플랫폼 > Maps). 넣으면 위치 영역에 네이버 지도가 나와요
  NAVER_MAP_KEY: "",
  MAP_ADDRESS: "강원특별자치도 강릉시 강릉대로 250",
  MAP_LAT: null, MAP_LNG: null,   // 좌표를 알면 넣어 주세요 비워 두면 주소로 위치를 찾아요
  MIN_DAYS: 6,
  MAX_DAYS: 183,
  MONTHS_AHEAD: 11
};
