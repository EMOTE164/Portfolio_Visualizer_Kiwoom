#GetCodeListByMarket, GetMasterCodeName을 이용해 stock_code.kospi, stock_code.kosdaq 테이블을 채움

import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import psycopg2

host = "localhost"
user = "postgres"
dbname = "stockdb"      #사용할 데이터베이스 이름
password = "emote164"   #설치할 때 지정한 것
port = "9003"           #설치할 때 지정할 것

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)

class Program(QMainWindow):

    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")  # 로그인창 호출
        # 서버로부터 오는 이벤트에 콜백함수 등록
        self.kiwoom.OnEventConnect.connect(self.receiveLoginEvent)

    # 로그인창에서 아이디와 패스워드가 맞으면 불리는 함수
    def receiveLoginEvent(self, err_code):
        if err_code == 0:
            print("로그인 성공")

            try:
                # 데이터 베이스를 연결하고 db를 선택해줌
                conn = psycopg2.connect(conn_string)
                print("연결성공")

                cursor = conn.cursor()

                # 스키마 생성
                cursor.execute("create SCHEMA IF NOT EXISTS stock_code;")

                # 존재할 수 있는 테이블 제거
                cursor.execute("drop TABLE IF EXISTS stock_code.kospi;")
                cursor.execute("drop TABLE IF EXISTS stock_code.kosdaq;")

                # stock_code스키마 하위에 kospi, kosdaq 테이블을 생성
                cursor.execute("create TABLE stock_code.kospi(code varchar(6) NOT NULL PRIMARY KEY, name varchar(40) NOT NULL);")
                cursor.execute("create TABLE stock_code.kosdaq(code varchar(6) NOT NULL PRIMARY KEY, name varchar(40) NOT NULL);")

                # stock_code.kospi 테이블 채워넣기
                ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])  # 0: 코스피, 10: 코스닥, 3: ELW, 8: ETF, 50: 코넥스, 4: 뮤추얼펀드, 5: 신주인수권, 6: 리츠, 9: 하이얼펀드, 30: K-PTC
                kospi_code_list = ret.split(';')

                for code in kospi_code_list:
                    name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])
                    cursor.execute("INSERT INTO stock_code.kospi(code, name) VALUES(\'" + code + "\',\'" + name + "\');")

                cursor.execute("SELECT * FROM stock_code.kospi;")

                result = cursor.fetchall()  # type : list
                print(result)

                # stock_code.kosdaq 테이블 채워넣기
                ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["10"])  # 0: 코스피, 10: 코스닥, 3: ELW, 8: ETF, 50: 코넥스, 4: 뮤추얼펀드, 5: 신주인수권, 6: 리츠, 9: 하이얼펀드, 30: K-PTC
                kosdaq_code_list = ret.split(';')

                for code in kosdaq_code_list:
                    name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [code])
                    cursor.execute("INSERT INTO stock_code.kosdaq(code, name) VALUES(\'" + code + "\',\'" + name + "\');")

                cursor.execute("SELECT * FROM stock_code.kosdaq;")

                result = cursor.fetchall()  # type : list
                print(result)


            except Exception as e:
                print("error")
                print(e)

            conn.commit()  # 이게 없으면 실제로 반영이 안됨.
            cursor.close()
            conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    trace = Program()
    app.exec_()