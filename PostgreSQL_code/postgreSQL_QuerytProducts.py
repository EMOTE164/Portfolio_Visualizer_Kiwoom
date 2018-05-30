import psycopg2
import json

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

    cursor.execute("select * FROM stock_code.kospi;")

    result = cursor.fetchall()  # type : list
    #print(result[0][0])

    # DB에 있는 주식 종목코드와 이름을 JSON Array로 만들어서 리턴하는 코드.. format은 다음과 같음.
    # [ {"code":"종목코드", "name":"이름"}, {"code":"종목코드", "name":"이름"}, ..... ]
    datalist=[]
    for element in result:
        if element[0] != '':
            data = {}
            data["code"] = element[0]
            data["name"] = element[1]
            #json_string_data = json.dumps(data, ensure_ascii=False)
            #json_object_data = json.loads(json_string_data)
            #datalist.append(json_object_data)
            datalist.append(data)
    json_data = json.dumps(datalist, ensure_ascii=False)
    print(json_data)

except Exception as e:
    print("error")
    print(e)

conn.commit()   #이게 없으면 실제로 반영이 안됨.
cursor.close()
conn.close()