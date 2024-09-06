from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    address = db.Column(db.String, nullable=False)
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='restaurant', cascade="all, delete-orphan")

    def to_dict(self, only=None, include=None):
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        if include:
            for item in include:
                data[item] = [x.to_dict() for x in getattr(self, item)]
        if only:
            data = {k: data[k] for k in only}
        return data

class Pizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    ingredients = db.Column(db.String, nullable=False)
    restaurant_pizzas = db.relationship('RestaurantPizza', backref='pizza', cascade="all, delete-orphan")

    def to_dict(self, only=None):
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        if only:
            data = {k: data[k] for k in only}
        return data

class RestaurantPizza(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer, nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    pizza_id = db.Column(db.Integer, db.ForeignKey('pizza.id'), nullable=False)

    @validates('price')
    def validate_price(self, key, value):
        if value < 1 or value > 30:
            raise ValueError("Price must be between 1 and 30")
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'price': self.price,
            'pizza': self.pizza.to_dict(),
            'pizza_id': self.pizza_id,
            'restaurant': self.restaurant.to_dict(),
            'restaurant_id': self.restaurant_id
        }
