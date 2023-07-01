
from app_private_wall.config.mysqlconnection import connectToMySQL
from flask import Flask, render_template, request, redirect, session, url_for, flash
import re
from datetime import date, datetime
from app_private_wall import app,BASE_DE_DATOS
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

class User:
    def __init__( self , data ):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.fech_nac = data['fech_nac']
        self.country_nac = data['country_nac']
        self.language = self.load_languages()
  
    @classmethod
    def get_all_user(cls):
        query = "SELECT * FROM users ORDER BY first_name ASC;"
        users = []
        results = connectToMySQL(BASE_DE_DATOS).query_db(query)
        
        for user in results:
            users.append( cls(user) )
        return users

    def load_languages(self):
        query = "SELECT language FROM user_languages WHERE user_id = %(user_id)s;"
        data = {
            'user_id': self.id
        }
        result = connectToMySQL(BASE_DE_DATOS).query_db(query, data)
        languages = []
        if isinstance(result, list):
            languages = [row['language'] for row in result]
        return languages

    @classmethod
    def new_user(cls, data_register ):
        
        pw_hash = bcrypt.generate_password_hash(data_register["password"])
        data_register['password'] = pw_hash
       
        query_user = "INSERT INTO users (first_name, last_name, email, password, fech_nac, country_nac) VALUES (%(first_name)s, %(last_name)s, %(email)s, %(password)s, %(fech_nac)s, %(country_nac)s);"
  
        user_id = connectToMySQL(BASE_DE_DATOS).query_db(query_user, data_register)

        if user_id:
           
            query_languages = "INSERT INTO user_languages (user_id, language) VALUES (%(user_id)s, %(language)s);"
            for language in data_register['language']:
                language_data = {
                    'user_id': user_id,
                    'language': language
                }
                connectToMySQL(BASE_DE_DATOS).query_db(query_languages, language_data)
        else:
            print("No se insertó ningún registro en la tabla 'users'")
        user_data = {
            'id': user_id,
            'first_name': data_register['first_name'],
            'last_name': data_register['last_name'],
            'email': data_register['email'],
            'password': data_register['password'],
            'fech_nac': data_register['fech_nac'],
            'country_nac': data_register['country_nac']
        }

        user = cls(user_data)
        user.language = data_register['language']  # Agrega el atributo language al objeto user

        return user
            
        
    @staticmethod
    def validate_register(data_register):
        email = data_register["email"]
        password = data_register['password']
        confirmpassword = data_register['confirmpassword']
        radio = data_register['country_nac']
        is_valid = True 
        fech_nac = None

        fech_nac_str = data_register['fech_nac']
        
        try:
            fech_nac = datetime.strptime(fech_nac_str, '%Y-%m-%d').date()
        except ValueError:
            flash("The date of birth is invalid.", "error_register")
            is_valid = False
        today = date.today()
        
        

        existing_email = User.get_user_by_email(data_register['email'])
        if existing_email:
            flash("Email already exists.", "error_register")
            return False
        
       

        if not EMAIL_REGEX.match(email):
            flash("Invalid email address!", "error_register")
            is_valid = False
        if not data_register['first_name'].isalpha():
            flash("First Name must contain only letters.", "error_register")
            is_valid = False
        if len(data_register['first_name']) < 2:
            flash("First Name must be at least 2 characters.", "error_register")
            is_valid = False
        if not data_register['last_name'].isalpha():
            flash("Last Name must contain only letters.", "error_register")
            is_valid = False
        if len(data_register['last_name']) < 2:
            flash("Last Name must be at least 2 characters.", "error_register")
            is_valid = False

        if len(data_register['password']) < 8:
            flash("Password must be at least 8 characters.", "error_register")
            is_valid = False
        if password != confirmpassword:
            flash("Passwords do not match.", "error_register")
            is_valid = False
        if not re.search(r"\d", password):
            flash("Password must contain at least one digit.", "error_register")
            is_valid = False
        if not re.search(r"[A-Z]", password):
            flash("Password must contain at least one uppercase letter.", "error_register")
            is_valid = False
        
        if fech_nac is not None:
            age = today.year - fech_nac.year - ((today.month, today.day) < (fech_nac.month, fech_nac.day))
            if age < 18:
                flash("You must be of legal age to register.", "error_register")
                is_valid = False
        else:
            flash("The date of birth is invalid.", "error_register")
            is_valid = False
        
        if radio is None:
            flash("You must select an option in country of birth.", "error_register")
            is_valid = False
        return is_valid
        
   

    @staticmethod
    def get_user_by_id(user_id):
        
        query = "SELECT * FROM users WHERE id = %(user_id)s"
        result = connectToMySQL(BASE_DE_DATOS).query_db(query, {"user_id": user_id})
        if result:
            return User(result[0])  
        else:
            return None

    @staticmethod
    def validate_login(data_login):
        email = data_login["email"]
        password = data_login['password']
        
        is_valid = True

        user = User.get_user_by_email(email)
        if not user:
            flash("Invalid Email/Password.", "error_login")
            is_valid = False
        else:
            if user.password is None or not bcrypt.check_password_hash(user.password, password):
                flash("Invalid Password", "error_login")
                is_valid = False

        if not EMAIL_REGEX.match(email):
            flash("Invalid email address!", "error_login")
            is_valid = False

        if len(data_login['password']) < 8:
            flash("Password must be at least 8 characters.", "error_login")
            is_valid = False
        return is_valid
     
    @staticmethod
    def get_user_by_email(email):
        print("ESTE ES EL ID QUE LLEGA:", email)
        query = "SELECT * FROM users WHERE email = %(email)s"
        result = connectToMySQL(BASE_DE_DATOS).query_db(query, {"email": email})
        
        if result:
            user_data = result[0]  # Obtener los datos del usuario
            user = User(user_data)  # Crear objeto User con los datos
            print("SENTENCIA DEL MAIL:", user)
            return user
        else:
            return None

    @staticmethod
    def get_message_count(user_id):
        query = "SELECT COUNT(*) AS count FROM messages WHERE sender_id = %(user_id)s"
        result = connectToMySQL(BASE_DE_DATOS).query_db(query, {"user_id": user_id})
        if result:
            return result[0]['count']
        return 0


