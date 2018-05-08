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
MODE = "kospi" # kosdaq으로 지정하면 코드닥에 대한 데이터도 처리가능하다.


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
        self.currentCodeRecentDate = ""

    # 로그인창에서 아이디와 패스워드가 맞으면 불리는 함수
    def receiveLoginEvent(self, err_code):
        if err_code == 0:
            print("로그인 성공")

            try:
                # 데이터 베이스를 연결하고 db를 선택해줌
                conn = psycopg2.connect(conn_string)
                print("연결성공1")

                cursor = conn.cursor()

                # stock_code.kospi 테이블의 레코드를 모두 가져옴
                cursor.execute("select * FROM stock_code." + MODE + ";")
                self.code_name_list = cursor.fetchall()  # type : 튜플로 이루어진 list

            except Exception as e:
                print("error")
                print(e)
            cursor.close()
            conn.close()

            self.requestTrData(0)  # 로그인 성공이 확인된 후에만 요청을 할 수 있다.

    def requestTrData(self, c):

        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.code_name_list[self.code_name_list_currentIndex][0])  # 종목코드
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", "19900508")  # 조회할 날짜
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "0")  # 0 or 1, 1: 유상증자, 2: 무상증자, 4: 배당락, 8: 액면불할, 16: 액면병합, 32: 기업합병, 64: 감자, 256: 권리락
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10081_req", "opt10081", c, "0766")  # 사용사요청명칭 / 요청함수 / 초기조회:0, 연속조회:2 / 화면번호

        if (c == 0):
            try:
                # 데이터 베이스를 연결하고 db를 선택해줌
                conn = psycopg2.connect(conn_string)
                print("연결성공2")

                cursor = conn.cursor()

                cursor.execute("select date FROM stock_kospi.daily_price where code = \'" +
                               self.code_name_list[self.code_name_list_currentIndex][0] + "\' ORDER BY date DESC;")
                result = cursor.fetchall()  # type : list

                if (len(result) > 0):
                    self.currentCodeRecentDate = str(result[0]).replace('(', '').replace(')', '').replace(',', '')
                else:
                    self.currentCodeRecentDate = ""

            except Exception as e:
                print("error")
                print(e)




    def receiveTrData(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):

        isMustStop = False

        if rqname == "opt10081_req":
            try:
                # 데이터 베이스를 연결하고 db를 선택해줌
                conn = psycopg2.connect(conn_string)
                print("연결성공2")

                cursor = conn.cursor()

                print(prev_next)
                for i in range(600): # 한번 요청에 600일의 정보가 들어오는데 혹시몰라서 큰 값으로 잡음.
                    date = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "일자").strip()

                    if (date == ""):
                        break
                    startPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "시가").strip()
                    highPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "고가").strip()
                    lowPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "저가").strip()
                    closePrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가").strip()
                    volumeCount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "거래량").strip()
                    volumeMoney = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "거래대금").strip()

                    print(i, date, "\t", startPrice, "\t", highPrice, "\t", lowPrice, "\t", closePrice, "\t", volumeCount, "\t", volumeMoney)

                    # 테이블에 이미 존재하는 날짜의 데이터를 테이블에 입력하려고 한다면 동작을 그만하여도 됨.
                    if(self.currentCodeRecentDate == date):
                        isMustStop = True
                        break

                    # 레코드 삽입                                                                                                                                             #date + "\');
                    cursor.execute("insert INTO stock_kospi.daily_price(code, date, open, low, high, close, volumeCount, volumeMoney) VALUES(\'" + self.code_name_list[self.code_name_list_currentIndex][0] + "\',\'" + date + "\',\'" + startPrice + "\',\'" + lowPrice + "\',\'" + highPrice + "\',\'" + closePrice + "\',\'" + volumeCount + "\',\'" + volumeMoney + "\');")

                conn.commit()  # 이게 없으면 실제로 반영이 안됨.

            except Exception as e:
                print("error")
                print(e)


            if (prev_next == '2' and isMustStop == False):
                print(str(self.code_name_list_currentIndex) + "조회 중")
                print("연속조회")
                time.sleep(0.5)        # !이 딜레이를 없애면 초당 요청 블락에 걸려서 전체 조회가 되지 않는다.!
                self.requestTrData(2)   #연속조회
            else:
                cursor.close()
                conn.close()

                print("조회완료")
                # 이때 코드 테이블을 True로 업데이트 해준다.
                #cursor.execute("update stock_code.kospi SET isupdated = True WHERE code = '';")

                self.code_name_list_currentIndex = self.code_name_list_currentIndex + 1


                if(len(self.code_name_list) > self.code_name_list_currentIndex):
                    print(str(self.code_name_list_currentIndex) + ": 새로시작")
                    self.requestTrData(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    trace = Program()
    app.exec_()