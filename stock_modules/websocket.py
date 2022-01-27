import stock_modules.stock as stock
import json
import websocket
import logging
import _thread
import requests
import time
import signal
import database


class websocketPrice():
    def __init__(self, db):
        # websocket.enableTrace(True)
        signal.signal(signal.SIGQUIT, self.stopthread)
        signal.signal(signal.SIGINT, self.stopthread)
        signal.signal(signal.SIGTERM, self.stopthread)
        self.db = db
        self.stocks_hose = []
        self.stocks_hnx = []
        self.stocks_upcom = []
        self.stocks = {}
        defaultAllStocks = requests.get('https://iboard.ssi.com.vn/dchart/api/1.1/defaultAllStocks').json()
        for stock_val in defaultAllStocks['data']:
            if (stock_val['stockNo'] != ''):
                if (stock_val['exchange'] == 'HOSE'):
                    self.stocks_hose.append(stock_val['stockNo'])
                elif (stock_val['stockNo'] != '' and stock_val['exchange'] == 'HXN'):
                    self.stocks_hnx.append(stock_val['stockNo'])
                elif (stock_val['stockNo'] != '' and stock_val['exchange'] == 'HXN'):
                    self.stocks_upcom.append(stock_val['stockNo'])
                stockobj = stock.Stock()
                stockobj.load_default(stock_val)
                self.db.stockUpdate(stockobj.stockNo, stockobj, overwrite=False)
                #  đẩy vô database -> update

        self.ws = websocket.WebSocketApp("wss://pricestream-iboard.ssi.com.vn/realtime",
                                on_open=self.on_open,
                                on_message=self.on_message,
                                on_error=self.on_error,
                                on_close=self.on_close)
        self.ws.keep_running = True

    def run(self):
        self.stop = False
        while not(self.stop):
            self.ws.run_forever()
            logging.info("Reconnecting...")
            time.sleep(3)
            
    def stopthread(self):
        print('Exiting')
        self.stop = True
        self.ws.keep_running = False
        
    def subscribe(self):
        req_hose = {
            'type': 'sub',
            'topic': 'stockRealtimeByList',
            'variables' : self.stocks_hose
        }        
        req_hnx = {
            'type': 'sub',
            'topic': 'stockRealtimeByList',
            'variables' : self.stocks_hnx
        }       
        req_upcom = {
            'type': 'sub',
            'topic': 'stockRealtimeByList',
            'variables' : self.stocks_upcom
        }
        #self.ws.send('{"type":"sub","topic":"notifySessionByList","variables":{"markets":["hose","hnx","upcom"]}}') 
        #self.ws.send('{"type":"sub","topic":"notifyIndexRealtimeByList","variables":["VNINDEX","VN30","HNX30","HNXIndex","ESTVN30","HNXUpcomIndex","VNXALL"]}') 
        self.ws.send(json.dumps(req_hose))
        self.ws.send(json.dumps(req_hnx))
        self.ws.send(json.dumps(req_upcom))

    def on_open(self, ws):
        _thread.start_new_thread(self.subscribe, ())

    def on_error(self, ws, error):
        logging.error(error)

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(f"{close_status_code}: {close_msg}")

    def on_message(self, ws, message):
        if (message[0] == 'S' and message[1] == '#'):
            message = message[2:]
            obj = message.split("|")
            currentData = self.db.stockRead(obj[0])
            if (currentData is not None):
                del currentData['_id']
                inputStock = stock.Stock()
                inputStock.from_json(currentData)
                inputStock.update_from_message(obj)
                self.db.stockUpdate(inputStock.stockNo, inputStock, overwrite=True)
            else:
                inputStock = stock.Stock()
                inputStock.update_from_message(obj)
                self.db.stockUpdate(inputStock.stockNo, inputStock, overwrite=True)

                

