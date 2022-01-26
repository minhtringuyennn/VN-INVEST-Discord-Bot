import json

def try_float(x):
    try:
        return round(float(x),2)
    except ValueError:
        return 0
        
class Stock():
    def __init__(self):
        # --- Default Stock Info ---
        self.type = ''
        self.clientName = ''
        self.clientNameEn = ''
        self.code = ''
        self.full_name = ''
        self.name = ''
        self.securityName = ''
        self.stockNo = ''
        # --- Realtime Stock Info ---
        self.bidPrc1 = 0
        self.bidVol1 = 0
        self.bidPrc2 = 0
        self.bidVol2 = 0
        self.bidPrc3 = 0
        self.bidVol3 = 0
        self.askPrc1 = 0
        self.askVol1 = 0
        self.askPrc2 = 0
        self.askVol2 = 0
        self.askPrc3 = 0
        self.askVol3 = 0
        self.matchedPrc = 0
        self.matchedVol = 0
        self.highPrc = 0
        self.exchange = ''
        self.lowPrc = 0
        self.avgPrc = 0
        self.foreginBought = 0
        self.foreginSold = 0
        self.diffPrc = 0
        self.diffPer = 0
        self.totalVol = 0
        self.totalValue = 0
        self.refPrc = 0
        self.session = 0
        self.foreginRoom = 0
    
    def load_default(self, obj):
        self.type = obj['type']
        self.clientName = obj['clientName']
        self.clientNameEn = obj['clientNameEn']
        self.stockNo = obj['stockNo']
        self.code = obj['code']
        self.name = obj['name']
        self.exchange = obj['exchange']
        self.full_name = obj['full_name']
        self.securityName = obj['securityName']

    def update_from_message(self,obj):
        self.stockNo = obj[0] if obj[0] != '' else self.stockNo
        self.code = obj[1] if obj[1] != '' else self.Code
        self.bidPrc1 = try_float(obj[2])/1000 if obj[2] != '' else self.BidPrc1
        self.bidVol1 = try_float(obj[3])/1000 if obj[3] != '' else self.BidVol1
        self.bidPrc2 = try_float(obj[4])/1000 if obj[4] != '' else self.BidPrc2
        self.bidVol2 = try_float(obj[5])/1000 if obj[5] != '' else self.BidVol2
        self.bidPrc3 = try_float(obj[6])/1000 if obj[6] != '' else self.BidPrc3
        self.bidVol3 = try_float(obj[7])/1000 if obj[7] != '' else self.BidVol3
        self.askPrc1 = try_float(obj[22])/1000 if obj[22] != '' else self.AskPrc1
        self.askVol1 = try_float(obj[23])/1000 if obj[23] != '' else self.AskVol1
        self.askPrc2 = try_float(obj[24])/1000 if obj[24] != '' else self.AskPrc2
        self.askVol2 = try_float(obj[25])/1000 if obj[25] != '' else self.AskVol2
        self.askPrc3 = try_float(obj[26])/1000 if obj[26] != '' else self.AskPrc3
        self.askVol3 = try_float(obj[27])/1000 if obj[27] != '' else self.AskVol3
        self.matchedPrc = try_float(obj[42])/1000 if obj[42] != '' else self.MatchedPrc
        self.matchedVol = try_float(obj[43])/100 if obj[43] != '' else self.MatchedVol
        self.highPrc = try_float(obj[44])/1000 if obj[44] != '' else self.HighPrc
        self.exchange = obj[45] if obj[45] != '' else self.Exchange
        self.lowPrc = try_float(obj[46])/1000 if obj[46] != '' else self.LowPrc
        self.avgPrc = round(try_float(obj[47])/1000,2) if obj[47] != '' else self.AvgPrc
        self.foreginBought = try_float(obj[49]) if obj[49] != '' else self.ForeginBought
        self.foreginSold = try_float(obj[51]) if obj[51] != '' else self.ForeginSold
        self.diffPrc = try_float(obj[52])/1000 if obj[52] != '' else self.DiffPrc
        self.diffPer = try_float(obj[53]) if obj[53] != '' else self.DiffPer
        self.totalVol = try_float(obj[54])/1000 if obj[54] != '' else self.TotalVol
        self.totalValue = try_float(obj[55])/1000 if obj[55] != '' else self.TotalValue
        self.refPrc = obj[61] if obj[61] != '' else self.RefPrc
        self.session = obj[63] if obj[63] != '' else self.Session
        self.foreginRoom = try_float(obj[66]) if obj[66] != '' else self.ForeginRoom

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def from_json(self, input):
        self.type = input['type']
        self.clientName = input['clientName']
        self.clientNameEn = input['clientNameEn']
        self.code = input['code']
        self.full_name = input['full_name']
        self.name = input['name']
        self.securityName = input['securityName']
        self.stockNo = input['stockNo']
        self.bidPrc1 = input['bidPrc1']
        self.bidVol1 = input['bidVol1']
        self.bidPrc2 = input['bidPrc2']
        self.bidVol2 = input['bidVol2']
        self.bidPrc3 = input['bidPrc3']
        self.bidVol3 = input['bidVol3']
        self.askPrc1 = input['askPrc1']
        self.askVol1 = input['askVol1']
        self.askPrc2 = input['askPrc2']
        self.askVol2 = input['askVol2']
        self.askPrc3 = input['askPrc3']
        self.askVol3 = input['askVol3']
        self.matchedPrc = input['matchedPrc']
        self.matchedVol = input['matchedVol']
        self.highPrc = input['highPrc']
        self.exchange = input['exchange']
        self.lowPrc = input['lowPrc']
        self.avgPrc = input['avgPrc']
        self.foreginBought = input['foreginBought']
        self.foreginSold = input['foreginSold']
        self.diffPrc = input['diffPrc']
        self.diffPer = input['diffPer']
        self.totalVol = input['totalVol']
        self.totalValue = input['totalValue']
        self.refPrc = input['refPrc']
        self.session = input['session']
        self.foreginRoom = input['foreginRoom']
        