import os, hashlib, time,json
import requests
from dotenv import load_dotenv
from flask import Flask,request
from flasgger import Swagger, swag_from
from dotenv import load_dotenv


load_dotenv()
########################################

app = Flask(__name__)
swag = Swagger(app)
########################################
PRIV_KEY = os.getenv('MARVEL_PRIV')
PUB_KEY = os.getenv('MARVEL_PUB')



@app.route('/searchComics/',defaults = {'searchV':None})
@app.route('/searchComics/<string:searchV>', methods=['GET'])
def search_p(searchV):

    filter = request.args.get('filter', default = '*', type = str)
    
    result = {}
    if filter == '*':
        result['characters'] = characterSearch(searchV)
        result['comics'] = comicSearch(searchV)
        
    elif filter == 'comic' : 
        result['comics'] = comicSearch(searchV)
    elif filter == 'character':
        result['characters'] = characterSearch(searchV)
    
    return json.dumps(result)




#########################################

def comicSearch(comicV):
    lst_result = list()
    ts = '1'
    hasmd5 = hashlib.md5((ts+PRIV_KEY+PUB_KEY).encode())
    RURL = 'https://gateway.marvel.com:443/v1/public/comics'
    PARAM = {
            'ts':ts ,
            'hash':hasmd5.hexdigest(),
            'apikey': PUB_KEY,
            'format': 'comic',
            'limit' : 100
            }
    if comicV :
        PARAM['title'] = comicV.capitalize()

    r = requests.get(url=RURL , params=PARAM)
    response = r.text
    d_comics = json.loads(response)
    
    for i in d_comics['data']['results']:
        lst_result.append(
            {
                'id': i['id'],
                'title': i['title'],
                'image':i['thumbnail']['path'],
                'onSaleDate': i['dates'][0]['date']
            }
        )
    
    return lst_result

def characterSearch(characterV):
    lst_result = list()
    ts = '1'
    hasmd5 = hashlib.md5((ts+PRIV_KEY+PUB_KEY).encode())
    RURL = 'https://gateway.marvel.com:443/v1/public/characters'
    PARAM = {
            'ts':ts ,
            'hash':hasmd5.hexdigest(),
            'apikey': PUB_KEY,
            'limit' : 100
            }
    if characterV :
        PARAM['name'] = characterV.capitalize()
    
    r = requests.get(url=RURL , params=PARAM)
    response = r.text
    d_character = json.loads(response)
    

    for i in d_character['data']['results']:
        lst_result.append(
            {
                'id': i['id'],
                'name': i['name'],
                'image':i['thumbnail']['path'],
                'apparences': i['comics']['available']
            }
        ) 
    
    return lst_result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='6000',debug=True)