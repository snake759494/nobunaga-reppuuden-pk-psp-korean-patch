# 노부나가의 야망 · 열풍전 with 파워업키트 (PSP) 비공식 한글패치

PSP 일본판 **信長の野望・烈風伝 with パワーアップキット (노부나가의 야망 · 열풍전 with 파워업키트, ULJM-05022, v1.02)** 비공식 한국어 패치입니다. 이 저장소에는 제작 도구와 기술 문서만 있고, 패치 파일(xdelta)은 [Releases](../../releases)에서 받을 수 있습니다. 게임 원본·일본어 원문·번역 대본은 포함하지 않습니다.

## 적용 방법

1. 아래 해시와 일치하는 **원본 `.iso`** 를 준비합니다. (CSO·CHD 등으로 변환한 이미지에는 적용할 수 없습니다.)
   - PowerShell: `Get-FileHash -Algorithm MD5 -LiteralPath '.\Nobunaga no Yabou - Reppuuden with Power Up Kit (Japan) (v1.02).iso'`
2. xdeltaUI 같은 도구로 원본 `.iso` 에 `NobunagaReppuudenPK_KO_v1.1.xdelta` 를 적용합니다. (Patch = xdelta, Source File = 원본 ISO, Output File = 새 파일명)
   - 명령줄: `xdelta3 -d -s "Nobunaga no Yabou - Reppuuden with Power Up Kit (Japan) (v1.02).iso" NobunagaReppuudenPK_KO_v1.1.xdelta "Nobunaga no Yabou - Reppuuden with Power Up Kit (Korean).iso"`
3. 만들어진 ISO를 PPSSPP 또는 커스텀 펌웨어(PSP·PS Vita Adrenaline 등)에서 실행합니다.

| 항목 | 값 |
| --- | --- |
| 원본 ISO 크기 | 206,012,416 바이트 |
| 원본 ISO MD5 | `b933443625dc61c212e3086563952fd1` |
| 원본 ISO SHA-256 | `6aa9e2f8f90eff2cd54e85a85be08caf778b37098a9e8b591659832ceee06dae` |
| xdelta SHA-256 | `b486360971405f29fc923c8e7b001af0b30daff118d467db11e4d78b0e0e7306` |
| 결과 ISO 크기 | 206,880,768 바이트 |
| 결과 ISO SHA-256 | `62155633c173c20870f19a428c90005d6da3b1e1acc416a4fe080c7f9f1139d7` |

## 주의
- 암호화되지 않은 수정 실행 파일(BOOT.BIN)을 EBOOT.BIN 자리에도 넣었기 때문에 **PPSSPP·커스텀 펌웨어 전용**입니다. 정품 펌웨어에서는 부팅되지 않습니다.
- v1.02 원본 전용입니다. 다른 판(v1.00 등)에는 적용되지 않습니다.
- 원본에서 만든 **상태저장(세이브 스테이트)** 은 불러오지 마세요. 일반 세이브는 쓸 수 있지만 일본어판에서 만든 신무장 이름 등은 글자 코드가 달라 다르게 보일 수 있습니다.
- 이름 칸이 좁은 곳에서는 성과 이름을 띄어쓰기 없이 붙여 씁니다(「가와지리히데타카」 등).
- xdelta는 2차 압축을 쓰지 않은 형식입니다(약 15MB).

## 한글화 내용
- 메시지 6,749항목(이벤트·평정·외교·무장 열전·용어 사전·시나리오 설명 등) 전체 직접 번역
- 실행 파일 문자열 2,361개(메뉴·커맨드·도움말·서식 문자열 등)
- 고유명사: 무장 1,018명, 성 104개, 가보 351개, 관위·역직 211개, 구니 40개, 칭호 40개
- 인물·지명 뒤 조사를 받침에 맞춰 고르는 실행 중 조사 처리 (`이(가)` → `이`/`가` 자동 선택)
- 메뉴·타이틀·시나리오 선택·커맨드 버튼·에디터 화면 등 그림 글자
- 타이틀 영상·오프닝 영상의 일본어 글자에 한글 자막을 입힘
- 게임 글꼴(16×16)에 KS X 1001 한글 2,350자 추가
- 글꼴: 갈무리14·11·9 (게임 글자·그림 글자·영상 자막)

## 그대로 둔 것
- 음성, 영상 속 그림(자막은 위에 입힘), 아주 작은 아이콘

## 검증 범위
PPSSPP에서 타이틀·영상, 메인 메뉴, 시나리오 선택·설명, 다이묘 선택, 게임 설정, 전략 화면의 각 커맨드, 무장 목록·정보·열전, 용어 사전을 실제로 확인했습니다. 메시지와 실행 파일 문자열은 번역 누락과 줄 폭을 전수 검사했습니다. 합전(특히 해전)과 일부 좁은 메시지 창, 실기 PSP 동작은 직접 확인하지 못했습니다. v1.1에서 실기 기동 불가 문제(#1)의 원인으로 보이는 영상 정보 표 불일치와 캐시 처리를 고쳤습니다. 문제를 발견하면 Issues로 알려 주세요.

## 문서
- [CHANGELOG.md](CHANGELOG.md) — 변경 기록
- [docs/TECHNICAL.md](docs/TECHNICAL.md) — 파일 형식과 한글화 방법
- [docs/BUILD.md](docs/BUILD.md) — 직접 빌드하는 방법
- [docs/TRANSLATION_GUIDE.md](docs/TRANSLATION_GUIDE.md) — 번역 지침
- [docs/FONT_CREDITS.md](docs/FONT_CREDITS.md) — 글꼴
- [RIGHTS.md](RIGHTS.md) — 권리 및 외부 자료
