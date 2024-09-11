# #!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from sqlalchemy.orm import Session
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict(only=('id', 'name', 'address')) for restaurant in restaurants])

@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurant(id):
    with Session(db.engine) as session:
        restaurant = session.get(Restaurant, id)
        if restaurant is None:
            return jsonify({"error": "Restaurant not found"}), 404
        return jsonify(restaurant.to_dict(only=('id', 'name', 'address', 'restaurant_pizzas')))

@app.route('/restaurants/<int:id>', methods=['DELETE'])
def delete_restaurant(id):
    with Session(db.engine) as session:
        restaurant = session.get(Restaurant, id)
        if restaurant is None:
            return jsonify({"error": "Restaurant not found"}), 404

        # Delete associated RestaurantPizzas
        session.query(RestaurantPizza).filter_by(restaurant_id=id).delete()

        # Delete the restaurant
        session.delete(restaurant)
        session.commit()

    return '', 204


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    pizzas_list = [pizza.to_dict(only=('id', 'ingredients', 'name')) for pizza in pizzas]
    return jsonify(pizzas_list)

@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    
    # Validate input data
    if not all(key in data for key in ('price', 'pizza_id', 'restaurant_id')):
        return jsonify({"errors": ["validation errors"]}), 400
    
    # Validate price range
    if not (1 <= data['price'] <= 30):
        return jsonify({"errors": ["validation errors"]}), 400
    
    with Session(db.engine) as session:
        try:
            # Check if the Pizza and Restaurant exist
            pizza = session.get(Pizza, data['pizza_id'])
            restaurant = session.get(Restaurant, data['restaurant_id'])
            
            if not pizza or not restaurant:
                return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404
            
            # Create the RestaurantPizza
            restaurant_pizza = RestaurantPizza(price=data['price'], pizza_id=data['pizza_id'], restaurant_id=data['restaurant_id'])
            session.add(restaurant_pizza)
            session.commit()
            
            # Prepare the response data
            response_data = {
                "id": restaurant_pizza.id,
                "pizza": pizza.to_dict(only=('id', 'ingredients', 'name')),
                "pizza_id": restaurant_pizza.pizza_id,
                "price": restaurant_pizza.price,
                "restaurant": restaurant.to_dict(only=('id', 'name', 'address')),
                "restaurant_id": restaurant_pizza.restaurant_id
            }
            
            return jsonify(response_data), 201
        
        except Exception as e:
            session.rollback()
            return jsonify({"errors": [str(e)]}), 500

if __name__ == "__main__":
    app.run(port=5555, debug=True)