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
1.DB서비스을 시작시킴
- 시작-"Start PostgreSQL 10"

2.명령어를 입력할 수 있는 Shell을 실행시킴
- 시작-"PSQL"

3.TABLESPACE를 생성
- TableSpace는 PostgreSQL에서 DBA가 데이터베이스 객체가 저장된 파일 시스템 장소를 지정할 수 있게 해주는 기능을 함
- create tablespace 테이블스페이스명 location 'C:\PostgreSQL\';
- //되도록이면 명령문에는 대문자를 사용하지 말자. 오류로 인식한다. 아직 안정화가 덜 된것일까?
- //생성시 OWNER도 지정해 줄 수 있는데 명시를 해주지 않으면 기본 값으로 알아서 들어감
