#실행하면 오늘까지의 데이터를 받아옴.

import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time
import psycopg2
from datetime import datetime

host = "localhost"
user = "postgres"
dbname = "stockdb"      #사용할 데이터베이스 이름
password = "emote164"   #설치할 때 지정한 것
port = "9003"           #설치할 때 지정할 것

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)


#세팅설정
MODE = "kospi" # kosdaq으로 지정하면 코드닥에 대한 데이터도 처리가능하다.
STANDARD_DATE = datetime.today().strftime("%Y%m%d") #오늘날짜
TR_REQ_TIME_INTERVAL = 0.5

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()
        self.req_stock_code = ""    #실행중에는 현재 작업중인 주식코드를 저장하고 있음.
        self.isHappendError = False

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    #발생한 이벤트를 처리할 함수를 맵핑해주는 함수.
    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._event_receive_tr_data)

    # 로그인 요청 후 결과 이벤트를 받을 수 있는 루프를 생성해주는 함수.
    def comm_connect(self):
        self.dynamicCall("CommConnect()")       # 로그인창을 띄우는 함수 호출
        self.login_event_loop = QEventLoop()    # QEventLoop는 키움증권 서버에서 보내오는 이벤트를 모두 처리할 수 있는듯 하다.
        self.login_event_loop.exec_()           # 여기서는 OnEventConnect를 감시하고자 한다.

    #로그인 이벤트를 처리하는 함수.
    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()            # 사용되어 필요없는 이벤트 루프를 종료한다.

    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    # 데이터에서 하나씩 뽑아서 반환해주는 함수.
    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString", code, real_type, field_name, index, item_name)
        return ret.strip()

    # 요청을 보낸뒤 결과 이벤트를 받을 수 있는 루프를 생성해주는 함수.
    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)  # 서버에 데이터를 요청한다.
        self.tr_event_loop = QEventLoop()   # QEventLoop는 키움증권 서버에서 보내오는 이벤트를 모두 처리할 수 있는듯 하다.
        self.tr_event_loop.exec_()          # 여기서는 OnReceiveTrData 이벤트를 감시하고자 한다.

    # OnReceiveTrData이벤트가 발생하면 불리는 함수.
    def _event_receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        # 받은 데이터를 하나씩 읽는 함수에 전달
        # 여러 종류의 TR을 요청해도 모두 이 메서드 내에서 처리해야한다.
        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)
        '''
        if  rqname == "opt10082_req":
            self._opt10082(rqname, trcode)
        '''

        try:
            self.tr_event_loop.exit()       # 사용되어 필요없는 이벤트 루프를 종료한다.
        except AttributeError:
            pass

    #받아온 데이터를 한개씩 읽는 함수.
    def _opt10081(self, rqname, trcode):
        # ex) rqname : "opt10081_req"
        # ex) trcode : "opt10081"
        data_cnt = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)      # 데이터를 받을 때 몇개의 데이터가 왔는지 반환해주는 함수.

        try:
            conn = psycopg2.connect(conn_string)
            print("연결성공")
            cursor = conn.cursor()

            # stock_code.kospi 테이블의 레코드를 모두 가져옴
            #cursor.execute("select * FROM stock_code." + MODE + ";")
            #self.code_name_list = cursor.fetchall()  # type : 튜플로 이루어진 list

            for i in range(data_cnt):
                date = self._comm_get_data(trcode, "", rqname, i, "일자")
                open = self._comm_get_data(trcode, "", rqname, i, "시가")
                high = self._comm_get_data(trcode, "", rqname, i, "고가")
                low = self._comm_get_data(trcode, "", rqname, i, "저가")
                close = self._comm_get_data(trcode, "", rqname, i, "현재가")
                volume = self._comm_get_data(trcode, "", rqname, i, "거래량")
                money = self._comm_get_data(trcode, "", rqname, i, "거래대금")
                print(date, self.req_stock_code, open, high, low, close, volume, money)
                cursor.execute("insert INTO stock_"+ MODE +".daily_price(code, date, open, low, high, close, count, money) VALUES(\'" + self.req_stock_code + "\',\'" + date + "\',\'" + open + "\',\'" + high + "\',\'" + low + "\',\'" + close + "\',\'" + volume + "\',\'" + money + "\');")
                conn.commit()  # 이게 없으면 실제로 반영이 안됨.

        except Exception as e:
            print("error")
            print(e)
            self.isHappendError = True
            print("이미 존재하는 데이터 발견")

        conn.commit()  # 이게 없으면 실제로 반영이 안됨.
        cursor.close()
        conn.close()

    #넣어야할 데이터를 모두 넣었다면 stock_code.kospi 또는 stock_code.kosdaq의 isUpdated column값을 true로 세트해준다.
    def fill_o_r_date(self):
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()

            cursor.execute("SELECT MIN(date) FROM stock_"+ MODE +".daily_price WHERE code = \'" + self.req_stock_code + "\'")
            oDate = cursor.fetchall()  # type : list
            cursor.execute("SELECT MAX(date) FROM stock_"+ MODE +".daily_price WHERE code = \'" + self.req_stock_code + "\'")
            rDate = cursor.fetchall()  # type : list

            if(oDate[0][0] != -1 and rDate[0][0] != -1):
                cursor.execute("update stock_code." + MODE + " SET odate = \'" + str(oDate[0][0]) + "\' WHERE code = \'" + self.req_stock_code + "\';")
                cursor.execute("update stock_code." + MODE + " SET rdate = \'" + str(rDate[0][0]) + "\' WHERE code = \'" + self.req_stock_code + "\';")
            else:
                cursor.execute("update stock_code." + MODE + " SET rdate = \'" + str(rDate[0][0]) + "\' WHERE code = \'" + self.req_stock_code + "\';")

        except Exception as e:
            print("error")
            print(e)

        conn.commit()  # 이게 없으면 실제로 반영이 안됨.
        cursor.close()
        conn.close()

    #stock_code.X 테이블에서 odate, rdate가 -1인 애들을 리스트로 리턴해줌.
    def getTotalCode(self):
        try:
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute("select code FROM stock_code." + MODE +";")
            codeList = cursor.fetchall()  #업데이트 안된 코드들만 뽑아냄
        except Exception as e:
            print("error")
            print(e)
            print(type(e))

        cursor.close()
        conn.close()
        return codeList

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    for item in kiwoom.getTotalCode():
        kiwoom.req_stock_code = item[0]
        kiwoom.set_input_value("종목코드", kiwoom.req_stock_code)
        kiwoom.set_input_value("기준일자", STANDARD_DATE)
        kiwoom.set_input_value("수정주가구분", 0)                      # 0: ?, 1: 유상증자, 2: 무상증자, 4: 배당락, 8: 액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락
        kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")   # 요청 // 세 번째인자가 0일때 한번조회

        while (kiwoom.remained_data == True) and (kiwoom.isHappendError == False):
            time.sleep(TR_REQ_TIME_INTERVAL)
            kiwoom.set_input_value("종목코드", kiwoom.req_stock_code)
            kiwoom.set_input_value("기준일자", STANDARD_DATE)
            kiwoom.set_input_value("수정주가구분", 0)
            kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101") # 요청 // 세 번째인자가 2일때 연속조회

        kiwoom.fill_o_r_date()  # 정상적으로 다 입력한 테이블은 odate와 rdate 갱신
        kiwoom.isHappendError == False

        print("연속조회 완료")