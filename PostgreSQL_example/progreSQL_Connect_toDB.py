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

    cursor.execute("select count(*) FROM stock_code.kospi;")

    result = cursor.fetchall()
    print(result[0][0])

except Exception as e:
    print("error")
    print(e)

conn.commit()   #이게 없으면 실제로 반영이 안됨.
cursor.close()
conn.close()