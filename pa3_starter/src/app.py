import datetime
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
    return "Hello world!"


# your routes here


# route to return all users in the database
@app.route("/api/users/", methods=["GET"])
def get_users():
    users = DB.get_all_users()

    # hide the balance of the
    for user in users:
        del user["balance"]

    return success_response({"users": users})

# route to create a user
@app.route("/api/users/", methods=["POST"])
def create_user():
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
    
    transactions = DB.get_transactions_by_user_id(user_id)

    response = {
        "id": user["id"],
        "name": user["name"],
        "username": user["username"],
        "balance": user["balance"],
        "transactions": transactions
    }

    return success_response(response, 201)

# route to get a specific user by ID
@app.route("/api/users/<int:user_id>/", methods=["GET"]) 
def get_user(user_id):
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("User not found!")

    transactions = DB.get_transactions_by_user_id(user_id)

    response = {
        "id": user["id"],
        "name": user["name"],
        "username": user["username"],
        "balance": user["balance"],
        "transactions": transactions
    }

    return success_response(response)

# route to delete a specific user by ID
@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = DB.get_user_by_id(user_id)

    if user is None:
        return failure_response("User not found!")
    DB.delete_user_by_id(user_id)

    transactions = DB.get_transactions_by_user_id(user_id)

    response = {
        "id": user["id"],
        "name": user["name"],
        "username": user["username"],
        "balance": user["balance"],
        "transactions": transactions
    }

    return success_response(response)

# create transaction by sending or requesting money
@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    body = json.loads(request.data)

    fields = ["sender_id", "receiver_id", "amount", "message", "accepted"]
    blank_fields = []
    for field in fields:
        if field not in body:
            blank_fields.append(field)
   
    if blank_fields:
        return failure_response(f"Fields {blank_fields} are required", 400)

    sender_id = body["sender_id"]
    receiver_id = body["receiver_id"]
    amount = body["amount"]
    message = body["message"]
    accepted = body["accepted"]
    
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    if accepted:
        sender = DB.get_user_by_id(sender_id)
        receiver = DB.get_user_by_id(receiver_id)

        if sender is None:
            return failure_response("Sender not found!", 404)
        if receiver is None:
            return failure_response("Receiver not found!", 404)

        sender_balance = sender["balance"] - amount
        receiver_balance = receiver["balance"] + amount

        if sender_balance >= 0:
            DB.update_user_by_id(sender_id, sender["name"], sender["username"], sender_balance)
            DB.update_user_by_id(receiver_id, receiver["name"], receiver["username"], receiver_balance)

            DB.insert_transaction(timestamp, sender_id, receiver_id, amount, accepted, message)
        else:
            return failure_response(message, 403)
    else:
        receiver = DB.get_user_by_id(receiver_id)
        receiver_balance = receiver["balance"] - amount
        if receiver_balance >= 0:
            DB.insert_transaction(timestamp, sender_id, receiver_id, amount, None, message)
        else:
            return failure_response("Insufficient funds", 403)
    
    response = {
        "id": DB.get_last_transaction_id(),
        "timestamp": timestamp,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "amount": amount,
        "message": message,
        "accepted": accepted,
    }

    return success_response(response, 201)

# route to accept or deny a transaction
@app.route("/api/transactions/<int:transaction_id>/", methods=["POST"])
def accept_deny_transaction(transaction_id):
    body = json.loads(request.data)

    if "accepted" not in body:
        return failure_response("Accepted field is required!", 400)
    
    transaction = DB.get_transaction_by_id(transaction_id)
    
    current_accepted = transaction["accepted"]
    sender_id = transaction["sender_id"]
    receiver_id = transaction["receiver_id"]
    amount = transaction["amount"]
    message = transaction["message"]

    new_accepted = body["accepted"]

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    if current_accepted is None:
        if new_accepted:
            sender = DB.get_user_by_id(sender_id)
            if sender is None:
                return failure_response("Sender not found!", 404)

            sender_balance = sender["balance"]
            if sender_balance >= amount:
                new_sender_balance = sender_balance - amount
                receiver = DB.get_user_by_id(receiver_id)
                if receiver is None:
                    return failure_response("Receiver not found!", 404)
                new_receiver_balance = receiver["balance"] + amount

                DB.update_user_by_id(sender_id, sender["name"], sender["username"], new_sender_balance)
                DB.update_user_by_id(receiver_id, receiver["name"], receiver["username"], new_receiver_balance)

                DB.accept_transaction(transaction_id, timestamp)
            else:
                return failure_response("Insufficient funds", 403)
        else:
            DB.deny_transaction(transaction_id, timestamp)
    else:
        return failure_response("Cannot change transaction's accepted field if it has already been accepted or denied", 403)

    response = {
        "id": transaction_id,
        "timestamp": timestamp,
        "sender_id": sender_id,
        "receiver_id": receiver_id,
        "amount": amount,
        "message": message,
        "accepted": new_accepted
    }

    return success_response(response, 200)

# get all transactions for testing purposes
@app.route("/api/transactions/", methods=["GET"])
def get_transactions():
    transactions = DB.get_all_transactions()

    return success_response({"transactions": transactions})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
