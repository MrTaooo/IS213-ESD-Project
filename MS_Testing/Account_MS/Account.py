import firebase_admin
from firebase_admin import auth
from firebase_admin import db, credentials
from flask import Flask, request, jsonify, session, redirect
from flask_cors import CORS
from os import environ 

app = Flask(__name__)

CORS(app)

cred = credentials.Certificate({
  "type": "service_account",
  "project_id": "accounts-c05d0",
  "private_key_id": "fc5a25afeaf48412f91ba69c796a34ef6be6afaf",
  "private_key": ".....EnterYourAPIPrivateKeyHere.....",
  "client_email": "firebase-adminsdk-3tyit@accounts-c05d0.iam.gserviceaccount.com",
  "client_id": "100368083984929806068",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-3tyit%40accounts-c05d0.iam.gserviceaccount.com"
})

# cred = credentials.Certificate('/path/to/firebase-adminsdk.json') # replace with the path to your Firebase Admin SDK JSON file
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://accounts-c05d0-default-rtdb.asia-southeast1.firebasedatabase.app/",
})



app.secret_key = "ESDProject"

db = db.reference()

# # Now you can use auth and db to interact with Firebase services
@app.route("/verify_login", methods=['POST'])
def login_user():
    data = request.get_json()
    email = data["email"]
    input_password = data["password"]

    print(email)

    user = auth.get_user_by_email(email)
    print(user.uid)

    if user:
        print("user exists")
        user_password = db.child("users").child(user.uid).child("password").get()
        
        if input_password == user_password:
            return jsonify(
                {
                    "code": 200,
                    "message": "Login successful",
                    "data" : {
                        "userId": user.uid
                    }
                }
            ), 200
        else:
            return jsonify(
                {
                    "code": 400,
                    "message": "Incorrect login details"
                }
            ), 400


@app.route("/create_acct", methods=["POST"])
def create_user():

    data = request.get_json()
    email = data["newEmail"]
    password = data["newPassword"]
    name = data["newName"]

    try:
        user = auth.create_user(
            email = email,
            # email_verified=False,
            password = password,
            # display_name = name,
            # photo_url='http://www.example.com/12345678/photo.png',
            disabled=False)
        print('Sucessfully created new user: {0}'.format(user.uid))

        firebase_admin.db.reference('users').child(user.uid).set({
            'name': name,
            'email': email,
            'password': password
        })  

        return jsonify(
            {
                "code": 201, 
                "message": "Account created successfully"
            }
        ), 201

    except:
        return jsonify(
            {
                "code": 400,
                "message": "Error occurred when trying to create user"
            }
        ), 400
    

# retrieve user email
@app.route("/retrieve_email/<userId>", methods=['GET'])
def retrieve_email(userId):

    email = db.child("users").child(userId).child("email").get()
    print (email)
    if email:
        return jsonify(
            {
                "code": 200,
                "message": "Email retrieved successfully",
                "data": {
                    "email": email
                }
            }), 200
    
    else:
        return jsonify(
            {
                "code": 400,
                "message": "Error occurred when trying to retrieve email"
            }
        ), 400

# retrieve user name
@app.route("/retrieve_name/<userId>", methods=['GET'])
def retrieve_name(userId):

    name = db.child("users").child(userId).child("name").get()
    print (name)
    if name:
        return jsonify(
            {
                "code": 200,
                "message": "Name retrieved successfully",
                "data": {
                    "name": name
                }
            }), 200
    
    else:
        return jsonify(
            {
                "code": 400,
                "message": "Error occurred when trying to retrieve name"
            }
        ), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)