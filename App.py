from flask import Flask, redirect, render_template, flash, request, session
from flask_mysqldb import MySQL
from wtforms import StringField, IntegerField, PasswordField, validators
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from flask_wtf import Form
from werkzeug.datastructures import CombinedMultiDict
import recognize
import os
from datetime import datetime
from flask_wtf.file import FileField, FileRequired

now = datetime.now()
app = Flask(__name__)
app.secret_key = "super secret key"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Staystrongforyourself26@'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['UPLOAD_FOLDER']="/home/shruti/dlib-19.6/images/"
mysql = MySQL(app)


class RegisterForm(Form):
    teacher_id = StringField('Teacher Id', validators=[validators.length(min=1, max=50)])
    name = StringField('Name', validators=[validators.length(min=1, max=50)])
    email = StringField('College Email Id', validators=[validators.length(min=1, max=50)])
    phoneNo = IntegerField('Phone Number')
    username = StringField('Username', validators=[validators.length(min=1, max=50)])
    password = PasswordField('Password', [validators.DataRequired(),
                                          validators.EqualTo('confirm', message="Passwords do not match")])
    confirm = PasswordField('Confirm Password')
class RegisterStudentForm(Form):
    student_id = StringField('Student Id', validators=[validators.length(min=1, max=50)])
    name = StringField('Name', validators=[validators.length(min=1, max=50)])
    email = StringField('College Email Id', validators=[validators.length(min=1, max=50)])
    phoneNo = IntegerField('Phone Number')
    photo = FileField(validators=[FileRequired()])


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if (request.method == "GET"):
        return render_template('register.html', form=form)
    else:
        if (request.method == "POST" and form.validate()):
            teacher_id = form.teacher_id.data
            name = form.name.data
            email = form.email.data
            phoneNo = int(form.phoneNo.data)
            username = form.username.data
            password = str(sha256_crypt.encrypt(form.password.data))
            cur = mysql.connection.cursor()
            cur.execute('insert into instructor values(%s,%s,%s,%s,%s,%s)',
                        (teacher_id, name, email, phoneNo, username, password))
            mysql.connection.commit()
            cur.close()
            flash('You have successfully registered ', 'success')
            return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute('select * from instructor where username=%s', [username])
        if (result > 0):
            data = cur.fetchone()
            data_pass = data['password']
            if sha256_crypt.verify(password, data_pass):
                session['logged_in'] = True
                session['username'] = username
                session['id']=data['teacher_id']
                flash('you are now logged in', 'success')
                return redirect('/')
            else:
                error = "Invalid login"
                return render_template('login.html', error=error)
            cur.close()
        else:
            error = "No user found"
            return render_template('login.html', error=error)

@app.route('/logout',methods=['GET','POST'])
def logout():
        session.clear()
        flash('You have successfully logged out','success')
        return redirect('/')


@app.route('/my_courses/<string:id>',methods=['GET'])
def display(id):
    cur=mysql.connection.cursor()
    result=cur.execute('select courses.course_id , course_name from courses,tcourses where tcourses.teacher_id=%s and tcourses.course_id=courses.course_id',[id])
    if(result>0):
        data=cur.fetchall()
        return render_template('displaycourses.html',data=data,id=id)
    else:
        flash("No courses available")
        data=""
    return redirect('/registercourses/'+str(id))

@app.route('/registercourses/<string:id>',methods=['GET','POST'])

def registercourses(id):
    if request.method == "GET":
        return render_template('coursesreg.html',id=id)
    elif request.method == "POST":
        course=request.form['course_id']
        cur=mysql.connection.cursor()
        result = cur.execute('insert into tcourses values (%s,%s)',(id,course))
        mysql.connection.commit()
        cur.close()
        flash('You have successfully registered ', 'success')
        return redirect('/my_courses/'+str(id))


@app.route('/registerstudents',methods=['GET','POST'])
def registerstudents():
    form = RegisterStudentForm(CombinedMultiDict((request.files, request.form)))
    if (request.method == "GET"):
        return render_template('registerstudents.html', form=form)
    else:
        if (request.method=="POST" ):
            print("hello")
            student_id = form.student_id.data
            print(student_id)
            name = form.name.data
            email = form.email.data
            phoneNo = int(form.phoneNo.data)
            f = form.photo.data
            filename = secure_filename(f.filename)
            f.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], filename
            ))
            #Register student with the student table in db
            cur = mysql.connection.cursor()
            cur.execute('insert into student values(%s,%s,%s,%s)', (student_id, name, email, phoneNo))
            mysql.connection.commit()
            cur.close()
            return redirect('/')
        return redirect('/registerstudents')


@app.route('/regscourse/<string:t_id>/<string:course_id>',methods=['GET','POST'])
def coursereg(t_id,course_id):
    if request.method == "GET":
        return render_template('coursesregstudent.html',id1=course_id,id2=t_id)
    elif request.method == "POST":
        student=request.form['student_id']
        cur=mysql.connection.cursor()
        result = cur.execute('insert into scourses values (%s,%s)',(student,course_id))
        mysql.connection.commit()
        cur.close()
        flash('You have successfully registered ', 'success')
        return redirect('/my_courses/'+str(t_id))

@app.route('/attendance/<string:t_id>/<string:c_id>/')
def attendance(t_id,c_id):
    students=recognize.main()
    print(students)
    cur=mysql.connection.cursor()
    formatted_date = now.strftime('%Y-%m-%d')
    for id in students:
        cur.execute("insert into attendance values (%s,%s,%s,%s,%s)",(c_id,t_id,id,'p',formatted_date))
    mysql.connection.commit()
    cur.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
