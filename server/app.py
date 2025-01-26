#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
from flask_cors import CORS 
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

CORS(app)

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])


# GET /restaurants/:id
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant_by_id(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404
    return jsonify(restaurant.to_dict())


# DELETE /restaurants/:id
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if restaurant is None:
        return jsonify({"error": "Restaurant not found"}), 404

    # Delete associated RestaurantPizza records
    RestaurantPizza.query.filter_by(restaurant_id=id).delete()

    db.session.delete(restaurant)
    db.session.commit()
    return '', 204


# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict() for pizza in pizzas])


# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not (price and pizza_id and restaurant_id):
        return jsonify({"errors": ["Missing data for price, pizza_id, or restaurant_id"]}), 400

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)

    if not pizza or not restaurant:
        return jsonify({"errors": ["Invalid pizza or restaurant ID"]}), 404

    # Create the new RestaurantPizza
    restaurant_pizza = RestaurantPizza(price=price, pizza_id=pizza_id, restaurant_id=restaurant_id)

    # Validate the price (assuming you have validation set up in your model)
    try:
        db.session.add(restaurant_pizza)
        db.session.commit()
    except ValueError as e:
        return jsonify({"errors": [str(e)]}), 400

    # Return the created restaurant-pizza object
    return jsonify(restaurant_pizza.to_dict()), 201


if __name__ == "__main__":
    app.run(port=5555, debug=True)
