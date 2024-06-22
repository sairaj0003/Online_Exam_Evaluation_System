from flask import Flask, render_template, request, flash, session, url_for, redirect, send_file
# from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
# from wtforms import Form, StringField, PasswordField, validators
# from passlib.hash import sha256_crypt
from functools import wraps
import os
from db import connection
import gc
import json
import base64

import nltk
from nltk.tokenize import word_tokenize
# nltk.download('punkt') # Uncomment if not available
from nltk.corpus import stopwords
# nltk.download('stopwords')
from nltk.stem.porter import PorterStemmer

app = Flask(__name__)
app.secret_key = os.urandom(24)

# login_manager = LoginManager()
# login_manager.login_view = "login"
# login_manager.session_protection = "strong"
# login_manager.setup_app(app)

# class RegistrationForm(Form):
#     fname = StringField('First Name', validators=[
#         validators.InputRequired(),
#         validators.Length(min=2, max=20)
#     ])
#     lname = StringField('Last Name', validators=[
#         validators.InputRequired(),
#         validators.Length(min=2, max=20)
#     ])
#     rollnumber = StringField('Roll Number', validators=[validators.InputRequired()])
#     password = PasswordField('Password', validators=[
#         validators.InputRequired(),
#         validators.EqualTo('repassword', message='Passwords do not match')
#     ])
#     repassword = PasswordField('Repeat Password', validators=[validators.InputRequired()])
#     email = StringField('Email', validators=[
#         validators.InputRequired(),
#         validators.Email()
#     ])
#     mob_no = StringField('Mobile Number', validators=[
#         validators.InputRequired(),
#         validators.Length(min=10, max=15)
#     ])
#     department = StringField('Department', validators=[validators.InputRequired()])
#     sem = StringField('Semester', validators=[validators.InputRequired()])
#     dob = StringField('Date of Birth')
#     guardian = StringField('Guardian Name')
#     g_mob_no = StringField('Guardian Mobile Number')
#     img = StringField('Profile Picture')
#     about = StringField('About Me')

# session.pop('_flashes', None)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            if session['student'] == True:
                return f(*args, **kwargs)
        
        flash('You need to login first.')
        return redirect(url_for('login'))
    return wrap

def f_login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            if session['faculty'] == True:
                return f(*args, **kwargs)

        flash('You need to login first.')
        return redirect(url_for('flogin'))
    return wrap

@app.route("/")
def index():
    return render_template("index.html")
    
@app.route("/login", methods = ['POST','GET'])
def login():
    msg = " "
    if request.method == 'POST':
        rollnumber = request.form.get('rollnumber')
        password = request.form.get('password')

        cur, con = connection()

        cur.execute("SELECT * FROM STUDENT WHERE rollnumber = (%s)", (rollnumber,))
        y = cur.rowcount
        x = cur.fetchone()

        if y == 0:
            msg = "No User Found!"
            return render_template('login.html', msg=msg)

        dpassword = x[3]
        if dpassword != password:
            msg = "Incorrect Password!"
            return render_template('login.html', msg=msg)

        cur.close()
        con.close()
        gc.collect()
        session['logged_in'] = True
        session['username'] = rollnumber
        session['student'] =  True
        session['faculty'] =  False

        return redirect(url_for('dashboard', username = (rollnumber)))
   
    return render_template("login.html")
    
@app.route("/flogin", methods = ['POST','GET'])
def flogin():
    msg = " "
    if request.method == 'POST':
        rollnumber = request.form.get('rollnumber')
        password = request.form.get('password')

        cur, con = connection()

        cur.execute("SELECT * FROM faculty WHERE rollnumber = (%s)", (rollnumber,))
        y = cur.rowcount
        x = cur.fetchone()

        if y == 0:
            msg = "No User Found!"
            return render_template('flogin.html', msg=msg)

        dpassword = x[3]
        if dpassword != password:
            msg = "Incorrect Password!"
            return render_template('flogin.html', msg=msg)

        cur.close()
        con.close()
        gc.collect()
        session['logged_in'] = True
        session['username'] = rollnumber
        session['faculty'] =  True
        session['student'] =  False

        return redirect(url_for('fdashboard', username = (rollnumber)))

    return render_template("flogin.html")
    
@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    if 'faculty' in session:
        session.pop('faculty', None)
    session.clear()
    gc.collect
    return redirect(url_for('index'))
    
@app.route("/register", methods = ['POST','GET'])
def register():
    if request.method == 'POST': #and form.validate():
        msg = " "
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        rollnumber = request.form.get('rollnumber')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        email = request.form.get('email')
        mob_no = request.form.get('mob_no')
        department = request.form.get('department')
        sem = request.form.get('sem')
        dob = request.form.get('dob')
        guardian = request.form.get('guardian')
        g_mob_no = request.form.get('g_mob_no')
        # img = request.form.get('img')
        img = request.files['img'].read()

        if department == '0':
            msg = "Select Department"
            return render_template("register.html", msg=msg)

        if sem == '0':
            msg = "Select Sem"
            return render_template("register.html", msg=msg)

        if password != repassword:
            msg = "Passwords not matched"
            return render_template("register.html", msg=msg)

        cur, con = connection()

        cur.execute("SELECT * FROM STUDENT WHERE rollnumber = (%s)", (rollnumber,))
        x = cur.rowcount

        if x > 0:
            msg = "Roll Number already exists!"
            return render_template('register.html', msg=msg)

        cur.execute("SELECT * FROM STUDENT WHERE email = (%s)", (email,))
        x = cur.rowcount

        if x > 0:
            msg = "Email already exists!"
            return render_template('register.html', msg=msg)

        cur.execute("SELECT * FROM STUDENT WHERE mob_no = (%s)", (mob_no,))
        x = cur.rowcount

        if x > 0:
            msg = "Phone Number already exists!"
            return render_template('register.html', msg=msg)
        else:
            cur.execute("INSERT INTO student (fname, lname, rollnumber, password, email, mob_no, department, sem, dob, guardian, g_mob_no, img) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(fname, lname, rollnumber, password, email, mob_no, department, sem, dob, guardian, g_mob_no, img, ))
            con.commit()
            cur.close()
            con.close()
            gc.collect()
            session['logged_in'] = True
            session['username'] = rollnumber
            session['student'] =  True
            session['faculty'] =  False

        return redirect(url_for('dashboard', username = (rollnumber)))
        
    return render_template("register.html")

@app.route("/fregister", methods = ['POST','GET'])
def fregister():
    if request.method == 'POST': #and form.validate():
        msg = " "
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        rollnumber = request.form.get('rollnumber')
        password = request.form.get('password')
        repassword = request.form.get('repassword')
        email = request.form.get('email')
        mob_no = request.form.get('mob_no')
        department = request.form.get('department')
        img = request.form.get('img')
        about = request.form.get('about')

        if department == '0':
            msg = "Select Department"
            return render_template("fregister.html", msg=msg)

        if password != repassword:
            msg = "Passwords not matched"
            return render_template("fregister.html", msg=msg)

        cur, con = connection()

        cur.execute("SELECT * FROM faculty WHERE rollnumber = (%s)", (rollnumber,))
        x = cur.rowcount

        if x > 0:
            msg = "Roll Number already exists!"
            return render_template('fregister.html', msg=msg)

        cur.execute("SELECT * FROM faculty WHERE email = (%s)", (email,))
        x = cur.rowcount

        if x > 0:
            msg = "Email already exists!"
            return render_template('fregister.html', msg=msg)

        cur.execute("SELECT * FROM faculty WHERE mob_no = (%s)", (mob_no,))
        x = cur.rowcount

        if x > 0:
            msg = "Phone Number already exists!"
            return render_template('fregister.html', msg=msg)
        else:
            cur.execute("INSERT INTO faculty (fname, lname, rollnumber, password, email, mob_no, department) VALUES (%s, %s, %s, %s, %s, %s, %s)",(fname, lname, rollnumber, password, email, mob_no, department, ))
            con.commit()
            cur.close()
            con.close()
            gc.collect()
            session['logged_in'] = True
            session['username'] = rollnumber
            session['faculty'] = True
            session['student'] =  False

        return redirect(url_for('fdashboard', username = (rollnumber)))
        
    return render_template("fregister.html")

@app.route("/dashboard/<username>")
@login_required
def dashboard(username):
    if username != session['username']:
        return render_template("login.html")
    cur, con = connection()

    cur.execute("SELECT * FROM student WHERE rollnumber = (%s)",(username,))
    # data = cur.execute("SELECT * FROM student WHERE rollnumber = (%s)",(session['username'],))

    x = cur.fetchone()

    fname = x[0]
    lname = x[1]
    cur.close()
    con.close()
    gc.collect()

    return render_template("dashboard.html", fname = fname, lname = lname, rollnumber=username)

@app.route("/fdashboard/<username>")
@f_login_required
def fdashboard(username):
    if username != session['username']:
        return render_template("flogin.html")
    cur, con = connection()

    data = cur.execute("SELECT * FROM faculty WHERE rollnumber = (%s)",(username,))
    x = cur.fetchone()

    fname = x[0]
    lname = x[1]
    cur.close()
    con.close()
    gc.collect()

    return render_template("fdashboard.html", fname = fname, lname = lname, rollnumber=username)

@app.route("/profile/<username>")
@login_required
def profile(username):
    if username != session['username']:
        return render_template("login.html")
    cur, con = connection()

    cur.execute("SELECT * FROM student WHERE rollnumber = (%s)",(username,))
    # data = cur.execute("SELECT * FROM student WHERE rollnumber = (%s)",(session['username'],))

    data = cur.fetchone()

    img = base64.b64encode(data[11]).decode('utf-8') if data[11] else None
    
    data = list(data)
    data[11] = img

    cur.close()
    con.close()
    gc.collect()

    return render_template("profile.html", data=data)

@app.route("/edit/<username>", methods = ['POST','GET'])
@login_required
def edit(username):
    if username != session['username']:
        return render_template("login.html")
    cur, con = connection()

    cur.execute("SELECT * FROM student WHERE rollnumber = (%s)",(username,))
    # data = cur.execute("SELECT * FROM student WHERE rollnumber = (%s)",(session['username'],))

    data = cur.fetchone()

    img = base64.b64encode(data[11]).decode('utf-8') if data[11] else None
    
    data = list(data)
    data[11] = img

    if request.method == 'POST': #and form.validate():
        msg = " "
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        # oldpassword = request.form.get('oldpassword')
        # password = request.form.get('password')
        # repassword = request.form.get('repassword')
        email = request.form.get('email')
        mob_no = request.form.get('mob_no')
        department = request.form.get('department')
        sem = request.form.get('sem')
        dob = request.form.get('dob')
        guardian = request.form.get('guardian')
        g_mob_no = request.form.get('g_mob_no')
        about = request.form.get('about')
        # img = request.form.get('img')
        # img = request.files['img'].read()

        if department == '0':
            msg = "Select Department"
            return render_template("edit.html", msg=msg, data=data)

        if sem == '0':
            msg = "Select Sem"
            return render_template("edit.html", msg=msg, data=data)

        # if password != repassword:
        #     msg = "Passwords not matched"
        #     return render_template("edit.html", msg=msg)

        # if oldpassword != data[3]:
        #     msg = "Old Password is Incorrect"
        #     return render_template("edit.html", msg=msg)

        cur, con = connection()


        cur.execute("SELECT * FROM STUDENT WHERE email = (%s) AND email != (%s)", (email,data[4]))
        x = cur.rowcount

        if x > 0:
            msg = "Email already exists!"
            return render_template('edit.html', msg=msg, data=data)

        cur.execute("SELECT * FROM STUDENT WHERE mob_no = (%s) AND mob_no != (%s)", (mob_no,data[5]))
        x = cur.rowcount

        if x > 0:
            msg = "Phone Number already exists!"
            return render_template('edit.html', msg=msg, data=data)
        else:
            # cur.execute("INSERT INTO student (fname, lname, rollnumber, password, email, mob_no, department, sem, dob, guardian, g_mob_no, img) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(fname, lname, rollnumber, password, email, mob_no, department, sem, dob, guardian, g_mob_no, img, ))
            cur.execute("UPDATE student SET fname = %s, lname = %s, email = %s, mob_no = %s, department = %s, sem = %s, dob = %s, guardian = %s, g_mob_no = %s, about = %s WHERE rollnumber = %s", (fname, lname, email, mob_no, department, sem, dob, guardian, g_mob_no, about, username))
            con.commit()
            cur.close()
            con.close()
            gc.collect()

        return redirect(url_for('profile', username = (username)))

    cur.close()
    con.close()
    gc.collect()

    return render_template("edit.html", data=data)

@app.route("/fedit/<username>", methods = ['POST','GET'])
@f_login_required
def fedit(username):
    if username != session['username']:
        return render_template("flogin.html")
    cur, con = connection()

    cur.execute("SELECT * FROM faculty WHERE rollnumber = (%s)",(username,))
    # data = cur.execute("SELECT * FROM student WHERE rollnumber = (%s)",(session['username'],))

    data = cur.fetchone()

    img = base64.b64encode(data[7]).decode('utf-8') if data[7] else None
    
    data = list(data)
    data[7] = img

    if request.method == 'POST': #and form.validate():
        msg = " "
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        # oldpassword = request.form.get('oldpassword')
        # password = request.form.get('password')
        # repassword = request.form.get('repassword')
        email = request.form.get('email')
        mob_no = request.form.get('mob_no')
        department = request.form.get('department')
        about = request.form.get('about')
        # img = request.form.get('img')
        # img = request.files['img'].read()

        if department == '0':
            msg = "Select Department"
            return render_template("fedit.html", msg=msg, data=data)

        # if password != repassword:
        #     msg = "Passwords not matched"
        #     return render_template("edit.html", msg=msg)

        # if oldpassword != data[3]:
        #     msg = "Old Password is Incorrect"
        #     return render_template("edit.html", msg=msg)

        cur, con = connection()


        cur.execute("SELECT * FROM faculty WHERE email = (%s) AND email != (%s)", (email, data[4]))
        x = cur.rowcount

        if x > 0:
            msg = "Email already exists!"
            return render_template('fedit.html', msg=msg, data=data)

        cur.execute("SELECT * FROM faculty WHERE mob_no = (%s) AND mob_no != (%s)", (mob_no, data[5]))
        x = cur.rowcount

        if x > 0:
            msg = "Phone Number already exists!"
            return render_template('fedit.html', msg=msg, data=data)
        else:
            # cur.execute("INSERT INTO student (fname, lname, rollnumber, password, email, mob_no, department, sem, dob, guardian, g_mob_no, img) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(fname, lname, rollnumber, password, email, mob_no, department, sem, dob, guardian, g_mob_no, img, ))
            cur.execute("UPDATE faculty SET fname = %s, lname = %s, email = %s, mob_no = %s, department = %s, about = %s WHERE rollnumber = %s", (fname, lname, email, mob_no, department, about, username))
            con.commit()
            cur.close()
            con.close()
            gc.collect()

        return redirect(url_for('fprofile', username = (username)))

    cur.close()
    con.close()
    gc.collect()

    return render_template("fedit.html", data=data)

@app.route("/fprofile/<username>")
@f_login_required
def fprofile(username):
    if username != session['username']:
        return render_template("flogin.html")
    cur, con = connection()

    cur.execute("SELECT * FROM faculty WHERE rollnumber = (%s)",(username,))
    data = cur.fetchone()

    cur.close()
    con.close()
    gc.collect()

    return render_template("fprofile.html", data=data)

@app.route("/addExam", methods = ['POST','GET'])
@f_login_required
def addExam():
    if request.method == 'POST':
        exam_name = request.form.get('exam_name')
        img = request.files['img'].read()
        # test_id = request.form.get('test_id')
        dept_sem = request.form.getlist('options')
        # ques_id = request.form.get('ques_id')
        question = request.form.get('question')
        q_img = request.files['q_img'].read()
        opt_A = request.form.get('opt_A')
        opt_A_img = request.files['opt_A_img'].read()
        opt_B = request.form.get('opt_B')
        opt_B_img = request.files['opt_B_img'].read()
        opt_C = request.form.get('opt_C')
        opt_C_img = request.files['opt_C_img'].read()
        opt_D = request.form.get('opt_D')
        opt_D_img = request.files['opt_D_img'].read()
        opt_ans = request.form.get('opt_ans')
        answer = request.form.get('answer')
        q_marks = request.form.get('q_marks')
        start_datetime = request.form.get('start_datetime')
        end_datetime = request.form.get('end_datetime')

        json_data = json.dumps(dept_sem)

        cur, con = connection()

        cur.execute("SELECT MAX(test_id) FROM exam")
        x = cur.fetchone()
        print(x)
        test_id = 1
        if x[0]:
            test_id = int(x[0]) + 1
        print(test_id)

        cur.execute("INSERT INTO question (test_id, ques_id, rollnumber, question, q_img, opt_A, opt_A_img, opt_B, opt_B_img, opt_C, opt_C_img, opt_D, opt_D_img, opt_ans, answer, q_marks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(test_id, 1, session['username'], question, q_img, opt_A, opt_A_img, opt_B, opt_B_img, opt_C, opt_C_img, opt_D, opt_D_img, opt_ans, answer, q_marks, ))
        con.commit()
        cur.execute("INSERT INTO exam (test_id, exam_name, rollnumber, dept_sem, start_datetime, end_datetime, img) VALUES (%s, %s, %s, %s, %s, %s, %s)",(test_id, exam_name, session['username'], json_data, start_datetime, end_datetime, img, ))
        con.commit()
        cur.close()
        con.close()
        gc.collect()

        return redirect(url_for('addQuestion', testid=(test_id)))
        
    return render_template("addExam.html")

@app.route("/addQuestion/<testid>/", methods = ['POST','GET'])
@f_login_required
def addQuestion(testid):

    cur, con = connection()

    cur.execute("SELECT * FROM question WHERE test_id = (%s)", (testid,))
    x = cur.rowcount
    print(x)

    if request.method == 'POST':
        # ques_id = request.form.get('ques_id')
        question = request.form.get('question')
        q_img = request.files['q_img'].read()
        opt_A = request.form.get('opt_A')
        opt_A_img = request.files['opt_A_img'].read()
        opt_B = request.form.get('opt_B')
        opt_B_img = request.files['opt_B_img'].read()
        opt_C = request.form.get('opt_C')
        opt_C_img = request.files['opt_C_img'].read()
        opt_D = request.form.get('opt_D')
        opt_D_img = request.files['opt_D_img'].read()
        opt_ans = request.form.get('opt_ans')
        answer = request.form.get('answer')
        q_marks = request.form.get('q_marks')

        if x == 0:
            return redirect(url_for('addExam'))
        else:
            cur.execute("SELECT MAX(ques_id) FROM question WHERE test_id = (%s)", (testid,))
            x = cur.fetchone()
            ques_id = int(x[0]) + 1
            print(ques_id)
        
            cur.execute("INSERT INTO question (test_id, ques_id, rollnumber, question, q_img, opt_A, opt_A_img, opt_B, opt_B_img, opt_C, opt_C_img, opt_D, opt_D_img, opt_ans, answer, q_marks) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(testid, ques_id, session['username'], question, q_img, opt_A, opt_A_img, opt_B, opt_B_img, opt_C, opt_C_img, opt_D, opt_D_img, opt_ans, answer, q_marks, ))
            con.commit()
            cur.close()
            con.close()
            gc.collect()

        return redirect(url_for('addQuestion', testid=testid))
        
    return render_template("addQuestion.html", testid=testid, x=x)

@app.route("/updateQuestion/<testid>/<qid>", methods = ['POST','GET'])
@f_login_required
def updateQuestion(testid, qid):

    cur, con = connection()

    cur.execute("SELECT * FROM question WHERE test_id = (%s) AND ques_id = (%s)", (testid, qid))
    question = cur.fetchone()

    cur.execute("SELECT * FROM question WHERE test_id = (%s)", (testid,))
    x = cur.rowcount

    if request.method == 'POST':
        # ques_id = request.form.get('ques_id')
        question = request.form.get('question')
        q_img = request.files['q_img'].read()
        opt_A = request.form.get('opt_A')
        opt_A_img = request.files['opt_A_img'].read()
        opt_B = request.form.get('opt_B')
        opt_B_img = request.files['opt_B_img'].read()
        opt_C = request.form.get('opt_C')
        opt_C_img = request.files['opt_C_img'].read()
        opt_D = request.form.get('opt_D')
        opt_D_img = request.files['opt_D_img'].read()
        opt_ans = request.form.get('opt_ans')
        answer = request.form.get('answer')
        q_marks = request.form.get('q_marks')

        cur, con = connection()
        cur.execute("UPDATE question SET rollnumber = %s, question = %s, q_img = %s, opt_A = %s, opt_A_img = %s, opt_B = %s, opt_B_img = %s, opt_C = %s, opt_C_img = %s, opt_D = %s, opt_D_img = %s, opt_ans = %s, answer = %s, q_marks = %s WHERE test_id = %s AND ques_id = %s", (session['username'], question, q_img, opt_A, opt_A_img, opt_B, opt_B_img, opt_C, opt_C_img, opt_D, opt_D_img, opt_ans, answer, q_marks, testid, qid, ))
        con.commit()
        cur.close()
        con.close()
        gc.collect()

        return redirect(url_for('addQuestion', testid=testid))
        
    return render_template("addQuestion.html", testid=testid, question=question, x=x)

@app.route("/deleteQuestion/<testid>/<qid>", methods = ['POST','GET'])
@f_login_required
def deleteQuestion(testid, qid):

    cur, con = connection()
    cur.execute("DELETE FROM question WHERE test_id = %s AND ques_id = %s", (testid, qid, ))
    cur.execute("UPDATE question SET ques_id = ques_id - 1 WHERE test_id = %s AND ques_id > %s", (testid, qid, ))
    con.commit()
    cur.close()
    con.close()
    gc.collect()

    return redirect(url_for('addQuestion', testid=testid))

@app.route("/deleteExam/<testid>/", methods = ['POST','GET'])
@f_login_required
def deleteExam(testid):

    cur, con = connection()
    cur.execute("DELETE FROM exam WHERE test_id = %s", (testid, ))
    cur.execute("UPDATE exam SET test_id = test_id - 1 WHERE test_id > %s", (testid, ))
    cur.execute("DELETE FROM question WHERE test_id = %s", (testid, ))
    cur.execute("UPDATE question SET test_id = test_id - 1 WHERE test_id > %s", (testid, ))
    cur.execute("DELETE FROM response WHERE test_id = %s", (testid, ))
    cur.execute("UPDATE response SET test_id = test_id - 1 WHERE test_id > %s", (testid, ))
    cur.execute("DELETE FROM results WHERE test_id = %s", (testid, ))
    cur.execute("UPDATE results SET test_id = test_id - 1 WHERE test_id > %s", (testid, ))
    con.commit()
    cur.close()
    con.close()
    gc.collect()

    return redirect(url_for('exams'))

@app.route("/exams")
@f_login_required
def exams():
    cur, con = connection()

    # data = cur.execute("SELECT * FROM exam WHERE rollnumber = (%s)",(username,))
    cur.execute("SELECT * FROM exam WHERE start_datetime < NOW() AND end_datetime > NOW() ORDER BY end_datetime")
    a_exam_data = cur.fetchall()
    
    cur.execute("SELECT * FROM exam WHERE start_datetime > NOW() ORDER BY end_datetime")
    f_exam_data = cur.fetchall()
    
    cur.execute("SELECT * FROM exam WHERE end_datetime < NOW() ORDER BY end_datetime")
    p_exam_data = cur.fetchall()
    
    # print(exam_data)
    cur.close()
    con.close()
    gc.collect()

    return render_template("exams.html", exams=a_exam_data, f_exam_data=f_exam_data, p_exam_data=p_exam_data, rollnumber=session['username'])

@app.route("/myExams")
@login_required
def myExams():
    cur, con = connection()

    cur.execute("SELECT department, sem FROM student WHERE rollnumber = (%s)",(session['username'],))
    dept = cur.fetchall()
    x = '"' + (dept[0][0]).lower() + str(dept[0][1]) + '"'
    print(x)
    cur.execute("SELECT e.* FROM exam e LEFT JOIN results r ON e.test_id = r.test_id AND r.rollnumber = (%s) WHERE JSON_CONTAINS(e.dept_sem, (%s)) AND r.rollnumber IS NULL AND e.start_datetime < NOW() AND e.end_datetime > NOW() ORDER BY e.end_datetime",(session['username'], x,))
    a_exam_data = cur.fetchall()
    # print(a_exam_data)
    for i in range(len(a_exam_data)):
        a_exam_data[i] = list(a_exam_data[i])
        img = base64.b64encode(a_exam_data[i][6]).decode('utf-8') if a_exam_data[i][6] else None
            
        a_exam_data[i][6] = img

    cur.execute("SELECT * FROM exam WHERE JSON_CONTAINS(dept_sem, (%s)) AND start_datetime > NOW() ORDER BY end_datetime",(x,))
    f_exam_data = cur.fetchall()
    # print(f_exam_data)
    for i in range(len(f_exam_data)):
        f_exam_data[i] = list(f_exam_data[i])
        img = base64.b64encode(f_exam_data[i][6]).decode('utf-8') if f_exam_data[i][6] else None
            
        f_exam_data[i][6] = img

    cur.execute("SELECT e.* FROM exam e JOIN results r ON e.test_id = r.test_id AND r.rollnumber = (%s) WHERE JSON_CONTAINS(e.dept_sem, (%s)) ORDER BY e.end_datetime",(session['username'], x, ))
    at_exam_data = cur.fetchall()
    print(at_exam_data)
    for i in range(len(at_exam_data)):
        at_exam_data[i] = list(at_exam_data[i])
        img = base64.b64encode(at_exam_data[i][6]).decode('utf-8') if at_exam_data[i][6] else None
            
        at_exam_data[i][6] = img

    cur.execute("SELECT * FROM exam WHERE JSON_CONTAINS(dept_sem, (%s)) AND end_datetime < NOW() ORDER BY end_datetime",(x,))
    p_exam_data = cur.fetchall()
    # print(p_exam_data)
    for i in range(len(p_exam_data)):
        p_exam_data[i] = list(p_exam_data[i])
        img = base64.b64encode(p_exam_data[i][6]).decode('utf-8') if p_exam_data[i][6] else None
            
        p_exam_data[i][6] = img

    cur.close()
    con.close()
    gc.collect()

    return render_template("myExams.html", exams=a_exam_data, f_exam_data=f_exam_data, at_exam_data=at_exam_data, p_exam_data=p_exam_data, rollnumber=session['username'])

@app.route("/exam/<testid>/<qid>/", methods = ['POST','GET'])
@login_required
def exam(testid, qid):
    msg = " "
    cur, con = connection()

    cur.execute("SELECT * FROM question WHERE test_id = (%s) AND ques_id = (%s)", (testid, qid))
    question = cur.fetchone()
    # print(question)
    cur.execute("SELECT COUNT(*) FROM question WHERE test_id = (%s)", (testid,))
    count = cur.fetchone()[0]
    # print(count)
    
    cur.execute("SELECT * FROM response WHERE rollnumber = (%s) AND test_id = (%s) AND ques_id = (%s)", (session['username'], testid, qid))
    x = cur.rowcount
    data = cur.fetchone()
    print(data)

    question = list(question)

    for i in (4, 6, 8, 10, 12):
        img = base64.b64encode(question[i]).decode('utf-8') if question[i] else None
        
        question[i] = img
    
    if request.method == 'POST': #and form.validate():
        opt_ans = request.form.get('opt_ans')
        answer = request.form.get('answer')
        
        # print(opt_ans)
        # print(type(opt_ans))
        # print(answer)
        # print(type(answer))

        q_marks = 0

        if opt_ans != '0' and opt_ans:
            print("opt")
            if opt_ans == question[13]:
                q_marks = question[15]
        elif answer:
            if answer != " ":
                ans = [question[14], answer]
                n_ans = []

                for i in ans:
                    text = i
                    tokens = word_tokenize(text)
                    sw=nltk.corpus.stopwords.words('english')
                    s_tokens = set([token.lower() for token in tokens if not token.lower() in sw])
                    ps = PorterStemmer()
                    n_ans.append([ps.stem(word) for word in list(s_tokens)])

                if len(n_ans[0]) != 0:
                    q_marks = question[15] * (len(set(n_ans[0]).intersection(set(n_ans[1])))/len(n_ans[0]))

        cur, con = connection()  
        cur.execute("SELECT * FROM response WHERE rollnumber = (%s) AND test_id = (%s) AND ques_id = (%s)", (session['username'], testid, qid))
        x = cur.rowcount
        if x == 0:
            cur.execute("INSERT INTO response (rollnumber, test_id, ques_id, opt_ans, answer, q_marks) VALUES (%s, %s, %s, %s, %s, %s)",(session['username'], testid, qid, opt_ans, answer, q_marks, ))
        else:
            cur.execute("UPDATE response SET opt_ans = %s, answer = %s, q_marks = %s WHERE rollnumber = %s AND test_id = %s AND ques_id = %s", (opt_ans, answer, q_marks, session['username'], testid, qid))

        if int(qid)!=count:
            return redirect(url_for('exam', testid=testid, qid=(int(qid)+1)))
    
    con.commit()
    cur.close()
    con.close()
    gc.collect()

    return render_template("exam.html", question=question, count=count, data=data)

@app.route("/result/<testid>/")
@login_required
def result(testid):
    msg = " "
    cur, con = connection()

    cur.execute("SELECT SUM(q_marks) FROM question WHERE test_id = (%s)", (testid,))
    totalScore = cur.fetchone()[0]
    print(totalScore)
    cur.execute("SELECT SUM(q_marks) FROM response WHERE rollnumber = (%s) AND test_id = (%s)", (session['username'], testid,))
    myScore = cur.fetchone()[0]
    print(myScore)

    cur.execute("SELECT * FROM results WHERE rollnumber = (%s) AND test_id = (%s)", (session['username'], testid))
    x = cur.rowcount
    if x == 0:
        cur.execute("INSERT INTO results (rollnumber, test_id, marks_obtained, total_marks) VALUES (%s, %s, %s, %s)",(session['username'], testid, myScore, totalScore))

    con.commit()
    cur.close()
    con.close()
    gc.collect()

    return render_template("result.html", totalScore=totalScore, myScore=myScore, rollnumber=session['username'])

@app.route("/myResults//")
@login_required
def myResults():
    msg = " "
    cur, con = connection()

    cur.execute("SELECT r.marks_obtained, r.total_marks, e.exam_name FROM results r JOIN exam e ON r.test_id = e.test_id WHERE r.rollnumber = (%s) ORDER BY e.end_datetime", (session['username'],))
    data = cur.fetchall()
    print(data)
    con.commit()
    cur.close()
    con.close()
    gc.collect()

    return render_template("myResults.html", data=data, rollnumber=session['username'])

@app.route("/results")
@f_login_required
def results():
    cur, con = connection()

    cur.execute("SELECT * FROM exam ORDER BY test_id DESC")
    exams = cur.fetchall()
    # print(exams)
    # ds = " "
    # if exams:
        # ds = json.loads(exams[0][3])
    # print(exams[1][3][2:6])
    con.commit()
    cur.close()
    con.close()
    gc.collect()

    return render_template("results.html", exams=exams, rollnumber=session['username'])

@app.route("/dsresults/<testid>/<ds>")
@f_login_required
def dsresults(testid, ds):
    msg = " "
    cur, con = connection()

    cur.execute("SELECT dept_sem FROM exam WHERE test_id = (%s)", (testid, ))
    data = cur.fetchone()
    print(data)
    dsd = json.loads(data[0])
    print(dsd)
    dept = ds[0:3].upper()
    sem = ds[-1]
    print(dept,sem)
    ds = '"' + ds + '"'

    #     SELECT s.student_id, s.name, d.dept_name, r.marks_obtained, e.exam_name
    # FROM students s
    # JOIN departments d ON s.department_id = d.department_id
    # JOIN results r ON s.student_id = r.student_id
    # JOIN exams e ON r.exam_id = e.exam_id
    # WHERE d.dept_name = 'Computer Science'   -- Condition 1: specific department
    #   AND e.exam_name = 'Final Exam'         -- Condition 2: specific exam
    #   AND r.marks_obtained > 70;  

    cur.execute("SELECT r.rollnumber, r.marks_obtained, r.total_marks FROM results r JOIN exam e ON r.test_id = e.test_id JOIN student s ON r.rollnumber = s.rollnumber WHERE r.test_id = (%s) AND JSON_CONTAINS(e.dept_sem, %s) AND s.department = (%s) AND s.sem = (%s)", (testid, ds, dept, sem))
    results = cur.fetchall()
    print(results)
    con.commit()
    cur.close()
    con.close()
    gc.collect()

    return render_template("dsresults.html", results=results, dsd=dsd, testid=testid, rollnumber=session['username'])

if __name__ == "__main__":
    # app.run(host="192.168.29.161", debug='True')
    app.run(debug='True')
