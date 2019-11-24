import xlrd
from flask import Flask, request, jsonify
import http.client
import urllib.parse
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


def getData_p():
    READ_API_KEY='M5VISQCBDFUWUTBC'
    CHANNEL_ID= '917454'
    TS = urlopen("http://api.thingspeak.com/channels/%s/feeds/last.json?api_key=%s" \
                       % (CHANNEL_ID,READ_API_KEY))
    response = TS.read()
    data=json.loads(response)
    readings=[]
    b = data['field1']
    cc = data['field2']
    d = data['field3']
    readings.append(b)
    readings.append(cc)
    readings.append(d)
    json_data = {"data": readings}
    return json_data

def write_ts(threshold):
  key = "6QDH75XFDQ7X4XFI" 
  params = urllib.parse.urlencode({'field4': threshold, 'key':key }) 
  headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
  conn = http.client.HTTPConnection("api.thingspeak.com:80")
  try:
    conn.request("POST", "/update", params, headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
  except:
    print ("connection failed")
    
def getData_c(crop_name):
    currDir = os.path.dirname(__file__)
    loc=(os.path.join(currDir,"Book1.xlsx"))
    wb = xlrd.open_workbook(loc) 
    sheet = wb.sheet_by_index(0) 
    sheet.cell_value(0, 0)
    for i in range(1,sheet.nrows): 
        crop_string=sheet.cell_value(i,0)
        if(crop_name==crop_string):
          mois_string=sheet.cell_value(i, 2)
    mois_lower,mois_upper=map(float,mois_string.split('-'))
    timeout = time.time() + 20
    while time.time()<timeout:
        write_ts(mois_lower)
    json_data = {"data":mois_lower}
    return json_data

@app.route('/suggest', methods = ['GET'])
def data():
    data = getData()
    return jsonify(data)
  
@app.route('/present', methods = ['GET'])
def data1():
    data = getData_p()
    return jsonify(data)

@app.route('/', methods = ['GET'])
def data2():
    crop=str(request.args['crop'])
    data = getData_c(crop)
    return jsonify(data)
