from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable = False, unique=True)
    _password_hash = db.Column(db.String)
    image_url = db.Column(db.String,nullable=True)
    bio = db.Column(db.String, nullable=True)

    recipes = db.relationship('Recipe', backref = 'user')

    @hybrid_property
    def password_hash(self):
        raise AttributeError()
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))



    def __repr__(self):
        return f'{self.username},\n {self.bio}, \n{self.image_url}, \n{self._password_hash}'

class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'  
    __table_arg__ = (
        db.CheckConstraint('len(instructions) >= 50'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
  
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, 
                             db.CheckConstraint('len(instructions) >= 50'),
                             nullable=False)
    minutes_to_complete = db.Column(db.Integer,nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @validates('instructions')
    def validates_instructions(self, key, recipes):
        if len(recipes) >= 50:
            return recipes