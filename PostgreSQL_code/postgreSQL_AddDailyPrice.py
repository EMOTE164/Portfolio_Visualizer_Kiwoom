# opt10081을 이용해 stock_kospi.daily_price, stock_kosdaq.daily_price 테이블을 채움

import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import time
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
        self.kiwoom.OnReceiveTrData.connect(self.receiveTrData)
        self.code_name_list = []
        self.code_name_list_currentIndex = 0

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
                cursor.execute("create SCHEMA IF NOT EXISTS stock_kospi;")
                cursor.execute("create SCHEMA IF NOT EXISTS stock_kosdaq;")

                # 존재할 수 있는 테이블 제거
                cursor.execute("drop TABLE IF EXISTS stock_kospi.daily_price;")
                cursor.execute("drop TABLE IF EXISTS stock_kosdaq.daily_price;")

                # stock_code스키마 하위에 kospi, kosdaq 테이블을 생성
                cursor.execute("create TABLE stock_kospi.daily_price(code varchar(6) NOT NULL REFERENCES stock_code.kospi(code), date varchar(20) NOT NULL, open integer, low integer, high integer, close integer, volumeCount integer, volumeMoney integer, PRIMARY KEY(code, date));")
                cursor.execute("create TABLE stock_kosdaq.daily_price(code varchar(6) NOT NULL REFERENCES stock_code.kosdaq(code), date varchar(20) NOT NULL, open integer, low integer, high integer, close integer, volumeCount integer, volumeMoney integer, PRIMARY KEY(code, date));")

                # stock_code.kospi 테이블의 레코드를 모두 가져옴
                cursor.execute("select * FROM stock_code.kospi;")
                self.code_name_list = cursor.fetchall()  # type : 튜플로 이루어진 list


            except Exception as e:
                print("error")
                print(e)

            conn.commit()  # 이게 없으면 실제로 반영이 안됨.
            cursor.close()
            conn.close()

            self.requestTrData(0)  # 로그인 성공이 확인된 후에만 요청을 할 수 있다.

    def requestTrData(self, c):
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.code_name_list[self.code_name_list_currentIndex][0])  # 종목코드
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", "20180508")  # 조회할 날짜
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "0")   # 0 or 1, 1: 유상증자, 2: 무상증자, 4: 배당락, 8: 액면불할, 16: 액면병합, 32: 기업합병, 64: 감자, 256: 권리락
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081_req", "opt10081", c, "0766") # 사용사요청명칭 / 요청함수 / 초기조회:0, 연속조회:2 / 화면번호

    def receiveTrData(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10081_req":
            try:
                # 데이터 베이스를 연결하고 db를 선택해줌
                conn = psycopg2.connect(conn_string)
                print("연결성공")

                cursor = conn.cursor()

                print(prev_next)
                for i in range(800): # 한번 요청에 600일의 정보가 들어오는데 혹시몰라서 큰 값으로 잡음.
                    date = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "일자")

                    if (date == ""):
                        break
                    startPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "시가")
                    highPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "고가")
                    lowPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "저가")
                    closePrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가")
                    volumeCount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "거래량")
                    volumeMoney = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "거래대금")

                    print(i, date.strip(), "\t", startPrice.strip(), "\t", highPrice.strip(), "\t", lowPrice.strip(), "\t", closePrice.strip(), "\t", volumeCount.strip(), "\t", volumeMoney.strip())

                # 레코드 삽입                                                                                                                                             #date + "\');
                cursor.execute("insert INTO stock_kospi.daily_price(code, date, open, low, high, close, volumeCount, volumeMoney) VALUES(\'" + self.code_name_list[self.code_name_list_currentIndex][0] + "\',\'" + date + "\',\'" + startPrice + "\',\'" + lowPrice + "\',\'" + highPrice + "\',\'" + closePrice + "\',\'" + volumeCount + "\',\'" + volumeMoney + "\');")


            except Exception as e:
                print("error")
                print(e)


            if (prev_next == '2'):
                print("연속조회")
                time.sleep(0.5)        # !이 딜레이를 없애면 초당 요청 블락에 걸려서 전체 조회가 되지 않는다.!
                self.requestTrData(2)   #연속조회
            else:
                conn.commit()  # 이게 없으면 실제로 반영이 안됨.
                cursor.close()
                conn.close()

                print("조회완료")
                self.code_name_list_currentIndex = self.code_name_list_currentIndex + 1

                if(len(self.code_name_list) < self.code_name_list_currentIndex):
                    self.requestTrData(0)
                #여기서 리퀘스트 0을 다시 부른다.

if __name__ == "__main__":
    app = QApplication(sys.argv)
    trace = Program()
    app.exec_()