from flask import Flask, render_template, redirect, request, url_for, session
from flask_mysqldb import MySQL, MySQLdb
import datetime
import bcrypt
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'users'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/')
def home():
	if session:
		c = mysql.connection.cursor()
		c.execute("SELECT * FROM posts WHERE id=%s",(session['id'],))
		posts = c.fetchall()
		return render_template('home.html', posts=posts)
	else:
		return render_template('home.html')

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template('auth/register.html')
	else:
		name = request.form['name']
		email = request.form['email']
		password = request.form['password'].encode('utf-8')
		hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

		c = mysql.connection.cursor()
		c.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",(name, email, hash_password,))
		mysql.connection.commit()
		session['name'] = name
		session['email'] = email

	return redirect(url_for('home'))

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password'].encode('utf-8')

		c = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		c.execute("SELECT * FROM users WHERE email=%s",(email,))
		user = c.fetchone()
		c.close()

		if user:
			if bcrypt.hashpw(password, user['password'].encode('utf-8')) == user['password'].encode('utf-8'):
				session['name'] = user['name']
				session['email'] = user['email']
				session['id'] = user['id']
				return redirect(url_for('home'))
		else:
			return render_template('/auth/login.html')
	else:
		return render_template('/auth/login.html')

@app.route('/share', methods=['GET', 'POST'])
def submit():
	if request.method == 'GET':
		return render_template('/home.html')
	else:
		if session:
			message = request.form['message']
			date = datetime.datetime.now()
			time = '{}-{}-{}, {}:{}:{}'.format(date.day, date.month, date.year, date.hour, date.minute, date.second)
			c = mysql.connection.cursor()
			c.execute("INSERT INTO posts (id, message, timestamp) VALUES (%s, %s, %s)",(session['id'], message, time,))
			mysql.connection.commit()
			c.close()
		return redirect(url_for('home'))

@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('home'))


if __name__ == '__main__':
	app.secret_key = os.urandom(12)
	app.run(debug=True)