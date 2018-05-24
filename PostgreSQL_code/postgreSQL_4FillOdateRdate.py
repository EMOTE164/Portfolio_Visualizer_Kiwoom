import psycopg2
import pandas as pd
from sqlalchemy import create_engine


host = "localhost"
user = "postgres"
dbname = "stockdb"      #사용할 데이터베이스 이름
password = "emote164"   #설치할 때 지정한 것
port = "9003"           #설치할 때 지정할 것

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)

MODE = "kospi"

try:
    # 데이터 베이스를 연결하고 db를 선택해줌
    conn = psycopg2.connect(conn_string)
    print("연결성공")
    cursor = conn.cursor()

    cursor.execute("SELECT code FROM stock_code.kospi order by code;")
    codeList = cursor.fetchall()  # type : list
    
    for i in range(0, len(codeList)):
        currentCode = codeList[i][0]

        cursor.execute("SELECT MIN(date) FROM stock_kospi.daily_price WHERE code = \'" + currentCode + "\'")
        oDate = cursor.fetchall()  # type : list
        cursor.execute("SELECT MAX(date) FROM stock_kospi.daily_price WHERE code = \'" + currentCode + "\'")
        rDate = cursor.fetchall()  # type : list

        if(oDate[0][0] != None and rDate[0][0] != None):
            cursor.execute("update stock_code." + MODE + " SET odate = \'" + str(oDate[0][0]) + "\' WHERE code = \'" + currentCode + "\';")
            cursor.execute("update stock_code." + MODE + " SET rdate = \'"+ str(rDate[0][0]) + "\' WHERE code = \'" + currentCode + "\';")
        else:
            print(currentCode + "코드 인덱스에서 문제터짐")

    conn.commit()  # 이게 없으면 실제로 반영이 안됨.
    cursor.close()
    conn.close()

except Exception as e:
    print("error")
    print(e)

