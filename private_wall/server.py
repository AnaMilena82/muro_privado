from app_private_wall import app
from app_private_wall.controllers import controller_users, controller_wall





if __name__=="__main__":   # Asegúrate de que este archivo se esté ejecutando directamente y no desde un módulo diferente    
    app.run(debug=True)    # Ejecuta la aplicación en modo de depuración

