from flask import Flask, jsonify, request
import jwt
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt
from functools import wraps
from mongoengine import connect
from model import User
import os
from dotenv import load_dotenv


load_dotenv()

SECRET = os.getenv('SECRET_KEY')
MONGO_CON = str(os.getenv('STRING_CONNECTION'))
MONGO_DB = str(os.getenv('MONGODB_DATABASE'))


print(SECRET,MONGO_CON,MONGO_DB)


app = Flask(__name__)
bcrypt = Bcrypt(app)

#CONEXION CON MONGO
connect(
    db=MONGO_DB,
    host = MONGO_CON,
    port=27017,
    authentication_source ='admin' 
)

#MODELO IMPORTADO
usuario = User()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
           
        
        if not token:
            return jsonify({'message' : 'Token is missing !!'}), 401
  
        try:
            print('decorador')
            data = jwt.decode(token, SECRET,algorithms=["HS256"])  
            __id =  data['id']     
            
            
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        
        return f(*args, **kwargs)
  
    return decorated


@app.route('/')
def func():
    return "Solo para no dejar vacio por aqui 🐵🐵🐒🐒", 200


@app.route('/users', methods=['GET', 'POST'])
@token_required
def user_data():
    data = {}
    code = 500
    message = ""
    status = "Fail"
    try:
        token = request.headers['x-access-token']
        data = jwt.decode(token, SECRET,algorithms=["HS256"]) 
        __id =  data['id']     
        current_user = User.objects(_id = __id).first()
        
        if data:
            message = "Access Successful"
            status = "successful"
            code = 200
            data = {
                'id' : __id,
                'name' : current_user.name,
                'age' : current_user.age,
                'token' : token
            }
        else:
            message = "User Data Failed"
            status = "Fail"
            code = 401
    except Exception as ee:
        message =  str(ee)
        status = "Error"

    return jsonify({"status": status, "message":message,'data': data}), code



@app.route('/signup', methods =['POST'])
def save_user():
    message = ""
    code = 500
    status = "Fail"
    res_data = {}
    try:
        # creates a dictionary of the form data
        data = request.form

        # gets date from FORM to ODM
        new_user = User()
        new_user.name = data.get('name')
        new_user.email = data.get('email')
        new_user.password = data.get('password')
        new_user.age = data.get('age')

        
        check = User.objects(email = new_user.email)
        if check.count() >= 1:
            
            message = "User with that email exists"
            code = 401
            status = "Fail"
            res_data['email'] = new_user.email

        else:
            new_user.password = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
            #Validando datos
            new_user.validate()
            new_user.save()
            status = "Successful"
            message = "User Created Successfully"
            code = 201

    except Exception as ex:
        message = f"{ex}"
        status = "Fail"
        code = 500

    return jsonify({'status': status, "message": message, 'data':res_data}), code



@app.route('/login', methods =['POST'])
def login():
    message = ""
    res_data = {}
    code = 500
    status = "Fail"
    
    try:
        auth = request.form
        
        if not auth or not auth.get('email') or not auth.get('password'):        
            message = 'Could not verify'
            code = 401
            status = 'Fail'
            res_data = {'WWW-Authenticate' : 'Basic realm ="Login required !!"'}
            return jsonify({'status': status, "data": res_data, "message":message}), code

        user = User.objects(email = auth.get('email')).first()
        
        if not user:
            message = 'Could not verify'
            code = 401
            status = 'Fail'
            res_data = {'WWW-Authenticate' : 'Basic realm ="User does not exist !!"'}
            return jsonify({'status': status, "data": res_data, "message":message}), code

        if bcrypt.check_password_hash(user.password, auth.get('password')):
            
            id = str(user._id)
            token = jwt.encode({'id': id,'exp' : datetime.utcnow() + timedelta(minutes = 30)}, SECRET,algorithm="HS256")
            message = 'Loggin Success'
            code = 201
            status = 'Success'
            return jsonify({'status': status, "data": {'token' : token}, "message":message}), code


    except Exception as ex:
        message = f"{ex}"
        code = 500
        status = "Fail"

    return jsonify({'status': status, "data": res_data, "message":message}), code


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='5000')