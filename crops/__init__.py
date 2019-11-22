import xlrd
from flask import Flask, request, jsonify
import requests 
import os
from urllib.request import urlopen
import json
import time

def getData():
    currDir = os.path.dirname(__file__)
    loc=(os.path.join(currDir,"Book1.xlsx"))
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0) 
    sheet.cell_value(0, 0) 
    temp_dev=[]
    mois_dev=[]
    hum_dev=[]
    sum_dev={}
    c=0
    READ_API_KEY='M5VISQCBDFUWUTBC'
    CHANNEL_ID= '917454'
    TS = urlopen("http://api.thingspeak.com/channels/%s/feeds/last.json?api_key=%s" \
                       % (CHANNEL_ID,READ_API_KEY))

    response = TS.read()
    data=json.loads(response)


    a = data['created_at']
    b = data['field1']
    cc = data['field2']
    d = data['field3']
    print (a + "    " + b + "    " + cc + "    " + d)
    temp_reading = float(b)
    mois_reading = float(d)
    hum_reading = float(cc)
    time.sleep(5)   

    TS.close()
    for i in range(1,sheet.nrows): 
        crop_string=sheet.cell_value(i,0)
        
        temp_string=sheet.cell_value(i, 1)
        temp_lower,temp_upper=map(float,temp_string.split('-'))
        avg_temp=(temp_lower+temp_upper)/2
        if (temp_reading>=temp_lower and temp_reading<=temp_upper):
            temp_dev.append(abs(temp_reading-avg_temp))
        else:
            temp_dev.append(float('inf'))
            
        mois_string=sheet.cell_value(i, 2)
        mois_lower,mois_upper=map(float,mois_string.split('-'))
        avg_mois=(mois_lower+mois_upper)/2
        if (mois_reading>=mois_lower and mois_reading<=mois_upper):
            mois_dev.append(abs(mois_reading-avg_mois))
        else:
            mois_dev.append(float('inf'))
            
        hum_string=sheet.cell_value(i, 3)
        hum_lower,hum_upper=map(float,hum_string.split('-'))
        avg_hum=(hum_lower+hum_upper)/2
        if (hum_reading>=hum_lower and hum_reading<=hum_upper):
            hum_dev.append(abs(hum_reading-avg_hum))
        else:
            hum_dev.append(float('inf'))
        sum_dev[crop_string]=temp_dev[c]+mois_dev[c]+hum_dev[c]
        c+=1
    print("Suggested Crops: ")
    listofCrops = sorted(sum_dev.items() ,  key=lambda x: x[1])
    for elem in listofCrops :
        if(elem[1]!=float('inf')):
            print(elem[0] , " ::" , elem[1] )
    json_data = {"data": listofCrops}
    return json_data
app = Flask(__name__) 



@app.route('/', methods = ['GET'])
def data():
    data = getData()
    return jsonify(data)
  

