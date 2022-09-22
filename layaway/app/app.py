from flask import Flask, jsonify, request
import jwt
from datetime import datetime
from flask_bcrypt import Bcrypt
from functools import wraps
from mongoengine import connect
from model import User,User_Layaway
import os, hashlib,json
import requests
from dotenv import load_dotenv


load_dotenv()

SECRET = os.getenv('SECRET_KEY')
MONGO_CON = str(os.getenv('STRING_CONNECTION'))
MONGO_DB = str(os.getenv('MONGODB_DATABASE'))
PRIV_KEY = os.getenv('MARVEL_PRIV')
PUB_KEY = os.getenv('MARVEL_PUB')




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
            
            data = jwt.decode(token, SECRET,algorithms=["HS256"])  
            __id =  data['id'] 
            current_user = User.objects(_id = __id).first()
            
        except:
            return jsonify({
                'message' : 'Token is invalid !!'
            }), 401
        return f(*args, **kwargs)
    return decorated


def comics_validation(lst_comics):
    
    res_comics = list()
    try:
        ts = '1'
        hasmd5 = hashlib.md5((ts+PRIV_KEY+PUB_KEY).encode())
        RURL = 'https://gateway.marvel.com:443/v1/public/comics/'
        PARAM = {
            'ts':ts ,
            'hash':hasmd5.hexdigest(),
            'apikey': PUB_KEY
            }
        
        for id in lst_comics:
            r = requests.get(url=RURL+str(id) , params=PARAM)
            response = r.text
            d_comic = json.loads(response)
            
            if d_comic['status'] == 'Ok' and d_comic['code'] == 200:
                res_comics.append({'id': id, 'valid':True})
                
            else:
                res_comics.append({'id': id, 'valid':False , 'status': d_comic['status']})
                
            
    except Exception as ex:
        message = f"{ex}"
        status = "Fail"
        code = 500
        
    return res_comics


@app.route('/addtolayaway/', methods =['POST'])
@token_required
def save_comics():
    message = ""
    code = 500
    status = "Fail"
    comics_validados = None
    
    try:
        # creates a dictionary of the form data
        data = request.form
        
        #Lista de los ID de comics
        comics = json.loads(data['comics'])
        comics_validados = comics_validation(comics)        
        code=200
        status='Ok'


        token = request.headers['x-access-token']
        token_payload = jwt.decode(token, SECRET,algorithms=["HS256"]) 
        __id =  token_payload['id']
        #print('llego aqui!!',__id, token, token_payload)     
        current_user = User.objects(_id = __id).first()

        #User_layaway
        cont = 0
        for order in comics_validados:
            
            if order['valid']:
                new_order = User_Layaway()
                new_order.id_comic = str(order['id'])    
                new_order.id_user = __id
                new_order.register_date = datetime.now()
                new_order.save()
                cont = cont + 1
                

    except Exception as ex:
        message = f"{ex}"
        status = "Fail"
        code = 500

    return jsonify({'status': status, "message": message ,'data':comics_validados}), code


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='7000')