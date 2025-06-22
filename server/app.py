#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
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

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        response = [
            {

                "id": r.id,
                "name": r.name,
                "address": r.address
            } for r in restaurants
        ]
        return response, 200

api.add_resource(Restaurants, "/restaurants")

class RestaurantByID(Resource):
    def get(self, id):
        r = db.session.get(Restaurant, id)
        if not r:
            return {"error": "Restaurant not found"}, 404

        return {
            "id": r.id,
            "name": r.name,
            "address": r.address,
            "restaurant_pizzas": [
                {
                    "id": rp.id,
                    "price": rp.price,
                    "pizza": {
                        "id": rp.pizza.id,
                        "name": rp.pizza.name,
                        "ingredients": rp.pizza.ingredients
                    }
                } for rp in r.restaurant_pizzas
            ]
        }, 200

    def delete(self, id):
        r = db.session.get(Restaurant, id)
        if not r:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(r)
        db.session.commit()
        return {}, 204

api.add_resource(RestaurantByID, "/restaurants/<int:id>")

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        response = [
            {
                "id": p.id,
                "name": p.name,
                "ingredients": p.ingredients
            } for p in pizzas
        ]
        return response, 200

api.add_resource(Pizzas, "/pizzas")


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_rp = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_rp)
            db.session.commit()

            return {
                "id": new_rp.id,
                "price": new_rp.price,
                "pizza_id": new_rp.pizza_id,
                "restaurant_id": new_rp.restaurant_id,
                "pizza": {
                    "id": new_rp.pizza.id,
                    "name": new_rp.pizza.name,
                    "ingredients": new_rp.pizza.ingredients
                },
                "restaurant": {
                    "id": new_rp.restaurant.id,
                    "name": new_rp.restaurant.name,
                    "address": new_rp.restaurant.address
                }
            }, 201

        except Exception:
            return {"errors": ["validation errors"]}, 400


api.add_resource(RestaurantPizzas, "/restaurant_pizzas")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
