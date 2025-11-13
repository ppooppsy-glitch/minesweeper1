# Random Joke Generator (Tkinter)

간단한 데스크탑용 지뢰찾기 게임 생성기입니다.  
Python과 Tkinter로 구현된 GUI 앱으로 외부 API (JokeAPI: https://v2.jokeapi.dev)를 사용해 지뢰찾기 게임을 가져옵니다.

## 주요 기능
- "Get Joke" 버튼으로 외부 API에서 랜덤 농담을 가져오기
- Single-line 또는 Two-part(Setup + Delivery) 농담 지원
- 스크롤 가능한 텍스트 영역에 농담 표시
- "Copy" 버튼으로 클립보드에 복사
- "Clear" 버튼으로 텍스트 지우기
- Enter 키로 농담 가져오기 가능
- 네트워크 오류 시 재시도 옵션 표시

## 요구사항
- Python 3.7 이상
- requests 패키지
- 표준 라이브러리의 tkinter (대부분의 Python 설치에 기본 포함)

## 설치
1. (선택) 가상환경 생성 및 활성화
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. 의존성 설치
   ```bash
   pip install requests
   ```

3. 저장된 스크립트 실행
   ```bash
   python random_joke_generator.py
   ```

## 사용법
- 앱 창이 열리면 "Get Joke"을 누르세요. 네트워크를 통해 JokeAPI에서 농담을 받아와 텍스트 영역에 표시합니다.
- Two-part 농담인 경우 setup과 delivery가 빈 줄로 구분되어 표시됩니다.
- "Copy" 버튼을 눌러 현재 표시된 농담을 클립보드로 복사하세요.
- "Clear" 버튼으로 텍스트 영역을 초기화하세요.
- 네트워크 오류가 발생하면 재시도할지 물어보는 대화상자가 나옵니다.

## API 정보 및 필터
이 프로젝트는 https://v2.jokeapi.dev 를 사용합니다. 기본 파라미터로 아래 카테고리를 블랙리스트 처리하여 불쾌할 수 있는 콘텐츠를 배제합니다:
- nsfw, religious, political, racist, sexist, explicit

필요에 따라 코드 내 DEFAULT_PARAMS를 수정하여 카테고리를 조정할 수 있습니다.

## 예시 (스크립트 내부 동작 요약)
- 네트워크 호출은 UI가 멈추지 않도록 백그라운드 스레드에서 수행됩니다.
- API 응답 타입이 `single` 또는 `twopart`인지 확인하여 적절히 포맷합니다.
- UI 업데이트는 메인 스레드에서 안전하게 수행됩니다.

## 문제 해결
- "requests" 패키지 관련 오류: pip로 설치했는지 확인하세요.
- tkinter 관련 오류: 일부 경량 Python 배포판(특히 Windows의 일부 빌드)에는 tkinter가 포함되어 있지 않을 수 있습니다. Python 설치 시 "tkinter" 옵션을 포함하도록 설치하거나 운영체제 패키지 매니저로 설치하세요.
- 네트워크 / 방화벽: 외부 API에 접근이 차단되어 있으면 농담을 가져올 수 없습니다. 프록시/방화벽 설정을 확인하세요.

## 확장 아이디어
- 카테고리 선택 UI 추가 (Programming, Misc, Dark 등)
- 로컬 캐시 또는 히스토리 저장
- 언어 필터/번역 기능 추가
- 웹 버전(Flask/FastAPI) 또는 콘솔 버전 생성
- exe로 패키징(PyInstaller)해 배포

## 라이선스
MIT License — 자유롭게 사용/수정/배포 가능합니다. 원작자 표시는 감사하지만 필수는 아닙니다.

## 파일
- random_joke_generator.py — Tkinter GUI 메인 스크립트 (이 프로젝트의 핵심 파일)

감사합니다! 즐거운 농담 시간 되세요 :)
