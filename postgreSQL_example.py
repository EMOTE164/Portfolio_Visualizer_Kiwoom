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

    #스키마 생성
    cursor.execute("create SCHEMA IF NOT EXISTS stock_code;")
    cursor.execute("create SCHEMA IF NOT EXISTS stock_daily;")
    cursor.execute("create SCHEMA IF NOT EXISTS stock_weekly;")
    cursor.execute("create SCHEMA IF NOT EXISTS stock_monthly;")


    #stock_code스키마 하위에 kospi, kosdaq 테이블을 생성
    cursor.execute("create TABLE IF NOT EXISTS stock_code.kospi(code varchar(6) NOT NULL PRIMARY KEY, name varchar(40) NOT NULL);")
    cursor.execute("create TABLE IF NOT EXISTS stock_code.kosdaq(code varchar(6) NOT NULL PRIMARY KEY, name varchar(40) NOT NULL);")

    code1 = "01233"
    name1 = "삼성전자"

    code2 = "88512"
    name2 = "LG전자"

    cursor.execute("INSERT INTO stock_code.kospi(code, name) VALUES(\'" + code1 + "\',\'" + name1 + "\');")
    cursor.execute("INSERT INTO stock_code.kospi(code, name) VALUES(\'" + code2 + "\',\'" + name2 + "\');")

    cursor.execute("SELECT * FROM stock_code.kospi;")

    result = cursor.fetchall()  # type : list
    print(result)

except Exception as e:
    print("error")
    print(e)

conn.commit()   #이게 없으면 실제로 반영이 안됨.
cursor.close()
conn.close()