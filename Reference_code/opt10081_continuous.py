import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time

TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

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

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()            # 사용되어 필요없는 이벤트 루프를 종료한다.

    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

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

        for i in range(data_cnt):
            date = self._comm_get_data(trcode, "", rqname, i, "일자")
            open = self._comm_get_data(trcode, "", rqname, i, "시가")
            high = self._comm_get_data(trcode, "", rqname, i, "고가")
            low = self._comm_get_data(trcode, "", rqname, i, "저가")
            close = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")
            print(date, open, high, low, close, volume)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()

    # opt10081 TR 요청
    kiwoom.set_input_value("종목코드", "039490")
    kiwoom.set_input_value("기준일자", "20170224")
    kiwoom.set_input_value("수정주가구분", 1)
    kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")      # 세번째인자가 0일때 한번조회

    while kiwoom.remained_data == True:
        time.sleep(TR_REQ_TIME_INTERVAL)
        kiwoom.set_input_value("종목코드", "039490")
        kiwoom.set_input_value("기준일자", "20170224")
        kiwoom.set_input_value("수정주가구분", 1)
        kiwoom.comm_rq_data("opt10081_req", "opt10081", 2, "0101")  # 세번째인자가 2일때 연속조회

    print("연속조회 완료")