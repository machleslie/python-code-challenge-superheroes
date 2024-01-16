#!/usr/bin/env python3

from flask import Flask, jsonify,request,make_response
from flask_migrate import Migrate
from models import Hero,Power,HeroPower
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

# Create tables based on the models
# with app.app_context():
#     db.create_all()

@app.route('/')
def home():
    return 'test'

@app.route("/heroes")
def heros():
    # Query all heroes from the database
    all_heros = Hero.query.all()

    # Convert the hero instances to a list of dictionaries
    heros_list = [{"id": hero.id, "name": hero.name, "super_name": hero.super_name} for hero in all_heros]

    # Return the list of heroes as JSON
    return heros_list


@app.route('/heroes/<int:id>')
def get_id(id):
    """Get a specific hero by their ID"""
    hero = Hero.query.filter(Hero.id == id).first()

    if hero:
        # Get powers for the hero
        powers = get_powers(id)

        # Return a JSON response
        res = {
            "ID": hero.id,
            "Name": hero.name,
            "Super Name": hero.super_name,
            "powers":[ powers]  # Use powers directly without jsonify
        }

        return jsonify(res)

    else:
        return {"error": "Hero not found"}


@app.route('/powers/<int:id>', methods=["GET", "POST", "PATCH"])
def get_powers(id):
    if request.method == "GET":
        # Retrieve power data based on the given ID
        power = Power.query.filter(Power.id == id).first()

        if power:
            # Return power details as a dictionary
            return {
                "id": power.id,
                "name": power.name,
                "description": power.description
            }

        else:
            # Return an error message if power not found
            return {"error": "Power not found"}

    elif request.method == "POST":
        # Assuming you want to update the power with new data
        new_data = request.json

        # Get the existing power from the database
        existing_power = Power.query.filter(Power.id == id).first()

        if existing_power:
            # Update the existing power with new data
            existing_power.name = new_data.get('name', existing_power.name)
            existing_power.description = new_data.get('description', existing_power.description)

            # Commit the changes to the database
            db.session.commit()

            return jsonify({
                "message": "Power updated successfully",
                "id": existing_power.id,
                "name": existing_power.name,
                "description": existing_power.description
            }), 200
        else:
            # Return an error message if power not found
            return jsonify({"error": "Power not found"}), 404

    elif request.method == "PATCH":
        # Handle the PATCH method (add your logic here)
        return jsonify({"message": "PATCH request handled"}), 200

    else:
        # Default response for unsupported HTTP methods
        return jsonify({"error": "Unsupported HTTP method"}), 405
    
    


@app.route('/hero_powers', methods=["POST"])
def add_hero_power():
    # Get data from the request JSON
    strength = request.json.get('strength')
    power_id = request.json.get('power_id')
    hero_id = request.json.get('hero_id')

    # Validate 'strength'
    if strength not in ['Strong', 'Weak', 'Average']:
        return make_response({"errors": ["Validation error: 'strength' must be 'Strong', 'Weak', or 'Average"]}, 400)

    # Create a HeroPower instance
    hero_power = HeroPower(strength=strength, power_id=power_id, hero_id=hero_id)

    # Add the HeroPower to the database
    db.session.add(hero_power)
    db.session.commit()

    # Prepare a response
    resp = {
        "message": "HeroPower added successfully",
        "data": {
            "strength": hero_power.strength,
            "power_id": hero_power.power_id,
            "hero_id": hero_power.hero_id,
        }
    }

    # Return a response with a 201 status code
    return make_response(jsonify(resp), 201)

    
    
        

if __name__ == '__main__':
    app.run(port=3000, debug=True)
