# 빌드 방법

번역 대본·원문은 저장소에 없으므로, 아래는 자신이 가진 원본과 번역 파일로 다시 빌드하는 절차입니다.

## 준비물
- 원본 ISO `Nobunaga no Yabou - Reppuuden with Power Up Kit (Japan) (v1.02).iso` (MD5 `b933443625dc61c212e3086563952fd1`)
- Python 3.12+ : `pip install pillow numpy pycdlib capstone websocket-client`
- 글꼴: 갈무리14·11·11 Bold·9 (작업 폴더에 .ttf)
- 영상 자막용 FFmpeg(libx264), 검증용 PPSSPP (원격 디버거 사용, `tools/emu.py` 에서 경로 지정)

## 폴더 구성
```
<작업 폴더>/
  Nobunaga no Yabou - Reppuuden with Power Up Kit (Japan) (v1.02).iso
  *.ttf
  tools/        (이 저장소의 tools)
  work/
    iso/        원본 ISO를 풀어 둔 것
    img/ build/ 빌드 중간 파일
    trans/      번역 — 저장소 미포함
      msg/bXX.json     메시지 블록별 번역 {id, jp, ko, maxw}
      boot/*.json      실행 파일 문자열
      names/*.json     고유명사 표
      movie/*.PMF      자막 입힌 영상
```

## 순서
1. 원본 ISO 풀기: `python tools/extract.py "<원본>.iso" work/iso`
2. 번역 작성: `work/trans/` (`docs/TRANSLATION_GUIDE.md`), 검사 `python tools/tcheck.py work/trans/msg/*.json`
3. 그림 글자: `python tools/img.py`
4. 빌드: `python tools/build.py` → `Nobunaga no Yabou - Reppuuden with Power Up Kit (Korean).iso`
5. 차분: `xdelta3 -e -0 -S none -f -s 원본.iso 한글.iso 패치.xdelta`

PPSSPP 원격 디버거로 화면을 확인할 때는 `python tools/emu.py start <ISO>`, `python tools/emu.py press start`, `python tools/emu.py shot a.png`, `python tools/emu.py stop` 을 씁니다.
