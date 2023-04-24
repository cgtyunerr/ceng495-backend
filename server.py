from bson import ObjectId, json_util
from flask import Flask, jsonify, request
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import json

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'c92885cf58a3cff297a1b80e9ff8a233'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
jwt = JWTManager(app)
uri = "mongodb+srv://cgtyuner:ceng495hw1@cgtyuner.ow1tmh7.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client['ceng495hw1']
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)  # ObjectId'yi stringe dönüştürün
        return json.JSONEncoder.default(self, obj)
app.json_encoder = CustomJSONEncoder


@app.route('/sign-up', methods=['POST'])
def signup():
    username = request.json.get('username')
    password = request.json.get('password')
    user_type = request.json.get('user_type')
    db.get_collection(name="users").insert_one(
        {"username": username, "password": password, "total_rating": 0, "number_of_rating": 0, "reviews": [],
         "user_type": user_type})
    response = jsonify({'status': 'Ok'})
    response.status_code = 200
    return response


@app.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    username = get_jwt_identity()
    user = db.get_collection("users").find_one({"username": username})
    if user is None:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    user_map = json.loads(json.dumps(user, default=str))
    response = jsonify({"data": user_map})
    response.status_code = 200
    return response


@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = db.users.find_one({'username': username, 'password': password})
    if user:
        token = create_access_token(identity=username)
        response = jsonify({'token': token})
        response.status_code = 200
        return response
    else:
        response = jsonify({'error': 'username or password is wrong !'})
        response.status_code = 401
        return response


@app.route('/admin/user', methods=['POST'])
@jwt_required()
def add_user():
    username = get_jwt_identity()
    user = db.get_collection("users").find_one({"username": username})
    if user is None:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    if user["user_type"] == "admin":
        username = request.json.get('username')
        password = request.json.get('password')
        user_type = request.json.get('user_type')
        result = db.get_collection(name="users").find_one({'username': username})
        if result is None:
            db.get_collection(name="users").insert_one(
                {"username": username, "password": password, "total_rating": 0, "number_of_rating": 0, "reviews": [],
                 "user_type": user_type})
            response = jsonify({'status': 'Ok'})
            response.status_code = 200
            return response
        else:
            response = jsonify({'error': 'This username already exists !'})
            response.status_code = 409
            return response
    else:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response


@app.route('/admin/delete-user/<username>', methods=['DELETE'])
@jwt_required()
def delete_user(username):
    username1 = get_jwt_identity()
    user = db.get_collection("users").find_one({"username": username1})
    if user is None:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    if user['user_type'] == "admin":
        result = db.get_collection(name="users").delete_one({"username": username})
        if result.deleted_count == 1:
            reviews = db.get_collection("users").find({"username": username}, {"reviews": 1})
            for review in reviews:
                db.get_collection("items").update_one({'_id': review['item_id']},
                                                      {'$pull': {'reviews': {'username': username}}})
            response = jsonify({'status': 'User with name {} was deleted'.format(username)})
            response.status_code = 200
            return response
        else:
            response = jsonify({'error': 'user not found !'})
            response.status_code = 404
            return response
    else:
        response = jsonify({'error': 'unauthorized'})
        response.status_code = 401
        return response


@app.route('/admin/item', methods=['POST'])
@jwt_required()
def add_item():
    username = get_jwt_identity()
    user = db.get_collection("users").find_one({"username": username})
    if user is None:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    if user['user_type'] == "admin":
        item_type = request.json.get('item_type')
        description = request.json.get('description')
        price = request.json.get('price')
        seller = request.json.get('seller')
        image = request.json.get('image')
        name = request.json.get('name')
        if item_type == "clothing":
            size = request.json.get('size')
            color = request.json.get('color')
            db.get_collection("items").insert_one(
                {"item_type": item_type, "name": name, "description": description, "price": price, "seller": seller,
                 "image": image, "spec": None, "size": size, "color": color, "total_point": 0, "pointers": 0,
                 "reviews": []})
            response = jsonify({'status': 'The item was uploaded successfully.'})
            response.status_code = 200
            return response
        elif item_type == "computer_components":
            spec = request.json.get('spec')
            db.get_collection("items").insert_one(
                {"item_type": item_type, "name": name, "description": description, "price": price, "seller": seller,
                 "image": image, "spec": spec, "size": None, "color": None, "total_point": 0, "pointers": 0,
                 "reviews": []})
            response = jsonify({'status': 'The item was uploaded successfully.'})
            response.status_code = 200
            return response
        elif item_type == "monitors":
            spec = request.json.get('spec')
            db.get_collection("items").insert_one(
                {"item_type": item_type, "name": name, "description": description, "price": price, "seller": seller,
                 "image": image, "spec": spec, "size": None, "color": None, "total_point": 0, "pointers": 0,
                 "reviews": []})
            response = jsonify({'status': 'The item was uploaded successfully.'})
            response.status_code = 200
            return response
        elif item_type == "snacks":
            db.get_collection("items").insert_one(
                {"item_type": item_type, "name": name, "description": description, "price": price, "seller": seller,
                 "image": image, "spec": None, "size": None, "color": None, "total_point": 0, "pointers": 0,
                 "reviews": []})
            response = jsonify({'status': 'The item was uploaded successfully.'})
            response.status_code = 200
            return response
    else:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    response = jsonify({'error': 'An unknown error was happened !'})
    response.status_code = 409
    return response


@app.route('/admin/item/<item_id>', methods=['DELETE'])
@jwt_required()
def remove_item():
    username = get_jwt_identity()
    user = db.get_collection("users").find_one({"username": username})
    if user is None:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response
    if user['type'] == "admin":
        item_id = request.args.get("item_id")
        result = db.get_collection("items").delete_one({"_id": item_id})
        if result.deleted_count != 0:
            reviews = db.get_collection("items").find({"_id": item_id}, {"reviews": 1})
            for review in reviews:
                db.get_collection("users").update_one({'username': review['username']},
                                                      {'$pull': {'reviews': {'item_id': item_id}}})
            response = jsonify({'status': 'The item was removed successfully.'})
            response.status_code = 200
            return response
        else:
            response = jsonify({'error': 'The item was not found !'})
            response.status_code = 404
            return response
    else:
        response = jsonify({'error': 'Unauthorized.'})
        response.status_code = 401
        return response


@app.route('/admin/users', methods=['GET'])
@jwt_required()
def get_users():
    username = get_jwt_identity()
    user = db.get_collection("users").find_one({"username": username})
    if user is not None and user['user_type'] == "admin":
        users = db.get_collection("users").find()
        user_list = []
        for user in users:
            user_map = json.loads(json.dumps(user, default=str))
            user_list.append(user_map)
        response = jsonify({"data": user_list})
        response.status_code = 200
        return response
    else:
        response = jsonify({"error": "Unauthorized"})
        response.status_code = 401
        return response


@app.route('/item/details', methods=['GET'])
def item_details():
    item_id = request.args.get("item_id")
    username = request.args.get("username")
    item = db.get_collection("items").find_one({'_id': ObjectId(item_id)})
    if item is not None:
        review = db.get_collection("users").find_one({'username': username, 'reviews': {'$elemMatch':
                                                            {'item_id': ObjectId('6446a5e285a6036d93cfdb2c')}}})
        if review is None:
            response = jsonify(
                {'data': {"item_id": item['_id'], "item_type": item['item_type'], "name": item['name'],
                          "description": item['description'],
                          "price": item['price'], "seller": item['seller'], "image": item['image'],
                          "size": item['size'],
                          "color": item['color'], "spec": item['spec'], "total_point": item['total_point'],
                          "pointers": item['pointers'], "reviews": item['reviews'], "rate": 0,
                          "comment": ""},
                 'status': 'OK'})
            response.status_code = 200
            return response
        else:
            response = jsonify(
                {'data': {"item_type": item['item_type'], "name": item['name'], "description": item['description'],
                          "price": item['price'], "seller": item['seller'], "image": item['image'],
                          "size": item['size'],
                          "color": item['color'], "spec": item['spec'], "total_point": item['total_point'],
                          "pointers": item['pointers'], "reviews": item['reviews'], "rate": review['rate'],
                          "comment": review['comment']},
                 'status': 'OK'})
            response.status_code = 200
            return response
    else:
        response = jsonify({'error': 'The item not found !'})
        response.status_code = 404
        return response


@app.route('/item/rate', methods=['POST'])
@jwt_required()
def rate_item():
    username = get_jwt_identity()
    user = db.get_collection("users").find_one({"username": username})
    if user is not None:
        old_rate = request.json.get['old_rate']
        new_rate = request.json.get['new_rate']
        total_point = request.json.get['total_point']
        item_id = request.json.get['item_id']
        db.get_collection("items").update_one({"_id": item_id}, {"total_point": total_point - old_rate + new_rate})
        review = db.get_collection("users").find_one({'username': username, 'reviews': {'$elemMatch':
                                                                                            {'item_id': item_id}}})
        if review is not None:
            db.get_collection("users").update_one({"username": username, "reviews.item_id": item_id},
                                                  {'$set': {'reviews.$.rate': new_rate}})
            db.get_collection("items").update_one({"_id": item_id, "reviews.username": username},
                                                  {'$set': {'reviews.$.rate': new_rate}})
        elif review in None:
            db.get_collection("users").update_one({"username": username},
                                                  {'$push': {"reviews": {"item_id": item_id, "rate": new_rate,
                                                                         "comment": ""}}})
            db.get_collection("items").update_one({"_id": item_id},
                                                  {'$push': {"reviews": {"username": username, "rate": new_rate,
                                                                         "comment": ""}}})
        if old_rate == 0:
            db.get_collection("items").update_one({"_id": item_id}, {'$inc': {'pointers': 1}})
        response = jsonify({'status': 'OK'})
        response.status_code = 200
        return response
    else:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response


@app.route('/make-review', methods=['POST'])
@jwt_required()
def make_review():
    username = get_jwt_identity()
    user = db.get_collection("users").find_one({"username": username})
    if user is not None:
        item_id = request.json.get('item_id')
        comment = request.json.get('comment')
        review = db.get_collection("users").find_one({'username': username, 'reviews': {'$elemMatch':
                                                                                            {'item_id': item_id}}})
        if review is None:
            db.get_collection("users").update_one({"username": username},
                                                  {'$push': {"reviews": {"item_id": item_id, "rate": 0,
                                                                         "comment": comment}}})
            db.get_collection("items").update_one({"_id": item_id},
                                                  {'$push': {"reviews": {"username": username, "rate": 0,
                                                                         "comment": comment}}})
            response = jsonify({'status': 'The review is saved successfully.'})
            response.status_code = 200
            return response
        else:
            db.get_collection("users").update_one({"username": username, "reviews.item_id": item_id},
                                                  {'$set': {'reviews.$.comment': comment}})
            db.get_collection("items").update_one({"_id": item_id, "reviews.username": username},
                                                  {'$set': {'reviews.$.comment': comment}})
            response = jsonify({'status': 'The review was changed successfully.'})
            response.status_code = 200
            return response
    else:
        response = jsonify({'error': 'Unauthorized'})
        response.status_code = 401
        return response


@app.route('/items', methods=['GET'])
def get_items():
    items = list(db.get_collection("items").find({}, {'_id': 1, 'name': 1,'description': 1, 'image': 1,
                                                          'price': 1, 'item_type': 1}))
    item_list = []
    for item in items:
        item_map = json.loads(json.dumps(item, default=str))
        item_list.append(item_map)
    response = jsonify({'status': 'Ok', 'data': item_list})
    response.status_code = 200
    return response


if __name__ == "__main__":
    app.run(debug=True)
