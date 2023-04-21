from datetime import datetime,timedelta
from io import BytesIO
import pymongo
from flask import Flask, render_template, request, url_for, redirect, session, views, abort, make_response, jsonify
from pymongo import MongoClient
# from flask_cors import CORS
from flask_wtf import CSRFProtect

import time
import auth, costants,data_storing,data_acquisition,data_delete,data_update
from threading import Thread
import os
from functools import wraps
import uuid
import secrets
import utility
from authlogin import login_required
# import bcrypt
# set app as a Flask instance
app = Flask(__name__)
import uuid
from core import md5utils
# encryption relies on secret keys so they could be run
CSRFProtect(app)
# cors = CORS(app, resources={r"/*": {"origins": "*"}})

import logging
from utility import ImageCode
logger = logging.getLogger('my_logger')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('log.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
# referer check
@app.route('/process', methods=['POST'])
def process():
    # Check if the Referer field is from this site
    if not request.referrer or request.referrer.startswith(request.host_url):
        # Processing Requests
        return "Success"
    else:
        # Reject requests
        abort(403)
@app.before_request
def log_request_info():
    logger.info('Request URL: %s', request.url)
    logger.info('Request method: %s', request.method)
    logger.info('Request headers: %s', request.headers)
    logger.info('Request data: %s', request.get_data())

@app.after_request
def log_response_info(response):
    try:
        logger.info('Response status code: %s', response.status_code)
        logger.info('Response headers: %s', response.headers)
        logger.info('Response data: %s', response.get_data())
    except:
        pass
    return response
# #connect to your Mongo DB database
def MongoDB():
    client = data_storing.connect_cluster_mongodb(
        costants.CLUSTER_NAME, auth.MONGODB_USERNAME, auth.MONGODB_PASSWORD
    )
    db = client.get_database('security')
    records = db.user
    return records

records = MongoDB()

def init_app():
    app.config['DEBUG'] = True
    app.config['SECRET_KEY'] = secrets.token_hex(16)

def adminMongoDB():

    client = data_storing.connect_cluster_mongodb(
        costants.CLUSTER_NAME, auth.MONGODB_USERNAME, auth.MONGODB_PASSWORD
    )
    db = client.get_database('security')
    records = db.admin
    return records


##Connect with Docker Image###
# def dockerMongoDB():
#     client = MongoClient(host='test_mongodb',
#                             port=27017,
#                             username='root',
#                             password='pass',
#                             authSource="admin")
#     db = client.users
#     pw = "test123"
#     hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
#     records = db.register
#     records.insert_one({
#         "name": "Test Test",
#         "email": "test@yahoo.com",
#         "password": hashed
#     })
#     return records

# records = dockerMongoDB()

# pw = "test123"
# hashed = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
# records.insert_one({
#         "name": "Test Test",
#         "email": "test@yahoo.com",
#         "password": hashed
#     })

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        cookie=request.cookies.get('cookie')

        if not cookie:
            return redirect(url_for('login', next=request.url))
        if cookie=="":
            return redirect(url_for('login', next=request.url))

        if session.get(cookie) is None:
            return redirect(url_for('login', next=request.url))
        # Detecting if a common user accessing admin page
        if session.get(cookie)["id"] !=-1 and request.path.startswith("/admin"):
            return '<script>alert("You are not admin and cannot access privileges");location.href="/"</script>'
        if session.get(cookie)["id"] ==-1 and not request.path.startswith("/admin"):
            return redirect(url_for('admin_user_list', next=request.url))

        session["email"] = session.get(cookie)["email"]
        session["name"] = session.get(cookie)["name"]
        session["id"] = session.get(cookie)["id"]
        return f(*args, **kwargs)
    return decorated_function
import random
@app.route("/sendemail")
def send_mail():
    email = request.args.get("email")

    code = str(uuid.uuid4()).replace("-", "")[:6]
    session["ecode"] = code
    print(session.get("ecode"))
    emailutil=utility.EmailCode()
    emailutil.send_email(email, code)
    session["ecode"] = code

    return jsonify({"code": 200, "msg": "Sent Successfully"})

# assign URLs to have a particular route
@app.route("/register", methods=['post', 'get'])
def register():
    message = ''
    # if method post in index
    if "email" in session:
        return redirect(url_for("logged_in2"))
    if request.method == "POST":
        user = request.form.get("fullname")
        email = request.form.get("email")
        Vcode = request.form.get("Vcode")
        email_code = request.form.get("email_code")
        print("Vcode")
        print(Vcode)
        icode = session.get('image')
        print("icode")
        print(icode)
        if icode != Vcode:
            message = "Validation code error"
            return render_template('register.html', message=message)
        print(email_code,session.get("ecode"))
        if email_code!=session.get("ecode"):
            message = "Validation email code error"
            return render_template('register.html', message=message)

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # if found in database showcase that it's found
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})


        if user_found:
            message = 'There already is a user by that name'
            return render_template('register.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('register.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('register.html', message=message)
        else:
            # hash the password and encode it
            # hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())

            # assing them in a dictionary in key value pairs
            # user_input = {'name': user, 'email': email, 'password': hashed}
            result = records.find_one(sort=[("id", pymongo.DESCENDING)])
            max_id = result["id"]

            user_input = {'name': user, 'email': email, 'password': md5utils.md5_encode(password2)}
            user_input['id']=int(max_id)+1
            records.insert_one(user_input)

            # find the new created account and its email
            user_data = records.find_one({"email": email})
            new_email = user_data['email']
            # if registered redirect to logged in as the registered user
            return redirect(url_for("index"))
    return render_template('register.html')
@app.route('/vcode')
def vcode():
    image, str = ImageCode().draw_verify_code()
    # print(code,bstring)
    buf = BytesIO()
    image.save(buf, 'jpeg')
    buf_str = buf.getvalue()
    # Return binary as a response to the front-end, and set header fields.
    response = make_response(buf_str)
    response.headers['Content-Type'] = 'image/gif'
    # Store the verification code string in the session
    session['image'] = str
    return response



@app.route("/login", methods=["POST", "GET"])
def login():
    message = 'Please login to your account'
    # if "email" in session:
    #     return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        Vcode = request.form.get("Vcode")
        print("Vcode")
        print(Vcode)
        icode = session.get('image')
        print("icode")
        print(icode)
        if icode != Vcode:
            message = "Validation code error"
            return render_template('login.html', message=message)

        # check if email exists in database
        email_found = records.find_one({"email": email})
        if email_found:
            email_val = email_found['email']
            passwordcheck = email_found['password']
            # encode the password and check if it matches
            # if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
            if md5utils.md5_encode(password) == passwordcheck:
                myuuid= str(uuid.uuid4())
                session[myuuid]={"email":email_val,"name":email_found['name'],"id":email_found['id'],"uuid":myuuid}

                resp=redirect(url_for('index'))
                expires = datetime.now() + timedelta(days=1)

                resp.set_cookie('cookie',myuuid,expires=expires)

                with open("cookies.txt", "a") as f:
                    f.write(myuuid+"\n")

                return resp
            else:

                message = 'Wrong password'
                return render_template('login.html', message=message)
        else:
            message = 'Email not found'
            return render_template('login.html', message=message)
    return render_template('login.html', message=message)

import re
@app.route("/admin/login", methods=["POST", "GET"])
def adminlogin():
    message = 'Please login to your admin account'
    # if "email" in session:
    #     return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        Vcode = request.form.get("Vcode")
        print("Vcode")
        print(Vcode)
        icode = session.get('image')
        print("icode")
        print(icode)
        if icode != Vcode:
            message = "Validation code error"
            return render_template('adminlogin.html', message=message)
        adminINfo=adminMongoDB()
        pattern = "^(?=.*[!@#$%^&*(),.?\":{}|<>])(?=.{8,})\S+$"

        if not re.match(pattern, password):
            message = 'The password must be greater than 8 digits and contain special characters'
            return render_template('adminlogin.html', message=message)

        # check if email exists in database
        username_found = adminINfo.find_one({"username": username})
        if username_found:
            username = username_found['username']
            passwordcheck = username_found['password']
            # encode the password and check if it matches
            # if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
            if md5utils.md5_encode(password) == passwordcheck:
                myuuid= str(uuid.uuid4())
                session[myuuid]={"email":username_found['email'],"name":username,"id":-1,"uuid":myuuid}

                resp=redirect(url_for('admin_user_list'))
                expires = datetime.now() + timedelta(days=1)

                resp.set_cookie('cookie',myuuid,expires=expires)

                # with open("cookies.txt", "a") as f:
                #     f.write(myuuid+"\n")

                return resp
            else:
                message = 'Wrong password'
                return render_template('adminlogin.html', message=message)
        else:
            message = 'username not found'
            return render_template('adminlogin.html', message=message)
    return render_template('adminlogin.html', message=message)

@app.route('/')
@login_required
def index():

    # update the data in the table
    row = data_acquisition.acquire_data_from_message()
    # data = data_acquisition.acquire_data_from_message(conditionproduct={"nikename":"mike"})
    # return render_template('index.html', data=row)
    return render_template('index.html',data=row)



@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("email", None)
    session.pop("name", None)
    session.pop("id", None)

    resp = redirect(url_for('signout'))

    resp.set_cookie('cookie', '', expires=0)

    return resp
@app.route("/signout", methods=["POST", "GET"])
def signout():
    return render_template("signout.html")

#show the page of adding the message
@app.route('/add2')
@login_required

def add2():
    #
    # if session.get("email"):
    #     #  already logged in
    #     print(session.get('email'))
    return render_template('add2.html')
    # else:

    # return redirect(url_for("login"))
from core import checkutils

@app.route('/insert2', methods=['POST'])
@login_required
def insert2():
    # 1.get the data from form
    data_dict = request.form.to_dict()
    data_info=data_dict['info'].replace('\n', '')
    data_info=data_info.replace(' ','')
    data_info = data_info.replace('\r', '')
    data_info = data_info.replace('\t', '')
    if not checkutils.checkString(data_info):

        return '<script>alert("Contains sensitive information. Publishing failed!");location.href="/add2"</script>'
    if data_info:
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        data_dict['date'] = str(date)
        # get_max_id
        num = data_acquisition.get_max_id(costants.CLUSTER_NAME, costants.DATABASE_NAME, costants.COLLECTION_MESSAGE)
        data_dict['id'] = num + 1
        email = session.get("email")
        # print(email)
        # print(data_dict)
        data_dict['nikename'] = email
        # 2.把数据添加到数据库
        data_storing.store_dict_into_mongodb(costants.CLUSTER_NAME, costants.DATABASE_NAME, costants.COLLECTION_MESSAGE,
                                             data_dict)
        return '<script>alert("Message sent successfully!");location.href="/"</script>'

    else:
        return '<script>alert("The message is empty. Publishing failed!");location.href="/add2"</script>'




@app.route('/add1')
@login_required

def add():
    #
    # if session.get("email"):
    #
    #     print(session.get('email'))
    return render_template('add.html')
    # else:
    # return redirect(url_for("login"))
from core import checkutils


@app.route('/insert', methods=['POST'])
@login_required
def insert():
    # 1.get the data from form
    data_dict = request.form.to_dict()
    data_info=data_dict['info'].replace('\n', '')
    data_info=data_info.replace(' ','')
    data_info = data_info.replace('\r', '')
    data_info = data_info.replace('\t', '')
    if not checkutils.checkString(data_info):

        return '<script>alert("Contains sensitive information. Publishing failed!");location.href="/add1"</script>'
    if data_info:
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        data_dict['date'] = str(date)
        # get_max_id
        num = data_acquisition.get_max_id(costants.CLUSTER_NAME, costants.DATABASE_NAME, costants.COLLECTION_MESSAGE)
        data_dict['id'] = num + 1
        email = session.get("email")
        # print(email)
        # print(data_dict)
        data_dict['nikename'] = email
        # 2.insert the data from the database
        data_storing.store_dict_into_mongodb(costants.CLUSTER_NAME, costants.DATABASE_NAME, costants.COLLECTION_MESSAGE,
                                             data_dict)
        return '<script>alert("Message sent successfully!");location.href="/"</script>'

    else:
        return '<script>alert("The message is empty. Publishing failed!");location.href="/add1"</script>'


#  user can only delete their own message so we need to check the login status

#delete one row
@app.route("/delete")
@login_required
def delete():
    id = request.args.get('id')
    # according to the id get the nikename from database
    res = data_acquisition.acquire_data_from_message({'id': int(id)})
    res=res[0]
    nikename=res['nikename']
    # nikename=request.args.get('nikename')
    email = session.get("email")

    if email==nikename:
        data_delete.delete_one_record({'id': int(id)})
        return '<script>alert("Delete successfully！");location.href="/"</script>'
    else:
        return '<script>alert("Deletion failed! Unable to delete others message ");location.href="/"</script>'



@app.route("/update")
@login_required
def update():
    print("Waiting for updating")

    id = request.args.get('id')
    data = data_acquisition.get_data_one(costants.CLUSTER_NAME, costants.DATABASE_NAME, costants.COLLECTION_MESSAGE,id)

    # res=data_acquisition.acquire_data_from_message({'id':id})
    return render_template('update.html', data=data)




@app.route('/modify', methods=['POST'])
def modify():

    data_dict = request.form.to_dict()
    data_info = data_dict['info'].replace('\n', '')
    print(data_info)
    id = data_dict['id']

    data_info = data_info.replace(' ', '')
    data_info = data_info.replace('\r', '')
    data_info = data_info.replace('\t', '')
    if not checkutils.checkString(data_info):

        return '<script>alert("Contains sensitive information. Publishing failed!");location.href="/update?id={}"</script>'.format(id)
    if data_info:
        data = request.form.to_dict()
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        data['date'] = str(date)
        email = session.get("email")
        id=data['id']
        # print(email)
        # print(data_dict)
        data['nikename'] = email
        data_update.update_one_record(info=data['info'],date=data['date'],nikename=data['nikename'],condition={'id':int(data['id'])})
        return '<script>alert("Modification successful!");location.href="/"</script>'
    else:
        data = request.form.to_dict()
        id = data['id']
        return f'<script>alert("Message modification failed!");location.href="update?id={id}"</script>'

# Thread(target=lambda: app.run(port=5001)).start()
#
#  # ----------server 2-----------------
# app2 = Flask('app2')

@app.route('/hacker')
def hacker():
    return render_template('hackerB.html')
#admin function
@app.route('/admin/user/list')
@login_required
def admin_user_list():
    #get the data from db
    row = records.find({})

    return render_template('admin_user_list.html',data=row)

@app.route('/admin/user/delete')
@login_required
def admin_user_delete():
    id=request.args.get("id")

    records.delete_one({"id":int(id)})
    return f'<script>alert("User Deletion successful!");location.href="/admin/user/list"</script>'

@app.route('/admin/message/list')
@login_required
def admin_message_list():

    row = data_acquisition.acquire_data_from_message()

    return render_template('admin_message_list.html',data=row)

@app.route('/admin/message/delete')
@login_required
def admin_message_delete():
    id=request.args.get("id")
    data_delete.delete_one_record({'id': int(id)})
    return f'<script>alert("Message Deletion successful!");location.href="/admin/message/list"</script>'
@app.route("/admin/user/add", methods=['post', 'get'])
@login_required
def admin_user_add():
    message = ''
    # if method post in index
    if request.method == "GET":
        return render_template('admin_user_add.html')

    else:
        user = request.form.get("fullname")
        email = request.form.get("email")

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        # if found in database showcase that it's found
        user_found = records.find_one({"name": user})
        email_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user by that name'
            return render_template('admin_user_add.html', message=message)
        if email_found:
            message = 'This email already exists in database'
            return render_template('admin_user_add.html', message=message)
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('admin_user_add.html', message=message)
        else:
            result = records.find_one(sort=[("id", pymongo.DESCENDING)])
            max_id = result["id"]

            user_input = {'name': user, 'email': email, 'password': md5utils.md5_encode(password2)}
            user_input['id']=int(max_id)+1
            records.insert_one(user_input)

            # if registered redirect to logged in as the registered user
            return f'<script>alert("New user added successfully!");location.href="/admin/user/list"</script>'

@app.route("/admin/user/changpassword", methods=['post', 'get'])
@login_required
def admin_user_changeword():
    id = request.args.get("id")
    # if method post in index
    if request.method == "GET":
        data=records.find_one({"id":int(id)})

        return render_template('admin_user_change_password.html',data=data)

    else:

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('admin_user_change_password.html', message=message)
        else:
            records.update_one({"id":int(id)}, {"$set": {"password": md5utils.md5_encode(password2)}})
            return f'<script>alert("Password Changed Successfully!");location.href="/admin/user/list"</script>'

@app.route("/user/changpassword", methods=['post', 'get'])
@login_required
def user_changeword():
    id = request.args.get("id")
    # if method post in index
    if request.method == "GET":
        return render_template('user_change_password.html')


    else:

        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        if password1 != password2:
            message = 'Passwords should match!'
            return render_template('user_change_password.html', message=message)
        else:
            record=records.update_one({"id":session["id"]}, {"$set": {"password": md5utils.md5_encode(password2)}})
            return f'<script>alert("Password Changed Successfully!");location.href=""</script>'
if __name__ == "__main__":
    init_app()
    app.run(port=5003)
