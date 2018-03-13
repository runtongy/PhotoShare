######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
# Fulfilled by:Runtong Yan (runtongy@bu.edu) and Wenyu Wang (zickw@bu.edu)
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for, session
from flaskext.mysql import MySQL
import flask.ext.login as flask_login

# for image uploading
# from werkzeug import secure_filename
import os, base64
import operator

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '970606'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            session['logged_in'] = True
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    session['logged_in'] = False
    flask_login.logout_user()
    return render_template('hello.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    supress='True'
    return render_template('register.html', supress=supress)
#    return render_template('register.html')

@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        hometown = request.form.get('hometown')
    except:
        print(
            "couldn't find all tokens")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown)"
                            "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".
                             format(email, password, first_name, last_name, gender, dob, hometown)))
#        cursor.execute("INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown)"
#                       "VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}')".
#                       format(email, password, first_name, last_name, gender, dob, hometown))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('hello.html', name=email, message='Account Created!')
    else:
        print("couldn't find all tokens")
#        supress=''
#        return flask.redirect(flask.url_for('register'))
        return render_template('register.html', name=email, message='Already Exist!')

@app.route("/friends", methods=['GET', 'POST'])
@flask_login.login_required
def add_friends():
    if request.method == 'POST':
        try:
            email = request.form.get('email')
            uid1 = getUserIdFromEmail(flask_login.current_user.id)
            uid2 = getUserIdFromEmail(email)
        except:
            return render_template('hello.html', name=flask_login.current_user.id, message='Not a user')
        test = isEmailUnique(email)
        if test:
            return render_template('hello.html', name=flask_login.current_user.id, message='Friend is not a user')
        else:
            test1 = isFriendUnique(uid1, uid2)
            if test1:
                if uid1 != uid2:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO FRIENDSHIP (UID1, UID2) VALUES ('{0}', '{1}')".format(uid1, uid2))
                    conn.commit()
                    return render_template('hello.html', name=flask_login.current_user.id, message='Friend added!')
                else:
                    return render_template('hello.html', name=flask_login.current_user.id, message='YoU canT add yourself!')
            else:
                return render_template('hello.html', name=flask_login.current_user.id, message='Friend Already Exist!')
    else:
        return render_template('friends.html')

@app.route("/friendslist", methods=['GET'])
@flask_login.login_required
def friends_list():
    return render_template('friendslist.html', name=flask_login.current_user.id, message='Here are your friends!',
                            friends=getFriendID(getUserIdFromEmail(flask_login.current_user.id)))

@app.route("/create", methods=['GET', 'POST'])
@flask_login.login_required
def create_album():
    if request.method == 'POST':
        try:
            aname = request.form.get('name')
            uid = getUserIdFromEmail(flask_login.current_user.id)
            doc = request.form.get('doc')
        except:
            flask.redirect(flask.url_for('create'))
        cursor = conn.cursor()
        test = isAlbumUnique(uid, aname)
        if test:
            cursor.execute("INSERT INTO ALBUM (NAME, DOC, UID) VALUES ('{0}', now(), '{2}')".format(aname, doc, uid))
            conn.commit()
            return render_template('hello.html', name=flask_login.current_user.id, message='Album Created')
        else:
            return render_template('create.html', name=flask_login.current_user.id, message='Album Already Exist!')
    else:
        return render_template('create.html')

@app.route("/deletealbum", methods=['GET', 'POST'])
@flask_login.login_required
def delete_album():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        aid = request.form.get('aid')
        test = isYourAlbum(uid, aid)
        if test:
            cursor = conn.cursor()
            print(cursor.execute("DELETE FROM ALBUM WHERE AID = {0}".format(aid)))
            cursor.execute("DELETE FROM ALBUM WHERE AID = {0}".format(aid))
            conn.commit()
            return render_template('hello.html', message='Album deleted')
        else:
            return render_template('deletealbum.html', message='You Cannot Delete Albums Belong to Other Users')
    else:
        return render_template('deletealbum.html')

@app.route("/Albums", methods=['GET'])
@flask_login.login_required
def show_album():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    albums = getUsersAlbums(uid)
    return render_template('Albums.html', message='Here are your albums', albums=albums)

@app.route("/Photos", methods=['GET','POST'])
@flask_login.login_required
def show_photo():
    if request.method == 'POST':
        aid = request.form.get('aid')
        photos = getUsersPhotosFromAb(aid)
        return render_template('Photos.html', message='Here are your photos', photos=photos)
    else:
        return render_template('Photos.html')

@app.route("/deletephoto", methods=['GET', 'POST'])
@flask_login.login_required
def delete_photo():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        pid = request.form.get('pid')
        aid = getAIDfromPID(pid)
        print(aid)
        test = isYourAlbum(uid, aid)
        if test:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM PHOTO WHERE PID = {0}".format(pid))
            conn.commit()
            return render_template('hello.html', message='Photo Deleted')
        else:
            return render_template('deletephoto.html', message='You Cannot Delete Photos Belong to Other Users')
    else:
        return render_template('deletephoto.html')

@app.route("/tag", methods=['GET','POST'])
@flask_login.login_required
def tag():
    if request.method == 'POST':
        pid = request.form.get('pid')
        print(pid)
        hashtag = request.form.get('hashtag')
        print(hashtag)
        test = isPhotoExist(pid)
        test1 = isTagExist(hashtag)
        if test1:
            cursor = conn.cursor()
#            cursor.execute("INSERT INTO TAG (HASHTAG) VALUES ('{0}')".format(hashtag))
            cursor.execute("INSERT INTO ASSOCIATE (PID, HASHTAG) VALUES ('{0}','{1}')".format(pid, hashtag))
            conn.commit()
            return render_template('tag.html', message='Tag stored')
        elif test:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO TAG (HASHTAG) VALUES ('{0}')".format(hashtag))
            cursor.execute("INSERT INTO ASSOCIATE (PID, HASHTAG) VALUES ('{0}','{1}')".format(pid, hashtag))
            conn.commit()
            return render_template('tag.html', message='Tag stored')
        else:
            return render_template('tag.html', message='Photo does not exist')
    else:
        return render_template('tag.html')

@app.route("/ViewPhoto", methods=['GET', 'POST'])
def view_photo():
    if request.method == 'POST':
        hashtag = request.form.get('hashtag')
        hashtag = hashtag.split(" ")
#        print(hashtag)
#        photo = getPhotoWithTag(hashtag)
        photo = []
        for i in range(len(hashtag)):
            test = isTagExist(hashtag[i])
            list = getPhotoWithTag(hashtag[i])
            if test:
                for j in range(len(list)):
                    photo.append(list[j])
        if photo != []:
            return render_template('ViewPhoto.html', message='Here are the related Photos', photos=photo)
        else:
            return render_template('ViewPhoto.html', message='Tag Does not Exist')
    else:
        return render_template('ViewPhoto.html')

@app.route("/ViewYourPhoto", methods=['GET', 'POST'])
@flask_login.login_required
def view_yourphoto():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        hashtag = request.form.get('hashtag')
        hashtag = hashtag.split(" ")
        photo = []
        for i in range(len(hashtag)):
            test = isTagExist(hashtag[i])
            list = getPhotoByUserWsTg(hashtag[i], uid)
            if test:
                for j in range(len(list)):
                    photo.append(list[j])
        if photo != []:
            return render_template('ViewYourPhoto.html', message='Here are your related Photos', photos=photo)
        else:
            return render_template('ViewYourPhoto.html', message='Tag Does not Exist')
    else:
        return render_template('ViewYourPhoto.html')


@app.route('/clickable', methods = ['GET'])
def photofromtags():
    hashtag = request.args['hashtag']
    photos=[]
    photos += getPhotoWithTag(hashtag)
    return render_template('clickable.html', photos = photos)


@app.route("/MostPopularTag", methods=['GET'])
@flask_login.login_required
def popular_tag():
    taglist = []
    tag1 = getPopularTag()
    print(tag1)
    for i in range(len(tag1)):
        taglist.append(tag1[i])
    return render_template('MostPopularTag.html', tags=taglist, message='Here are the most popular tags right now')


@app.route("/comment", methods=['GET', 'POST'])
def comment():
    if request.method == 'POST':
        content = request.form.get('content')
        pid = request.form.get('pid')
        doc = request.form.get('doc')
        if not session.get('logged_in'):
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO COMMENT (CONTENT, DOC, UID, PID) VALUES ('{0}', NOW(), '{2}', '{3}')".format(content, doc,
                                                                                                          0, pid))
            conn.commit()
            return render_template('comment.html', message='Successfully commented, Anonymous!')
        else:
            uid = getUserIdFromEmail(flask_login.current_user.id)
            aid = getAIDfromPID(pid)
            test = isYourAlbum(uid, aid)
            if test:
                return render_template('comment.html', name=flask_login.current_user.id, message='You cannot comment your own Photo!')
            else:
                cursor = conn.cursor()
                cursor.execute(
                "INSERT INTO COMMENT (CONTENT, DOC, UID, PID) VALUES ('{0}', NOW(), '{2}', '{3}')".format(content, doc, uid, pid))
                cursor.execute("UPDATE Users SET contribution = contribution+1 WHERE UID = {0}".format(uid))
                conn.commit()
                conn.commit()
                return render_template('comment.html', message='Successfully commented')
    else:
        return render_template('comment.html')

@app.route("/show_comments", methods=['GET', 'POST'])
def show_comments():
    if request.method == 'POST':
        pid = request.form.get('pid')
        comments = getCommentPhoto(pid)
        return render_template('show_comments.html', message='Here are the comments!', comments=comments)
    else:
        return render_template('show_comments.html')

@app.route("/likes", methods=['GET','POST'])
@flask_login.login_required
def liketable():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        pid = request.form.get('pid')
        doc = request.form.get('doc')
        test = isLiked(uid, pid)
        if not test:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO LIKETABLE (UID, PID, DOC) VALUES ('{0}', '{1}', NOW())".format(uid, pid, doc))
            conn.commit()
            return render_template('likes.html', message='You Liked the Photo')
        else:
            return  render_template('likes.html', message='You Already Liked the photo')
    else:
        return render_template('likes.html')

@app.route('/showlikes', methods=['GET', 'POST'])
@flask_login.login_required
def show_likes():
    if request.method == 'POST':
        pid = request.form.get('pid')
        test = isPhotoExist(pid)
        if test:
            cursor = conn.cursor()
            likelist = getLikers(pid)
            countlikes = CountLike(pid)
            conn.commit()
            return render_template('showlikes.html', message='Here are the Likes', likes=likelist, counts=countlikes)
        else:
            return render_template('showlikes.html', message='Photo does not exist')
    else:
        return render_template('showlikes.html')

@app.route('/searchcomment', methods=['GET', 'POST'])
@flask_login.login_required
def search_comment():
    if request.method == 'POST':
        content = request.form.get('content')
        test = isCommentExist(content)
        if test:
            users = getUserByCmt(content)
            return render_template('searchcomment.html', message='Here are the users', users=users)
        else:
            return render_template('searchcomment.html', message='Comment Does not Exist!')
    else:
        return render_template('searchcomment.html')

@app.route('/recommendFriend', methods=['GET', 'POST'])
@flask_login.login_required
def rc_friend():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        recfriends = FriendRC(uid)
        print(recfriends)
        return render_template('recommendFriend.html', message='Here are your recommended friends!', recfriends=recfriends)
    else:
        return render_template('recommendFriend.html')

@app.route('/youmayalsolike', methods=['GET', 'POST'])
@flask_login.login_required
def alsolike():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        pptag_list = getUserPopularTag(uid)
        cursor = conn.cursor()
        cursor.execute("SELECT PID FROM PHOTO")
        ptlist = cursor.fetchall()
        rank = {}
        for i in ptlist:
            for j in pptag_list:
                cursor = conn.cursor()
                cursor.execute("SELECT P.PID FROM PHOTO P, ASSOCIATE A WHERE A.HASHTAG = '{0}' AND A.PID = '{1}' AND A.PID = P.PID".format(j, i[0]))
                rank_list = cursor.fetchall()
                for n in rank_list:
                    if n[0] not in rank:
                        rank[n[0]] = 1
                    else:
                        rank[n[0]] += 1
        sort_rank = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)
        new_list = []
        for key, value in sort_rank:
            cursor = conn.cursor()
            cursor.execute("SELECT DATA, PID, CAPTION FROM PHOTO WHERE PID = '{0}'".format(key))
            new_list += cursor.fetchall()
        return render_template('youmayalsolike.html', message='You may also like these!', photos=new_list, tags=pptag_list)
    else:
        return render_template('youmayalsolike.html')



def getUsersPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT DATA, PID, CAPTION FROM PHOTO WHERE UID = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]

def getUsersAlbums(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT AID, NAME, DOC FROM ALBUM WHERE UID = '{0}'".format(uid))
    return cursor.fetchall()

def getAIDfromPID(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT AID FROM PHOTO WHERE PID = '{0}'".format(pid))
    return cursor.fetchall()[0][0]

def getUsersPhotosFromAb(aid):
    cursor = conn.cursor()
    cursor.execute("SELECT DATA, PID, CAPTION FROM PHOTO WHERE AID = '{0}'".format(aid))
    return cursor.fetchall()

def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT UID FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

def isFriendUnique(uid1, uid2):
    cursor = conn.cursor()
    if cursor.execute("SELECT UID2 FROM FRIENDSHIP WHERE UID1 = '{0}' AND UID2 = '{1}'".format(uid1, uid2)):
        return False
    else:
        return True

#def getEmFromID(uid):
#    cursor = conn.cursor()
#    cursor.execute("SELECT email FROM Users WHERE UID = uid".format(uid))
#    return cursor.fetchall()

def getFriendID(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT UID2 FROM FRIENDSHIP WHERE UID1 = '{0}'".format(uid))
    return cursor.fetchall()

def getTop10():
    cursor = conn.cursor()
    cursor.execute("SELECT UID, email, first_name, last_name, contribution FROM Users ORDER BY CONTRIBUTION DESC LIMIT 10")
    return cursor.fetchall()

def isAlbumUnique(uid, aname):
    cursor = conn.cursor()
    if cursor.execute("SELECT AID FROM ALBUM WHERE UID = '{0}' AND NAME = '{1}'".format(uid, aname)):
        return False
    else:
        return True

def getAlbumIDwithName(uid, name):
    cursor = conn.cursor()
#    print(cursor.execute("SELECT AID FROM ALBUM WHERE UID = {0} AND NAME = '{1}'".format(uid, name)))
    cursor.execute("SELECT AID FROM ALBUM WHERE UID = '{0}' AND NAME = '{1}'".format(uid, name))
    return cursor.fetchall()[0][0]
# end login code

def isYourAlbum(uid, aid):
    cursor = conn.cursor()
    if cursor.execute("SELECT AID FROM ALBUM WHERE UID = '{0}' AND AID = '{1}'".format(uid, aid)):
        return True
    else:
        return False

def isPhotoExist(pid):
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM PHOTO WHERE PID = '{0}'".format(pid)):
        return True
    else:
        return False

def getPhotoWithTag(hashtag):
    cursor = conn.cursor()
    cursor.execute("SELECT p.DATA, p.CAPTION, p.PID FROM ASSOCIATE a JOIN PHOTO p ON a.PID = p.PID AND a.HASHTAG = '{0}'".format(hashtag))
    return cursor.fetchall()

def isTagExist(hashtag):
    cursor = conn.cursor()
    if cursor.execute("SELECT HASHTAG FROM TAG WHERE HASHTAG = '{0}'".format(hashtag)):
        return True
    else:
        return False

def getPhotoByUser(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT p.DATA, p.CAPTION, p.PID FROM Album a JOIN PHOTO p ON p.AID = a.AID AND a.UID = '{0}'".format(uid))
    return cursor.fetchall()

def getPhotoByUserWsTg(hashtag, uid):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DATA, PID, CAPTION FROM PHOTO WHERE PID IN "
        "(SELECT PID FROM ASSOCIATE WHERE HASHTAG = '{0}') AND PID IN (SELECT PID FROM PHOTO WHERE AID IN "
        "(SELECT AID FROM ALBUM WHERE UID = {1}))".format(hashtag, uid))
    return cursor.fetchall()

def getPopularTag():
    cursor = conn.cursor()
    cursor.execute("SELECT HASHTAG FROM ASSOCIATE AS A, PHOTO AS P WHERE A.PID = P.PID GROUP BY A.HASHTAG ORDER BY COUNT(P.PID) DESC LIMIT 5")
    return cursor.fetchall()

def getUserPopularTag(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT HASHTAG FROM ASSOCIATE AS A, PHOTO AS P WHERE A.PID =P.PID AND P.UID = '{0}' GROUP BY A.HASHTAG ORDER BY COUNT(P.PID) DESC LIMIT 5".format(uid))
    list_fetch = cursor.fetchall()
    tag_list = []
    for i in range(len(list_fetch)):
        tag_list.append(list_fetch[i][0])
    return tag_list


def isPTinAlbum(pid, aid):
    cursor = conn.cursor()
    if cursor.execute("SELECT AID FROM PHOTO WHERE PID = '{0}' AND AID = '{1}'".format(pid, aid)):
        return True
    else:
        return False

def getCommentPhoto(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT CONTENT, DOC, UID FROM COMMENT WHERE PID = '{0}'".format(pid))
    return cursor.fetchall()

def isLiked(uid, pid):
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM LIKETABLE WHERE UID = '{0}' AND PID = '{1}'".format(uid, pid)):
        return True
    else:
        return False

def CountLike(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(UID) FROM LIKETABLE WHERE PID = '{0}'".format(pid))
    return cursor.fetchall()

def getLikers(pid):
    cursor = conn.cursor()
    cursor.execute("SELECT UID FROM LIKETABLE WHERE PID = '{0}'".format(pid))
    return cursor.fetchall()

def isCommentExist(content):
    cursor = conn.cursor()
    if cursor.execute("SELECT CID FROM COMMENT WHERE CONTENT = '{0}'".format(content)):
        return True
    else:
        return False

def getUserByCmt(content):
    cursor = conn.cursor()
    cursor.execute("SELECT UID FROM COMMENT WHERE CONTENT = '{0}' AND UID <> 0 GROUP BY UID ORDER BY COUNT(*) DESC".format(content))
    return cursor.fetchall()

def FriendRC(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT F1.UID1 FROM FRIENDSHIP AS F1 WHERE F1.UID2 IN (SELECT F2.UID2 FROM FRIENDSHIP AS F2 WHERE F2.UID1={0}) GROUP BY F1.UID1 "
        "HAVING F1.UID1 <> {1} AND F1.UID1 NOT IN (SELECT F2.UID2 FROM FRIENDSHIP AS F2 WHERE F2.UID1={2}) "
        "ORDER BY COUNT(*) DESC".format(uid, uid, uid))
    return cursor.fetchall()

def YouHaveComment(uid):
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM COMMENT WHERE UID = '{0}'".format(uid)):
        return True
    else:
        return False


@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('hello.html', name=flask_login.current_user.id, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

#UPLOAD_FOLDER = '/Users/runtongyan/Downloads/PhotoShare2/uploads/'
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@app.route('/upload', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        name = request.form.get('name')
        aid = getAlbumIDwithName(uid, name)
        print(aid)
#        tag = request.form.get('tag')
        caption = request.form.get('caption')
        print(caption)
        photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO PHOTO (DATA, AID, CAPTION, UID) VALUES ('{0}', '{1}', '{2}', '{3}' )".format(photo_data, aid, caption, uid))
        cursor.execute("UPDATE Users SET contribution = contribution+1 WHERE UID = {0}".format(uid))
        conn.commit()
        conn.commit()
#        uploadfile = request.files['uploadFile']
#        filename = uploadfile.filename
#        uploadfile.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return render_template('hello.html', name=flask_login.current_user.id, message='Photo uploaded!',
                               photos=getUsersPhotosFromAb(aid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('upload.html')


# end photo uploading code


# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('hello.html', message='Welecome to Photoshare', contributions=getTop10())


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
