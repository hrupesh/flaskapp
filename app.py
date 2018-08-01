from flask import Flask ,  render_template ,request, redirect , flash , url_for , logging , session
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form , StringField , TextAreaField , PasswordField , validators
from passlib.hash import sha256_crypt
import mysql.connector as mariadb

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"

app.config['MySQL_HOST'] = 'localhost'
app.config['MySQL_USER'] = 'root'
app.config['MySQL_PASSWORD'] = 'toor'
app.config['MySQL_HOST'] = 'localhost'
app.config['MySQL_DB'] = 'articles'
app.config['MySQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

Articles = Articles()



@app.route('/')
def index():
		return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/articles')
def articles():
	return render_template('articles.html',articles = Articles)

@app.route('/articles/<string:id>/')
def article(id):
	return render_template('article.html',Id = id)


class registerform(Form):
	name = StringField('Name',[validators.data_required() , validators.Length(min=4,max=50,message="ReEnter Name Between 4 and 50 characters")])
	username = StringField('Username',[validators.data_required(),validators.Length(min=5,max=30,message="ReEnter username Between 4 and 30 characters")])
	email = StringField('Email',[validators.data_required(),validators.email(message="Enter a valid email"),validators.Length(min=4,max=50,message="ReEnter Email Between 4 and 50 characters")])
	password = PasswordField('Password',[
		validators.data_required(),
		validators.Length(min=6,max=15,message="ReEnter Password Between 6 and 15 characters"),
		validators.equal_to('confirm_password',message="Passwors do not match")
	])
	confirm_password = PasswordField('Confirm Password',[validators.data_required(),validators.Length(min=5,max=15,message="ReEnter Password Between 4 and 50 characters")])

@app.route('/register',methods=['GET','POST'])
def register():
	form =  registerform(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.hash(form.password.data)

		conn = mariadb.connect(user="root",password="",database="articles")

		cur = conn.cursor()

		cur.execute("INSERT INTO users(name,email,username,password) VALUES(%s,%s,%s,%s)",(name,email,username,password))

		conn.commit()
		flash("You have Successfully registered with Us","success")
		return redirect(url_for('index'))
	else:
		flash("Fill your details to register with Us ","warning")
		return render_template('register.html',form=form)

class loginform(Form):
	username = StringField('Username',[validators.data_required(),validators.Length(min=4,max=50,message="Please Enter a valid Username")])
	password = PasswordField('Password',[validators.data_required(),validators.Length(min=4,max=50,message="Enter a valid Password")])

@app.route('/login',methods=['GET','POST'])
def login():
	form = loginform(request.form)
	if request.method == 'POST' and form.validate():
		username = form.username.data
		pass_candidate = form.password.data 

		con = mariadb.connect(user="root",password="",database="articles")

		curs = con.cursor()

		res = curs.execute("SELECT * FROM users WHERE username = %s",[username])
		data = curs.fetchone()
		passw = data[4]
		app.logger.info(type(pass_candidate))
		app.logger.info(type(passw))
		app.logger.info(pass_candidate)
		app.logger.info(passw)
		app.logger.info(res)
		if sha256_crypt.verify(str(pass_candidate),str(passw)):
				app.logger.info(passw)
				app.logger.info("Password Matched")
		else:
			app.logger.info(data)
			app.logger.info(passw)
			app.logger.info("No User Found")
	return render_template('login.html',form=form)


if __name__ == '__main__':
	app.run(debug=True)
