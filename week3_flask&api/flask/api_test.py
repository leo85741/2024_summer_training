from flask import Flask, request, jsonify, render_template
from flask_restful import Resource, Api   #繼承Resource，改寫其function
from pymongo import MongoClient
from pymongo import errors
import json
import traceback
from bson import json_util
from bson import ObjectId
from text_analysis import text_analysis
from api_dash import dash_app

app = Flask(__name__)
dash = dash_app(app)
api = Api(app)

# MongoDB連接設定
# uri = "mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1"

# try:
#     client = MongoClient(uri)
    
#     db = client['2024_training'] #client_db
#     collection = db['youqi'] # db_collection
    
# except errors.ConnectionFailure as err:
#     print(err)


class show(Resource):
    def get(self):
        try:
            # Connect to MongoDB
            client = MongoClient('mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1')
            db = client['2024_training']
            collection = db['youqi']
            
            data=collection.find({},{'_id':0})
            data=[i for i in data]

            return json.dumps(data)
        
        except errors.ConnectionFailure as err:
            print(err)
        
class process(Resource):
    def post(self):
        try:

            user_info = request.json
            print(f"Received user info: {user_info}")

            # 連接MongoDB
            client = MongoClient('mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1')
            db = client['2024_training'] #client_db
            collection = db['youqi'] # 

            collection.insert_one({
            'name':user_info['name'],
            'star':user_info['star'],
            'comment_time':user_info['comment_time'],
            'comment':user_info['comment']
            })


            return "insert success!"

        except errors.ConnectionFailure as err:
            print(err)

class process_by_name(Resource):
    def delete(self, name):
        try:
            # 連接MongoDB
            client = MongoClient('mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1')
            db = client['2024_training'] #client_db
            collection = db['youqi'] # 
            
            collection.delete_one({"name":name})

            return  {"message : Delete success!"}
        except Exception as err:
            print(err)

    
    def put(self, name):
        try:
            user_info = request.json
            print(f"Received user info: {user_info}")

            # 連接MongoDB
            client = MongoClient('mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1')
            db = client['2024_training']
            collection = db['youqi']

            # 使用 $set 操作符來更新指定欄位
            result = collection.update_one(
                {"name": name},
                {"$set": {
                    "name": user_info['name'],
                    "star": user_info['star'],
                    "comment_time": user_info['comment_time'],
                    "comment": user_info['comment']
                }}
            )

            if result.matched_count == 0:
                return {"message": "No document found with the given name."}, 404

            return {"message": "Update success!"}
        except errors.ConnectionFailure as err:
            print(err)
        


    def get(self, name):
        try:
            # 連接MongoDB
            client = MongoClient('mongodb://training:Bkmsz3024@192.168.31.89:30241/?authSource=2024_training&authMechanism=SCRAM-SHA-1')
            db = client['2024_training'] #client_db
            collection = db['youqi'] # db_collection

            data=collection.find({'name':name},{'_id':0})
            data=[i for i in data]

            return json.dumps(data)
        
        except errors.ConnectionFailure as err:
            print(err)
        

class MonthlyStar(Resource):
    def get(self):
        analysis = text_analysis()
        star_data = analysis.monthly_star()
        return jsonify(star_data.to_dict(orient='records'))

class MonthlyComment(Resource):
    def get(self):
        analysis = text_analysis()
        comment_data = analysis.monthly_comment()
        return jsonify(comment_data.to_dict(orient='records'))

class MonthlySentiment(Resource):
    def get(self):
        analysis = text_analysis()
        sentiment_data = analysis.monthly_sentiment()
        return jsonify(sentiment_data.to_dict(orient='records'))

class WordCloud(Resource):
    def get(self):
        analysis = text_analysis()
        word_count = analysis.word_cloud()
        return jsonify(word_count.to_dict(orient='records'))
    
class Correlation(Resource):
    def get(self):
        analysis = text_analysis()
        corr = analysis.get_correlation()
        return jsonify(corr.to_dict(orient='records'))

@app.route('/')
def index():
    return render_template('index.html')


# 加入路徑
api.add_resource(show, '/data/users')
api.add_resource(process, '/data/user')
api.add_resource(process_by_name, '/data/user/<string:name>')
api.add_resource(MonthlyStar, '/monthly_star')
api.add_resource(MonthlyComment, '/monthly_comment')
api.add_resource(MonthlySentiment, '/monthly_sentiment')
api.add_resource(WordCloud, '/wordcloud')
api.add_resource(Correlation, '/correlation')

if __name__ == '__main__':
    app.run(debug=True, port=8000)


