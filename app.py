from flask import Flask, render_template, request, redirect, jsonify, make_response, flash, session
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
import jwt
import yaml
import os
from yaml.loader import SafeLoader
from werkzeug.security import generate_password_hash, check_password_hash
from flask_ckeditor import CKEditor
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin


app = Flask(__name__)
db = yaml.load(open('db.yaml'), Loader=SafeLoader)
# app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = 300
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = os.urandom(24)
# app.config.update(SECRET_KEY=os.urandom(24))
# app.secret_key = os.urandom(24)
app.config['CORS_HEADERS'] = 'Content-Type'
mysql = MySQL(app)

CKEditor(app)
# cors = CORS(app)
# server_session = Session(app)
# CORS(app)
# cors = CORS(app, resource={
#     r"/*": {
#         "origins": "*"
#     }
# })
# cors = CORS(app, resources={r'*': {'origins': 'http://localhost:3000'}})
CORS(app, supports_credentials=True)
# server_session = Session(app)


@app.route('/')
def index():
    if not session.get('login'):
        return redirect('/login')
    else:
        cursor = mysql.connection.cursor()
        result_value = cursor.execute("SELECT * FROM blog")
        if result_value > 0:
            blogs = cursor.fetchall()
            cursor.close()
            return render_template('index.html', blogs=blogs)
        return render_template('index.html', blogs=None)


@app.route('/about/')
def about():
    return render_template('about.html')


@app.route('/blogs/<int:id>')
def blogs(id):
    cursor = mysql.connection.cursor()
    result_value = cursor.execute(
        "SELECT * FROM blog WHERE blog_id = {}".format(id))
    if result_value > 0:
        blog = cursor.fetchone()
        return render_template('blogs.html', blog=blog)
    return 'Blog is not found'


@app.route('/register/', methods=["GET", "POST"])
def registr():
    if request.method == 'POST':
        req = request.get_json()
        # user_details = request.form
        user_details = req
        print(user_details)
        if user_details['password'] != user_details['confirmPassword']:
            return jsonify({"error": "Unauthorized"}), 401
            # flash('Passwords do not match! Try again!', 'danger')
            # return render_template('registr.html')
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO user(first_name, last_name, username, email, password) VALUES (%s, %s, %s, %s, %s)", (user_details['firstname'], user_details['lastname'], user_details['username'], user_details['email'], generate_password_hash(user_details['password'])))
        mysql.connection.commit()
        cursor.close()
        return jsonify({
            'message': 'test'
        }, 200)
        # flash('Registration successful! Please login', 'success')
        # return redirect('/login')
    return jsonify({"error": "Unauthorized"}), 401


@app.route('/login/', methods=["GET", "POST"])
def login():
    req = request.get_json()
    email = req.get('email')
    password = req.get('password')
    token = jwt.encode({
        'user': email,
        'expiration': str(datetime.utcnow() + timedelta(seconds=120))
    },
        app.config['SECRET_KEY'],
        algorithm="HS256"
    )
    cursor = mysql.connection.cursor()
    result_value = cursor.execute(
        "SELECT * FROM user WHERE email = %s", ([req.get('email')]))
    user = cursor.fetchone()

    if user is None:
        return jsonify({"error": "Unauthorized"}), 401

    if not check_password_hash(user['password'], password):
        return jsonify({"error": "Password not correct"}), 401

    session['first_name'] = user['first_name']
    session['last_name'] = user['last_name']
    session['email'] = user['email']
    session.modified = True
    return jsonify({
        "token": token,
        "user": user['email']
    })

    # if request.method == 'POST':
    #     req = request.get_json()
    #     session['email'] = req.get('email')
    #     token = jwt.encode({
    #         'user': req.get('email'),
    #         'expiration': str(datetime.utcnow() + timedelta(seconds=120))
    #     },
    #         app.config['SECRET_KEY'],
    #         algorithm="HS256"
    #     )
    #     cursor = mysql.connection.cursor()
    #     result_value = cursor.execute(
    #         "SELECT * FROM user WHERE email = %s", ([req.get('email')]))
    #     if result_value > 0:
    #         user = cursor.fetchone()
    #         session['first_name'] = user['first_name']
    #         session['last_name'] = user['last_name']
    #         session.modified = True
    #         print('login', session)
    #         if check_password_hash(user['password'], req.get('password')):
    #             responce = {
    #                 "message": "Login Succsess",
    #                 "token": token,
    #                 "user": user['email']
    #             }
    #             res = make_response(jsonify(responce), 200)
    #             return res
    #         else:
    #             cursor.close()
    #             responce = {
    #                 'message': 'Error password!'
    #             }
    #             res = make_response(jsonify(responce), 401)
    #             return res
    #     else:
    #         cursor.close()
    #         responce = {
    #             'message': 'Error email!'
    #         }
    #         res = make_response(jsonify(responce), 401)
    #         return res

    # if request.method == 'POST':
    #     user_details = request.form
    #     username = user_details['username']
    #     cursor = mysql.connection.cursor()
    #     result_value = cursor.execute(
    #         "SELECT * FROM user WHERE username = %s", ([username]))
    #     if result_value > 0:
    #         user = cursor.fetchone()
    #         if check_password_hash(user['password'], user_details['password']):
    #             session['login'] = True
    #             session['first_name'] = user['first_name']
    #             session['last_name'] = user['last_name']
    #             flash('Welcome ' + session['first_name'] +
    #                   '! You have been successfully logged in!', 'success')
    #         else:
    #             cursor.close()
    #             flash('Password is incorrect!', 'danger')
    #             return render_template('login.html')
    #     else:
    #         cursor.close()
    #         flash('User does not exist!', 'danger')
    #         return render_template('login.html')
    #     cursor.close()
    #     return redirect('/')
    # return render_template('login.html')


@app.route('/logout/')
def logout():
    session.pop("email")
    return "200"
    # responce = {
    #     "message": "Logout Succsess"
    # }
    # res = make_response(jsonify(responce), 200)
    # return res
    # session.clear()
    # flash('You have been logged out', 'info')
    # return redirect('/')


@app.route('/write-blog/', methods=["GET", "POST"])
def write_blog():
    if request.method == 'POST':
        blogpost = request.form
        title = blogpost['title']
        body = blogpost['body']
        author = session['first_name'] + ' ' + session['last_name']
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO blog (title, body, author) VALUES (%s, %s, %s)", (title, body, author))
        mysql.connection.commit()
        cursor.close()
        flash('Your blogpost is successfully posted!', 'success')
        return redirect('/')
    return render_template('write-blog.html')


@app.route('/@me', methods=['GET'])
def get_current_user():
    email = session.get('email')
    if not email:
        return jsonify({"error": "Unauthorized"}), 401
    cursor = mysql.connection.cursor()
    result_value = cursor.execute(
        "SELECT * FROM user WHERE email = %s", ([email]))
    user = cursor.fetchone()
    return jsonify({
        "email": user['email']
    })
    # token = request.headers.Authorization
    # if token:
    #     decoded = jwt.decode(token, app.config['SECRET_KEY'])
    #     print(decoded)
    #     return 'hello'
    # responce = {
    #     'message': 'test!'
    # }
    # res = make_response(jsonify(responce), 200)
    # return res


@app.route('/contacts/')
def contacts():
    cursor = mysql.connection.cursor()
    result_value = cursor.execute(
        "SELECT * FROM contacts WHERE author = %s", [session['email']])
    contacts = cursor.fetchall()
    responce = {
        'message': 'Fetch success!',
        'contacts': contacts
    }
    res = make_response(jsonify(responce), 200)
    return res


@app.route('/contacts/<int:id>')
def contact_id(id):
    cursor = mysql.connection.cursor()
    result_value = cursor.execute(
        "SELECT * FROM contacts WHERE contact_id = {}".format(id))
    print(result_value)
    if result_value > 0:
        contact = cursor.fetchone()
        responce = {
            'message': 'Fetch success!',
            'contact': contact
        }
        res = make_response(jsonify(responce), 200)
        return res
    responce = {
        'message': 'Error!',
    }
    res = make_response(jsonify(responce), 401)
    return res


@app.route('/edit-contact/<int:id>', methods=["GET", "POST"])
def edit_contact(id):
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        req = request.get_json()
        cursor.execute(
            "UPDATE contacts SET first_name = %s, last_name = %s, tel = %s, email = %s, company = %s, info = %s WHERE contact_id = %s", (req.get('first_name'), req.get('last_name'), req.get('tel'), req.get('email'), req.get('company'), req.get('info'), id))
        mysql.connection.commit()
        cursor.close()
        responce = {
            'message': 'Contact change completed!'
        }
        res = make_response(jsonify(responce), 200)
        return res
    # cursor = mysql.connection.cursor()
    # result_value = cursor.execute(
    #     "SELECT * FROM blog WHERE blog_id = {}".format(id))
    # if result_value > 0:
    #     blog = cursor.fetchone()
    #     blog_form = {}
    #     blog_form['title'] = blog['title']
    #     blog_form['body'] = blog['body']
    #     return render_template('edit-blog.html', blog_form=blog_form)


@app.route('/write-contact/', methods=["GET", "POST"])
def write_contact():
    if request.method == 'POST':
        req = request.get_json()
        author = session['email']
        cursor = mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO contacts (first_name, last_name, tel, email, company, info, author) VALUES (%s, %s, %s, %s, %s, %s, %s)", (req.get('first_name'), req.get('last_name'), req.get('tel'), req.get('email'), req.get('company'), req.get('info'), author))
        mysql.connection.commit()
        cursor.close()
        responce = {
            'message': 'Contact create completed!'
        }
        res = make_response(jsonify(responce), 200)
        return res


@app.route('/delete-contact/<int:id>', methods=["DELETE"])
def delete_contact(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM contacts WHERE contact_id = {}".format(id))
    mysql.connection.commit()
    responce = {
        'message': 'Contact delete completed!'
    }
    res = make_response(jsonify(responce), 200)
    return res


@app.route('/profile', methods=['GET'])
def profile():
    email = session['email']
    cursor = mysql.connection.cursor()
    result_value = cursor.execute(
        "SELECT * FROM user WHERE email = %s", ([email]))
    user = cursor.fetchone()

    responce = {
        'message': 'Get profile completed!',
        'data': user
    }
    res = make_response(jsonify(responce), 200)
    return res


@app.route('/my-blogs/')
def my_blogs():
    cursor = mysql.connection.cursor()
    result_value = cursor.execute(
        "SELECT * FROM contacts WHERE author = %s", [session['email']])
    contacts = cursor.fetchall()
    responce = {
        'message': 'Fetch success!',
        'contacts': contacts
    }
    res = make_response(jsonify(responce), 200)
    return res
    # author = session['first_name'] + ' ' + session['last_name']
    # result_value = cursor.execute(
    #     "SELECT * FROM blog WHERE author = %s", [author])
    # if result_value > 0:
    #     my_blogs = cursor.fetchall()
    #     responce = {
    #         "message": "Succsess fetch posts",
    #         "blogs": my_blogs
    #     }
    #     res = make_response(jsonify(responce), 200)
    #     return res
    # else:
    #     responce = {
    #         "message": "Post not found",
    #     }
    #     res = make_response(jsonify(responce), 200)
    #     return res
    # author = session['first_name'] + ' ' + session['last_name']
    # cursor = mysql.connection.cursor()
    # result_value = cursor.execute(
    #     "SELECT * FROM blog WHERE author = %s", [author])
    # if result_value > 0:
    #     my_blogs = cursor.fetchall()
    #     return render_template('my-blogs.html', blogs=my_blogs)
    # else:
    #     return render_template('my-blogs.html', blogs=None)


@app.route('/edit-blog/<int:id>', methods=["GET", "POST"])
def edit_blog(id):
    if request.method == "POST":
        cursor = mysql.connection.cursor()
        title = request.form['title']
        body = request.form['body']
        cursor.execute(
            "UPDATE blog SET title = %s, body = %s WHERE blog_id = %s", (title, body, id))
        mysql.connection.commit()
        cursor.close()
        flash('Post is updated successfully!', 'success')
        return redirect('/blogs/{}'.format(id))
    cursor = mysql.connection.cursor()
    result_value = cursor.execute(
        "SELECT * FROM blog WHERE blog_id = {}".format(id))
    if result_value > 0:
        blog = cursor.fetchone()
        blog_form = {}
        blog_form['title'] = blog['title']
        blog_form['body'] = blog['body']
        return render_template('edit-blog.html', blog_form=blog_form)


@app.route('/delete-blog/<int:id>')
def delete_blog(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM blog WHERE blog_id = {}".format(id))
    mysql.connection.commit()
    flash('Your blog has been deleted!', 'success')
    return redirect('/my-blogs')


if __name__ == '__main__':
    app.run(debug=True)
