from flask import Flask,render_template,request,jsonify,Response
import pymongo
from bson.objectid import ObjectId
import json
import datetime
import os

from dotenv import load_dotenv
app = Flask(__name__)

#mongod

try:

    load_dotenv()  # use dotenv to hide sensitive credential as environment variables
    DATABASE_URL = f'mongodb+srv://user:{os.environ.get("password")}' \
                   '@mongo-heroku-cluster-we.kyrhz.mongodb.net/myFirstDatabase?' \
                   'retryWrites=true&w=majority'  # get connection url from environment

    mongo = pymongo.MongoClient(DATABASE_URL)  # establish connection with database
'''
    mongo = pymongo.MongoClient(
        host="localhost",
        port= 27017
    )
    '''
    db = mongo.d_store6
    mongo.server_info()
except:
    print('cannot cnnect db')

################################### initiate tax details #############################3

@app.route("/",methods=['GET'])
def initiate():
    try:
        print("step1")
        item_category = [{"itemCategory":"medicines","tax":0.05},
                     {"itemCategory": "food", "tax": 0.05},
                     {"itemCategory":"clothes","tax_blw_1000":0.05,"tax_abv_1000":0.12},
                     {"itemCategory":"imported",'tax':0.18},
                     {"itemCategory": "music", "tax":0.03},
                     {"itemCategory":"books","tax":0}]
        dbres = db.itemcategory.insert_many(item_category)

        return Response(response = json.dumps(
        {"message" : "tax details initaited successfully"}),
        status=200,
        mimetype = "application/json"
        )
    except Exception as ex:
        print(ex)
        return Response(response=json.dumps(
            {"message": "cannot calculate total price"}),
            status=500,
            mimetype="application/json"
        )
##########################################   purchase item  #############################

@app.route("/buy",methods=['POST'])
def createuser():
    try:
        req = request.get_json()
        sum = 0
        sum_percen= 0
        total_sumprcent = 0
        discount = 0
        for vals in req:
           sum += vals['price']
           #vals['total_price'] = sum
           #dbres = db.users.insert_one(vals)
           db_res = db.itemcategory.find({"itemCategory": vals['itemCategory']})
           for cgory in db_res:
               print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
               if cgory['itemCategory'] == "food" or cgory['itemCategory'] == "medicines":
                   sum_percen = vals['price'] * cgory['tax']
               elif cgory['itemCategory'] == "import":
                   sum_percen = vals['price'] * cgory['tax']
               elif cgory['itemCategory'] == "music":
                   print(sum,"sum sum sum sum")
                   sum_percen = vals['price'] * cgory['tax']
                   print(sum_percen,"sum_percensum_percensum_percensum_percen")
               elif cgory['itemCategory'] == "cloths":
                   if vals['price'] <1000 :
                       sum_percen = vals['price'] * cgory["tax_blw_1000"]
                   else:
                       sum_percen = vals['price'] * cgory["tax_abv_1000"]
               else:
                   print(cgory['tax'])
                   sum_percen = cgory['tax']
               total_sumprcent += sum_percen
        t_price = total_sumprcent+sum
        ################calculate discount ####################
        if t_price >= 2000:
            discount = t_price*0.05
            discount_price = t_price - discount
        purchase_time = datetime.datetime.now()
        dict_app = {"total_price":sum,"discount":discount,"total_tax":total_sumprcent,"discount_price":discount_price,"purchase_time":purchase_time}
        d_copy = dict_app.copy()
        req.append(d_copy)
        dbres = db.users.insert_one({"list":req})
        return jsonify({"total_price":sum,"total_tax":total_sumprcent,"discount":discount,"discount_price":discount_price,"purchase_time":purchase_time})
    except Exception as ex:
        print(ex)
        return Response(response=json.dumps(
            {"message": "cannot calculate total price"}),
            status=500,
            mimetype="application/json"
        )

################################## get user purchase items ##################################################

@app.route("/user/<id>",methods=['GET','POST'])
def home(id):
    try:
        objinst = ObjectId(id)
        db_resp = db.users.find_one({'_id':objinst})
        return jsonify({"list":db_resp['list']})

    except Exception as ex:
        print(ex)
        return Response(response=json.dumps(
            {"message": "cannot find user details"}),
            status=500,
            mimetype="application/json"
        )

if __name__ == "__main__":
    app.run(debug=True)