from application_services.imdb_artists_resource import IMDBArtistResource
from application_services.UsersResource.user_service import UserResource, AddressResource
from application_services.imdb_users_resource import IMDBUserResource
from database_services.RDBService import RDBService as RDBService
from middleware import security

from sns import *

from flask import Flask, redirect, url_for, request, render_template, Response, make_response
from flask_dance.contrib.google import make_google_blueprint, google
from flask_cors import CORS, cross_origin
import json, os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

client_id = "40383817009-4mgv0ccp5j2a7agsol99qifvetbglaaf.apps.googleusercontent.com"
client_secret = "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"
app.secret_key = "supersekrit"
blueprint = make_google_blueprint(
    client_id=client_id,
    client_secret=client_secret,
    scope=["profile", "email"]
)
app.register_blueprint(blueprint, url_prefix="/login")
g_bp = app.blueprints.get("google")

# @app.before_request
# def before_request():
#     print("running before_request")
#     print(request)

#     result = security.security_check(request, google, g_bp)
    
#     if not result:
#         return redirect(url_for("google.login"))


@app.route("/", methods = ['GET'])
@cross_origin()
def hi():
    rsp = redirect("http://192.168.1.17:3000")
    rsp.headers.add('Access-Control-Allow-Origin', "*")
    return rsp

@app.route("/login", methods = ['GET'])
def idx():
    return redirect(url_for("google.login"))

@app.route("/index", methods = ['GET'])
@cross_origin()
def index():
    if not google.authorized:
        print("unauthorized")
        rsp = redirect(url_for("google.login"))
        # rsp.headers.add('Access-Control-Allow-Origin', "*")
        return rsp
        # return "hello"
    google_data = google.get('/oauth2/v2/userinfo')
    assert google_data.ok, google_data.text
    # print(json.dumps(google_data, indent=2))
    # return "You are {email} on Google".format(email=google_data.json()["email"])
    #res = UserResource.get_by_template({"email":google_data.json()["email"]}) # return list of dict
    res = UserResource.get_by_template({"email":google_data.json()["email"]}) # return list of dict
    
    if len(res) == 0:
        rsp = Response(json.dumps({
            "firstName": google_data.json()["given_name"],
            "lastName": google_data.json()["family_name"],
            "email": google_data.json()["email"],
            "status": "authorized",
            }, default=str), status=200, content_type="application/json")
    else:
        res["status"] = "authorized"
        rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp
    # return render_template("index.html", email=google_data.json()["email"])

@app.route('/account', methods = ['POST'])
def validateAccount():
    email = request.form.get('email')
    password = request.form.get('password')

    print(email)
    print(password)

    info = UserResource.get_by_template({"email": email})
    if len(info) > 0:
        pw = info[0]["password"]
        print(pw)
        if pw == password:
            rsp = Response(json.dumps({
                "firstName": info[0]["firstName"],
                "status": "valid",
                }, default=str), status=200, content_type="application/json")
            return rsp
        else:
            rsp = Response(json.dumps({
                "comment": "invalid password",
                "status": "invalid",
                }, default=str), status=200, content_type="application/json")
            return rsp
    
    rsp = Response(json.dumps({
        "comment": "invalid account",
        "status": "invalid",
        }, default=str), status=200, content_type="application/json")
    return rsp

@app.route('/api/users', methods = ['GET'])
def get_users():
    if request.args.get('limit'):
        limit = request.args.get('limit')
    else:
        limit = "10"
    if request.args.get('offset'):
        offset = request.args.get('offset')
    else:
        offset = "0"
    
    res = UserResource.get_by_template(None, limit, offset)
    for item in res:
        item["links"] = [
            {"rel": "self", "href": f"/api/users/{item['id']}"},
            {"rel": "address", "href":f"/api/address/{item['address_id']}"}
        ]
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp

@app.route('/api/users/<prefix>', methods = ['GET'])
def get_users_resource(prefix):
    res = UserResource.get_by_template({"id": prefix})
    res[0]["links"] = [
            {"rel": "self", "href": f"/api/users/{res[0]['id']}"},
            {"rel": "address", "href":f"/api/address/{res[0]['address_id']}"}
    ]
    rsp = Response(json.dumps(res[0], default=str), status=200, content_type="application/json")
    return rsp

@app.route('/api/address/<prefix>', methods = ['GET'])
def get_address_resource(prefix):
    res = AddressResource.get_by_template({"address_id": prefix})
    rsp = Response(json.dumps(res, default=str), status=200, content_type="application/json")
    return rsp

@app.route('/api/sns/<user_email>', methods=['GET'])
def sns_user_post(user_email):
    topic_arn = create_topic("oneTimeNotification")
    topic = sns.Topic(arn=topic_arn)
    subscribe(topic, 'email', user_email)
    publish_message(topic_arn, 'You have successfully registered to NBA service supported by DBUSERDBUSER!')
    delete_topic(topic_arn)

@app.route('/api/create', methods = ['POST'])
def create_user():
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    email = request.form.get('email')
    password = request.form.get('password')
    address = request.form.get('address')
    zip_code = request.form.get('zip')
    next_id = int(UserResource.get_next_id("id")[0]["max_id"]) + 1
    next_address_id = int(AddressResource.get_next_id("address_id")[0]["max_id"]) + 1

    AddressResource.create_data_resource({
        "address_id": next_address_id,
        "address": address,
        "zip": zip_code
        })
    
    UserResource.create_data_resource({
        "firstName": firstName,
        "lastName": lastName,
        "email": email,
        "password": password,
        "id": next_id,
        "address_id": next_address_id
        })
    
    return f"{firstName} are now a user! Checkout /api/users/{next_id}"

 
@app.after_request
def after(resp):
    resp = make_response(resp)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
    resp.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return resp

if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), host="0.0.0.0", port=5011)
