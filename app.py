from flask import Flask ,  render_template ,request, redirect , flash , url_for , logging , session
from data import Articles
from wtforms import Form , StringField , TextAreaField , PasswordField , validators
from passlib.hash import sha256_crypt
import mysql.connector as mariadb
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret"

app.config['MySQL_HOST'] = 'localhost'
app.config['MySQL_USER'] = 'root'
app.config['MySQL_PASSWORD'] = 'root'
app.config['MySQL_HOST'] = 'localhost'
app.config['MySQL_DB'] = 'articles'
app.config['MySQL_CURSORCLASS'] = 'DictCursor'


Articles = Articles()

def if_login(f):
	@wraps(f)
	def wrap(*args,**kwargs):
		if session['login'] and session['username']:
			return f(*args,**kwargs)
		else:
			flash("Unautharized section , please login ","danger")
			return redirect(url_for('login'))
	return wrap

@app.route('/')
def index():
		return render_template('index.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/articles')
@if_login
def articles():
	return render_template('articles.html',articles = Articles)

@app.route('/articles/<string:id>/')
@if_login
def article(id):
	connn = mariadb.connect(user="root",password="root",database="articles")
	cur = connn.cursor()
	cur.execute("select * from article where id=%s",[id])
	article = cur.fetchone()
	app.logger.info(article)
	return render_template('article.html',article=article)

@app.route('/e/<string:id>',methods=['GET','POST'])
@if_login
def edit(id):
	conn = mariadb.connect(user="root",password="root",database="articles")
	cur = conn.cursor()
	cur.execute("select * from article where id=%s",[id])
	article = cur.fetchone()
	form = articleform(request.form)
	form.title.data = article[1]
	form.body.data = article[3]
	app.logger.info(article)
	cur.close()
	conn.close()
	if request.method == 'POST' and form.validate():
		if not session['username'] == article[2]:
			flash("Access Denied , Only the owner of article can Edit the Article.","danger")
			return redirect(url_for('dash'))
		title = request.form['title']
		body = request.form['body']
		app.logger.info(title)
		app.logger.info(body)
		c = mariadb.connect(user='root',password='root',database='articles')
		cur = c.cursor()
		cur.execute("update article set title=%s , body=%s where id=%s",(title,body,id))
		c.commit()
		cur.close()
		c.close()
		flash("Article Updated","success")
		return redirect(url_for('dash'))
	return render_template('edit_article.html',form=form)


@app.route('/d/<string:id>',methods=['GET','POST'])
@if_login
def delete(id):
	conn = mariadb.connect(user="root",password="root",database="articles")
	cur = conn.cursor()
	cur.execute("select * from article where id=%s",[id])
	article = cur.fetchone()
	if not session['username'] == article[2]:
		flash("Access Dinied , you do not have requested Privelages.","danger")
		return redirect(url_for('dash'))
	app.logger.info(article)
	cur.execute("delete from article where id=%s",[id])
	conn.commit()
	flash("Article Deleted","danger")
	cur.close()
	conn.close()
	return redirect(url_for('dash'))


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
		password = form.password.data

		conn = mariadb.connect(user="root",password="root",database="articles")

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

		con = mariadb.connect(user="root",password="root",database="articles")

		curs = con.cursor()

		curs.execute("SELECT * FROM users WHERE username = %s",[username])
		data = curs.fetchone()
		passw = data[4]
		if pass_candidate == passw:
				session['login'] = True
				session['username'] = username
				flash("You have successfully Logged in","success")
				return redirect(url_for('dash'))
		else:
			app.logger.info("No User Found")
			flash("Incorrect Password","danger")
	return render_template('login.html',form=form)



@app.route('/dash')
@if_login
def dash():
	conn = mariadb.connect(user='root',password='root',database='articles')
	cur = conn.cursor()
	cur.execute("select * from article;")
	art = cur.fetchall()
	return render_template('dash.html',articles=art)

class articleform(Form):
	title = StringField('Title',[validators.data_required(),validators.Length(min=4,max=50,message="Please Enter a valid Title of the article")])
	body = TextAreaField('Body',[validators.data_required(),validators.Length(min=10,max=500,message="Enter Valid Body")])

@app.route('/add_article',methods=['GET','POST'])
@if_login
def add_article():
	form = articleform(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data

		connection = mariadb.connect(user='root',password='root',database='articles')

		cur = connection.cursor()

		cur.execute("INSERT INTO article(title,body,author) VALUES( %s,%s,%s );",(title,body,session['username']))

		connection.commit()

		connection.close()
		flash("Article Added","success")
		return redirect(url_for('dash'))
	return render_template('add_article.html',form=form)


@app.route('/logout')
@if_login
def logout():
	session.clear()
	session['login'] = False
	flash("You have been Logged Out ","warning")
	return redirect(url_for('login'))


if __name__ == '__main__':
	app.run(debug=True,port=80,host='0.0.0.0')
