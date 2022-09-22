from mongoengine import Document, StringField, IntField, EmailField,ObjectIdField

class User(Document):
    _id = ObjectIdField()
    email = EmailField(required=True ,unique=True)
    password = StringField(required=True)
    name = StringField(required=True)
    age = IntField(requirest=True)
    meta={'collection':'User'}
    
