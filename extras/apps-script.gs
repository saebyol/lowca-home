/**
 * 로우카 쉐어하우스 홈페이지 ↔ 구글 시트 연결
 *
 * 홈페이지가 입주 현황을 물어보면 '매출 장부' 탭에서 체크인·체크아웃·방이름 세 칸만 읽어
 * "어느 방이 어느 날 계약 중인지"만 돌려줘요. 이름·연락처·금액 같은 칸은 아예 읽지 않아요.
 * 계약이 확정되면 평소처럼 '매출 장부'에 적기만 하면 홈페이지 달력에 바로 반영돼요.
 * (입주 상담은 카카오톡으로 받기 때문에 홈페이지에서 시트에 쓰는 기능은 없어요.)
 */

const BOOK_SHEET = '매출 장부';
const COL_CHECKIN = 6;   // F열 체크인
const COL_CHECKOUT = 7;  // G열 체크아웃
const COL_ROOM = 9;      // I열 방이름
const ROOMS = ['하슬라1', '하슬라2', '시나미', '즈므', '윤슬'];
const TZ = 'Asia/Seoul';

function doGet() {
  return json_({ updated: fmt_(new Date()), bookings: readBookings_() });
}

function readBookings_() {
  const sh = SpreadsheetApp.getActive().getSheetByName(BOOK_SHEET);
  const last = sh.getLastRow();
  if (last < 2) return [];
  const width = COL_ROOM - COL_CHECKIN + 1;
  const rows = sh.getRange(2, COL_CHECKIN, last - 1, width).getValues();
  const cutoff = new Date(); cutoff.setDate(cutoff.getDate() - 40);
  const out = [];
  rows.forEach(function (r) {
    const ci = toDate_(r[0]);
    const co = toDate_(r[COL_CHECKOUT - COL_CHECKIN]);
    const rooms = parseRooms_(r[COL_ROOM - COL_CHECKIN]);
    if (!ci || !co || co <= ci || co < cutoff || !rooms.length) return;
    rooms.forEach(function (room) { out.push({ room: room, start: fmt_(ci), end: fmt_(co) }); });
  });
  return out;
}

// '하슬라 1,2'는 두 방을 함께 쓰는 계약. '룸메' 등 목록에 없는 값은 달력에서 빼요.
function parseRooms_(v) {
  const s = String(v || '').replace(/\s/g, '');
  if (s === '하슬라1,2' || s === '하슬라1·2') return ['하슬라1', '하슬라2'];
  return ROOMS.indexOf(s) >= 0 ? [s] : [];
}

function toDate_(v) {
  if (v instanceof Date && !isNaN(v)) return new Date(v.getFullYear(), v.getMonth(), v.getDate());
  const m = String(v || '').match(/(\d{4})\D+(\d{1,2})\D+(\d{1,2})/);
  return m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])) : null;
}

function fmt_(d) { return Utilities.formatDate(d, TZ, 'yyyy-MM-dd'); }

function json_(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}

// 설치 확인용: Apps Script 편집기에서 이 함수를 한 번 실행하면 권한 요청이 뜨고, 읽힌 계약 수가 로그에 찍혀요.
function 연결확인() {
  const list = readBookings_();
  Logger.log('달력에 쓰일 계약 ' + list.length + '건');
  Logger.log(JSON.stringify(list.slice(-5)));
}
