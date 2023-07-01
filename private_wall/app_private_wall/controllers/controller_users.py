from flask import Flask, render_template, request, redirect, session, url_for, flash
from app_private_wall import app
from app_private_wall.models.model_users import User
from app_private_wall.models.model_wall import Message 
from app_private_wall.controllers import controller_wall

@app.route('/', methods = ['GET'])    
@app.route('/register', methods = ['GET'])    
@app.route('/login', methods = ['GET'])    
def index():
    return render_template("index.html")



@app.route('/register', methods = ['POST'])    
def post_register():
    language = request.form.getlist('language')
    country_nac = request.form.get("country_nac")
    if not language:  # Si no se selecciona ningún idioma, establecer language como una lista vacía
        language = []
    data_register = {
        "first_name": request.form["first_name"],
        "last_name": request.form["last_name"],
        "email": request.form["email"],
        "password": request.form["password"],
        "confirmpassword": request.form["confirmpassword"],
        "fech_nac": request.form["fech_nac"],
        "country_nac": country_nac,
        "language" : language
        
    }

    if not User.validate_register(data_register):
        return redirect('/')
    
    user = User.new_user(data_register)
    session['user_id'] = user.id
    return redirect(url_for('wall'))

@app.route('/login', methods = ['POST'])    
def post_login():
   
    data_login = {
        "email": request.form["email"],
        "password": request.form["password"],
    }
    try:
        if not User.validate_login(data_login):
            return redirect('/')
        
        user = User.get_user_by_email(data_login["email"])
        
        if user:
            user_id = user.id
            session['user_id'] = user_id
            return redirect(url_for('wall'))
    except KeyError:
        
        return redirect('/')

@app.route('/wall')
def wall():
    user_id = session.get('user_id')
    user = User.get_user_by_id(user_id)
    if user_id:
        messages = Message.get_user_messages(user_id)
        users = User.get_all_user()
        return render_template('wall.html', user=user, users=users, messages=messages, session_user_id=user_id)
    return redirect('/')
          

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')     