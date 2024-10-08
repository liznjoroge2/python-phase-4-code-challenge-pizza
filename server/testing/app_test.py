import pytest
from app import app, db
from models import Restaurant, Pizza, RestaurantPizza
from faker import Faker

class TestRestaurantPizza:
    """Class RestaurantPizza in models.py"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup and teardown for each test"""
        with app.app_context():
            db.create_all()
            yield
            db.drop_all()

    def test_price_between_1_and_30(self):
        """Requires price between 1 and 30."""
        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients="Dough, Sauce, Cheese")
            restaurant = Restaurant(name=fake.name(), address='Main St')
            db.session.add(pizza)
            db.session.add(restaurant)
            db.session.commit()

            # Valid prices
            restaurant_pizza_1 = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=1)
            restaurant_pizza_2 = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=30)
            db.session.add_all([restaurant_pizza_1, restaurant_pizza_2])
            db.session.commit()

            # Check if they were added correctly
            assert RestaurantPizza.query.count() == 2

    def test_price_too_low(self):
        """Requires price between 1 and 30 and fails when price is 0."""
        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients="Dough, Sauce, Cheese")
            restaurant = Restaurant(name=fake.name(), address='Main St')
            db.session.add(pizza)
            db.session.add(restaurant)
            db.session.commit()

            with pytest.raises(ValueError):
                restaurant_pizza = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=0)
                db.session.add(restaurant_pizza)
                db.session.commit()

    def test_price_too_high(self):
        """Requires price between 1 and 30 and fails when price is 31."""
        with app.app_context():
            fake = Faker()
            pizza = Pizza(name=fake.name(), ingredients="Dough, Sauce, Cheese")
            restaurant = Restaurant(name=fake.name(), address='Main St')
            db.session.add(pizza)
            db.session.add(restaurant)
            db.session.commit()

            with pytest.raises(ValueError):
                restaurant_pizza = RestaurantPizza(restaurant_id=restaurant.id, pizza_id=pizza.id, price=31)
                db.session.add(restaurant_pizza)
                db.session.commit()
