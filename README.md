# 구현 시 주의점
Portfolio_Visualizer_Kiwoom/PostgreSQL_code/postgreSQL_3AddDailyPrice.py
키움증권 함수를 사용할 때 반복문을 사용하여 호출하게 되면 순차적 완료 실행이 아닌 비동기적 흐름이 나타나기 때문에 이를 주의해야 함
sleep 함수를 두어서 시간차를 줘봤지만 이도 소용이 없어 이벤트를 발생했을때 다음것이 불리게 하는 구현을 해야할 것 같다.

# 실행가능환경

- 운영체제 : Windows7 or 10

- 파이썬 : python3.x 32bit

- 데이터베이스 : postgreSQL 10.3

- 웹프레임워크 : Django

- 증권사API : 키움증권 OPEN API



# 환경구성을 위한 설치

파이썬 및 사용되는 모듈을 일일이 다운받아야 하는 번거로운 작업에 시간을 낭비하지 않으려면 Anaconda를 통한 설치장려.

- https://www.anaconda.com/downloada


데이터베이스로 postgreSQL을 사용하므로 다음 사이트에서 "Download the graphical installer" 클릭 후 자신에 맞는 설치.

- https://www.postgresql.org/download/windows/


키움증권 API를 사용하려면 아래의 4가지 작업을 해줘야 한다.

- https://www2.kiwoom.com/nkw.templateFrameSet.do?m=m1408000000
- Open API 사용신청
- 키움증권 Open API+ 모듈설치
- KOA Studio 설치
- 상시 모의투자 신청



# postgreSQL사용법
TABLESPACE 설명 : http://www.gurubee.net/lecture/2946

테이블생성까지의 과정 : http://freeprog.tistory.com/248

단축 명령어 : http://dbrang.tistory.com/749

1.DB서비스을 시작시킴
- 시작-"Start PostgreSQL 10"

2.명령어를 입력할 수 있는 Shell을 실행시킴
- 시작-"PSQL"

3.TABLESPACE 생성
- TableSpace는 DB관리자에 의해 데이터베이스의 객체가 저장될 수 있는 파일시스템 경로이다.
- ``create TABLESPACE 테이블스페이스명 LOCATION 디렉토리경로;``
- //명령문의 시작 단어는 소문자로 시작하게 하라. 대분자로 시작하면 오류로 인식한다. 아직 안정화가 덜 된것일까?
- //생성시 OWNER도 지정해 줄 수 있는데 명시를 해주지 않으면 기본 값으로 알아서 들어감
- 조회방법 : ``\db``
- 삭제방법 : ``drop TABLESPACE 테이블스페이스명;``
- //TABLESPACE와 연결된 DATABASE가 존재한다면 삭제불가하니 하위 내용을 지우고 삭제가능

4. DATABASE 생성
- ``create 데이터베이스명 TABLESPACE 테이블스페이스명``
- //지정된 테이블스페이스명에 연결된 경로에 관련 파일이 만들어진다.
- ``create 데이터베이스명``
- //기본으로 설정된 곳에 관련 파일이 만들어진다.
- 조회방법 : ``\l``
- 삭제방법 : ``drop DATABASE 데이터베이스명;``
- //DATABASE에 현재 연결중이라면 ``\q``를 이용해 창을 껐다가 키자. 혹은 다른 DATABASE로 연결한뒤 시도.

5. DATABASE 연결
- ``\c 데이터베이스명``

6. SCHEMA 생성
- ``create SCHEMA 스키마명;``
- 스키마는 테이블을 묶어주는 역할을 하며 스키마를 생성하지 않으면 테이블들은 미리 존재하는 public이란 스키마에 붙음.
- 조회방법 : ``\dn``
- 삭제방법 : ``drop SCHEMA 스키마명;``

7. TABLE 생성
- ``create TABLE 스키마명.테이블명 ( 변수명 integer PRIMARY KEY, 변수명 varchar(20), 변수명 char(13), 변수명 date)``
- //지정한 스키마명의 하위 테이블로 들어감
- ``create TABLE 테이블명 ( 변수명 integer PRIMARY KEY, 변수명 varchar(20), 변수명 char(13), 변수명 date)``
- //public 스키마의 하위 테이블로 들어감
- 조회방법 : ``\dt``
- 조회방법 : ``\dt 스키마명.``
- 삭제방법 : ``drop TABLE 테이블명``

# 설계한 DB구조
<img src="https://github.com/EMOTE164/Portfolio_Visualizer_Kiwoom/blob/master/DB%E1%84%89%E1%85%A5%E1%86%AF%E1%84%80%E1%85%A8%E1%84%89%E1%85%A1%E1%84%8C%E1%85%B5%E1%86%AB/%E1%84%8C%E1%85%A5%E1%86%AB%E1%84%8E%E1%85%A6%E1%84%80%E1%85%AE%E1%84%8C%E1%85%A9.png?raw=true" width="70%"></img>
<img src="https://github.com/EMOTE164/Portfolio_Visualizer_Kiwoom/blob/master/DB%E1%84%89%E1%85%A5%E1%86%AF%E1%84%80%E1%85%A8%E1%84%89%E1%85%A1%E1%84%8C%E1%85%B5%E1%86%AB/%E1%84%90%E1%85%A6%E1%84%8B%E1%85%B5%E1%84%87%E1%85%B3%E1%86%AF%20%E1%84%89%E1%85%A5%E1%86%AF%E1%84%80%E1%85%A8.png?raw=true" width="70%"></img>


# 프로젝트 실행순서
1. Anaconda prompt에서 현재 경로를 STOCK폴더 하위로 이동.
2. ``python manage.py runserver 0.0.0.0:80``으로 실행
3. 브라우저에서 url입력란에 localhost를 입력하여 접속

# 실행사진
<img src="https://github.com/EMOTE164/Portfolio_Visualizer_Kiwoom/blob/master/%EC%8B%A4%ED%96%89%EC%82%AC%EC%A7%84/111.png?raw=true" width="100%"></img>
<img src="https://github.com/EMOTE164/Portfolio_Visualizer_Kiwoom/blob/master/%EC%8B%A4%ED%96%89%EC%82%AC%EC%A7%84/2222.PNG?raw=true" width="100%"></img>
<img src="https://github.com/EMOTE164/Portfolio_Visualizer_Kiwoom/blob/master/%EC%8B%A4%ED%96%89%EC%82%AC%EC%A7%84/333.png?raw=true" width="100%"></img>
<img src="https://github.com/EMOTE164/Portfolio_Visualizer_Kiwoom/blob/master/%EC%8B%A4%ED%96%89%EC%82%AC%EC%A7%84/444.png?raw=true" width="100%"></img>
