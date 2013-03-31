import random
import string
import pymongo
import sendgrid
from bson.objectid import ObjectId, InvalidId
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask.ext.bcrypt import Bcrypt, generate_password_hash, \
	check_password_hash
from projekt import app
from projekt import events, users
from projekt import mailer
import flask_sijax


@app.route('/', methods=["GET","POST"])
def login():
	"""
	Function handler for /
	"""	

	if request.method == "POST":
		#if the person logs in
		email = request.form['email']
		password = request.form['password']
		#find the user which has the particular email
		user_found = users.find_one({'email' : email})
		
		if user_found:
			#first check if the user is confirmed
			if user_found['confirmed'] == "Yes":
				password_correct =  check_password_hash( user_found['password'],password)
				if password_correct:
					session['logged_in'] = True
					session['email'] = email
					session['name'] = user_found['name']				
					#redirect me to the control panel
					return redirect(url_for('panel'))
	#return the index template
	return render_template('index.html')

@app.route('/logout')
def logout():
	"""docstring for logout"""
	session.pop('logged_in', None)
	session.pop('name', None)
	session.pop('email', None)
	return redirect(url_for('login'))


@app.route('/register', methods=["GET", "POST"])
def register():
	"""
	Registeration new page
	"""
	if request.method == "POST":
		email = request.form['email']
		phone = request.form['phone']
		name = request.form['name']
		sex = request.form['sex']
		college = request.form['college']
		admin_level = 5
		events = []
		digits = "".join( [random.choice(string.digits) for i in xrange(8)] )
		chars = "".join( [random.choice(string.letters) for i in xrange(15)] )
		password = chars+digits		
		
		garbage_chars = "".join( [random.choice(string.letters) for i in xrange(30)] )
		garbage_digits = "".join( [random.choice(string.digits) for i in xrange(30)] )
		
		garbage = garbage_chars+garbage_digits
		
		email_value = email.encode('hex')
		new_user = { 'email': email,
		'phone': phone,
		'name' : name,
		'sex': sex,
		'college' : college,
		'virgin': 'Yes',
		'confirmed': 'No',
		'level' : admin_level,
		'event_list': events,
		'password': generate_password_hash(password)}
		user_exists = users.find_one({'email': email})
		if not user_exists:
			done_registering = users.insert(new_user)
			if done_registering:
				#send and email to the guy
				confirmation_link = "http://shrouded-sierra-1986.herokuapp.com/confirm/"+email_value+"/rdv12confirmation/"+garbage
				main_body = "Hey "+name+"!<br /><br />Your email id was used to register for Rendezvous 2012 going to be held at IIT Delhi. If it wasn't you, then please ignore this email. But if it was you, click on the link below to confirm. <br /><br /><a href="+confirmation_link+">Click here to confirm</a><br /><br /><br />Once you're done, you can use this password to login: <b>"+password+"</b>"
				message = sendgrid.Message("no-reply@rdv12.com", \
			    "Rendezvous 2012! IIT Delhi. Your registeration is just one step from completion",\
			"plain body", main_body)
				message.add_to(email,name)
				mail_sent = mailer.web.send(message)
				if mail_sent:
					return redirect(url_for('login'))
		
	return render_template('register.html')

@app.route('/panel', methods=["GET", "POST"])
def panel():
	"""
	Panel is place where the person feels safe.
	Best place to scare the logged in user
	"""
	try:
		current_user = users.find_one({'email': session['email']})
	except:
		return redirect(url_for('login'))
	
	if request.method == "POST":
		password = request.form['password']
		confirm = request.form['confirmpassword']
		if password == confirm:
			current_user['password'] = generate_password_hash(password)
			current_user['virgin'] = "No"
			users.save(current_user)
	return render_template('panel.html', user=current_user)
	
@app.route('/about')
def about():
	"""docstring for about"""
	return render_template('about.html')

@app.route('/contact')
def contact():
	"""docstring for contact"""
	return render_template('contact.html')
	
@app.route('/panel/events')
def events():
	"""docstring for events"""
	return render_template('events.html')

@app.route('/confirm/<email_value>/rdv12confirmation/<random_garbage_hash>')
def activation(email_value, random_garbage_hash):
	"""
	The hash value is given to the user using the email
	activates the user and allows access to the panel
	"""
	email = email_value.decode('hex')
	user_exists = users.find_one({'email':email})
	if user_exists:		
		#go the login page but first confirm the user
		user_exists['confirmed'] = "Yes"
		users.save(user_exists)
		#now redirect to the login page
		return redirect(url_for('login'))
	else:
		return redirect('/404')

def qrcode_generation():
	"""docstring for qrcode_generation"""
	pass

def page_not_found(e):
    return render_template('404.html'), 404