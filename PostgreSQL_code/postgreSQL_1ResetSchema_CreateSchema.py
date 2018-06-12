#데이터베이스 초기화

import psycopg2

host = "localhost"
user = "postgres"
dbname = "stockdb"      #사용할 데이터베이스 이름
password = "emote164"   #설치할 때 지정한 것
port = "9003"           #설치할 때 지정할 것

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)

try:
    #데이터 베이스를 연결하고 db를 선택해줌
    conn = psycopg2.connect(conn_string)
    print("연결성공")

    cursor = conn.cursor()

    # 존재할 수 있는 테이블 제거
    cursor.execute("drop TABLE IF EXISTS stock_kospi.daily_price;")
    cursor.execute("drop TABLE IF EXISTS stock_kosdaq.daily_price;")
    cursor.execute("drop TABLE IF EXISTS stock_code.kospi;")
    cursor.execute("drop TABLE IF EXISTS stock_code.kosdaq;")
    print("기존에 존재하던 테이블 제거완료")

    # 스키마 제거
    cursor.execute("drop SCHEMA IF EXISTS stock_code;")
    cursor.execute("drop SCHEMA IF EXISTS stock_kospi;")
    cursor.execute("drop SCHEMA IF EXISTS stock_kosdaq;")
    print("기존에 존재하던 스키마 제거완료")

    # 스키마 생성
    cursor.execute("create SCHEMA IF NOT EXISTS stock_code;")
    cursor.execute("create SCHEMA IF NOT EXISTS stock_kospi;")
    cursor.execute("create SCHEMA IF NOT EXISTS stock_kosdaq;")
    print("스키마 생성완료")

    # 테이블 생성
    cursor.execute("create TABLE stock_code.kospi(code varchar(6) NOT NULL PRIMARY KEY, name varchar(40) NOT NULL, odate integer default -1, rdate integer default -1);")
    cursor.execute("create TABLE stock_code.kosdaq(code varchar(6) NOT NULL PRIMARY KEY, name varchar(40) NOT NULL, odate integer default -1, rdate integer default -1);")
    cursor.execute("create TABLE stock_kospi.daily_price(code varchar(6) NOT NULL REFERENCES stock_code.kospi(code), date integer NOT NULL, open integer, low integer, high integer, close integer, count integer, money integer, PRIMARY KEY(code, date));")
    cursor.execute("create TABLE stock_kosdaq.daily_price(code varchar(6) NOT NULL REFERENCES stock_code.kosdaq(code), date integer NOT NULL, open integer, low integer, high integer, close integer, count integer, money integer, PRIMARY KEY(code, date));")
    print("테이블 생성완료")

except Exception as e:
    print("error")
    print(e)

conn.commit()   #이게 없으면 실제로 반영이 안됨.
cursor.close()
conn.close()