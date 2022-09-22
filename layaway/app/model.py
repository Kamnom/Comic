from mongoengine import Document, StringField, IntField, EmailField,ObjectIdField,DateTimeField

class User(Document):
    _id = ObjectIdField()
    email = EmailField(required=True ,unique=True)
    password = StringField(required=True)
    name = StringField(required=True)
    age = IntField(requirest=True)
    meta={'collection':'User'}
    
class User_Layaway(Document):
    _id = ObjectIdField()
    id_comic = StringField(required=True)
    id_user = StringField(required=True)
    register_date = DateTimeField(required=True)
    meta={'collection':'User-Layaway'}