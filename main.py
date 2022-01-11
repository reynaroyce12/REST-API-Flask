from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

API_KEY = '***SecretApiKey***'

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/random')
def show_random():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    return jsonify(cafe={
        "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,
        "seats": random_cafe.seats,
        "has_toilet": random_cafe.has_toilet,
        "has_wifi": random_cafe.has_wifi,
        "has_sockets": random_cafe.has_sockets,
        "can_take_calls": random_cafe.can_take_calls,
        "coffee_price": random_cafe.coffee_price,
    })


@app.route('/all')
def show_all():
    cafes = db.session.query(Cafe).all()
    cafe_list = []
    for cafe in cafes:
        cafe_dict = {"id": cafe.id, "name": cafe.name, "map_url": cafe.map_url,
                     "img_url": cafe.img_url,
                     "location": cafe.location, "has_sockets": cafe.has_sockets,
                     "has_toilet": cafe.has_toilet, "has_wifi": cafe.has_wifi,
                     "can_take_calls": cafe.can_take_calls, "seats": cafe.seats,
                     "coffee_price": cafe.coffee_price}
        cafe_list.append(cafe_dict)
    all_cafes = {"cafes": cafe_list}
    all_cafes_json = jsonify(cafes=all_cafes["cafes"])
    return all_cafes_json


@app.route('/search')
def search():
    location = request.args.get('loc')
    cafe = db.session.query(Cafe).filter_by(location=location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route('/add', methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfully added the new cafe."})


@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the new price."}), 200
    else:

        return jsonify(error={"Not Found": "Sorry a cafe with that id does not exist."}), 404


@app.route("/closed/<int:cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    secret_key = request.args.get('api_key')
    if secret_key == API_KEY:
        cafe = db.session.query(Cafe).get(cafe_id)
        if cafe:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted cafe"}), 200
        else:
            return jsonify(response={"Failed": "Failed to delete the record. Cafe does not exist."}), 404
    else:
        return jsonify(response={"Forbidden": "Not allowed. Make sure to have the right API Key"}), 403


if __name__ == '__main__':
    app.run(debug=True)
