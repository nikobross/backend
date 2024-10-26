import json
from dotenv import load_dotenv
from flask import Flask, request
import db
import hashlib
import os

DB = db.DatabaseDriver()

app = Flask(__name__)

def success_response(body, code=200):
    return json.dumps(body), code

def failure_response(message, code=404):
    return json.dumps({'error': message}), code


@app.route("/")
def hello_world():
    # Route to return a simple greeting
    return "Hello world!"


# your routes here

@app.route("/api/users/", methods=["GET"])
def get_users():
    # Route to get all users
    users = DB.get_all_users()

    # hide the balance of the
    for user in users:
        del user["balance"]

    return success_response({"users": users})

@app.route("/api/users/", methods=["POST"])
def create_user():
    # Route to create a new user
    body = json.loads(request.data)

    if "name" not in body and "username" not in body:
        return failure_response("Name and username are required!", 400)
    elif "username" not in body:
        return failure_response("Username is required!", 400)
    elif "name" not in body:
        return failure_response("Name is required!", 400)

    name = body["name"]
    username = body["username"]
    if "balance" in body:
        balance = body["balance"]
    else:
        balance = 0

    user_id = DB.insert_user(name, username, balance)
    user = DB.get_user_by_id(user_id)

    if user is None:
        return failure_response("Something went wrong while creating user!")
    
    return success_response(user, 201)


@app.route("/api/user/<int:user_id>/", methods=["GET"]) 
def get_user(user_id):
    # Route to get a specific user by ID
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found!")

    return success_response(user)

@app.route("/api/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    # Route to delete a specific user by ID
    user = DB.get_user_by_id(user_id)

    if user is None:
        return failure_response("User not found!")
    DB.delete_user_by_id(user_id)

    return success_response(user)

@app.route("/api/send/", methods=["POST"])
def send_money():
    
    body = json.loads(request.data)

    fields = ["amount", "sender_id", "receiver_id"]
    blank_fields = []
    for field in fields:
        if field not in body:
            blank_fields.append(field)

    if blank_fields:
        return failure_response(f"Fields {blank_fields} are required", 400)

    amount = body["amount"]

    sender_id = body["sender_id"]
    receiver_id = body["receiver_id"]

    sender = DB.get_user_by_id(sender_id)
    receiver = DB.get_user_by_id(receiver_id)

    sender_balance = sender["balance"] - amount
    receiver_balance = receiver["balance"] + amount

    if sender_balance >= 0:
        DB.update_user_by_id(sender_id, sender["name"], 
                             sender["username"], sender_balance)
        DB.update_user_by_id(receiver_id, receiver["name"], 
                             receiver["username"], receiver_balance)
        return success_response(body, 200)
    else:
        return failure_response("Insufficient funds", 400)




# ------EXTRA CREDIT------

load_dotenv()

PASSWORD_SALT = os.getenv('PASSWORD_SALT').encode('utf-8')
NUMBER_OF_ITERATIONS = int(os.getenv('NUMBER_OF_ITERATIONS'))

def hash_password(password):
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), PASSWORD_SALT, NUMBER_OF_ITERATIONS)
    return PASSWORD_SALT + hashed

def verify_password(stored_password, provided_password):
    salt = stored_password[:len(PASSWORD_SALT)]
    stored_hash = stored_password[len(PASSWORD_SALT):]
    provided_hash = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, NUMBER_OF_ITERATIONS)
    return stored_hash == provided_hash

# for testing purposes
@app.route("/api/users/all/", methods=["DELETE"])
def delete_all_users():
    users = DB.get_all_users()
    for user in users:
        DB.delete_user_by_id(user["id"])
    return success_response("All users deleted!")

@app.route("/api/extra/users/", methods=["POST"])
def create_user_with_password():
    body = json.loads(request.data)

    fields = ["name", "username", "password"]
    blank_fields = []
    for field in fields:
        if field not in body:
            blank_fields.append(field)

    if blank_fields:
        return failure_response(f"Fields {blank_fields} are required", 400)

    name = body["name"]
    username = body["username"]
    password = body["password"]
    balance = body.get("balance", 0)

    hashed_password = hash_password(password)
    user_id = DB.insert_user_extra(name, username, hashed_password, balance)
    user = DB.get_user_by_id_extra(user_id)

    user["password"] = password

    if user is None:
        return failure_response("Something went wrong while creating user!")
    return success_response(user, 201)


@app.route("/api/extra/user/<int:user_id>/", methods=["POST"])
def get_user_with_password(user_id):
    body = json.loads(request.data)

    if "password" not in body:
        return failure_response("Password is required!", 401)

    password = body["password"]
    user = DB.get_user_by_id_extra(user_id)

    if user is None:
        return failure_response("User not found")
    
    if not verify_password(user["password"], password):
        return failure_response("Incorrect password", 401)
    
    user["password"] = password

    return success_response(user)

@app.route("/api/extra/send/", methods=["POST"])
def send_money_with_password():
    body = json.loads(request.data)

    if "password" not in body:
        return failure_response("Password is required!", 401)

    fields = ["amount", "sender_id", "receiver_id"]
    blank_fields = []
    for field in fields:
        if field not in body:
            blank_fields.append(field)

    if blank_fields:
        return failure_response(f"Fields {blank_fields} are required", 400)

    amount = body["amount"]
    sender_id = body["sender_id"]
    receiver_id = body["receiver_id"]
    password = body["password"]

    sender = DB.get_user_by_id_extra(sender_id)
    receiver = DB.get_user_by_id_extra(receiver_id)

    if not verify_password(sender["password"], password):
        return failure_response("Incorrect password!", 401)
    if sender is None:
        return failure_response("Sender not found!", 404)
    if receiver is None:
        return failure_response("Receiver not found!", 404)

    sender_balance = sender["balance"] - amount
    receiver_balance = receiver["balance"] + amount

    if sender_balance >= 0:
        DB.update_user_by_id_extra(sender_id, sender["name"], 
                             sender["username"], sender["password"], sender_balance)
        DB.update_user_by_id_extra(receiver_id, receiver["name"], 
                             receiver["username"], receiver["password"], receiver_balance)
        return success_response(body, 200)
    else:
        return failure_response("Insufficient funds", 400)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
