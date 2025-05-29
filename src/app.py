"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

# create the jackson family object
jackson_family = FamilyStructure("Jackson")

# Los añado aquí para que existan cuando la aplicación inicie
jackson_family.add_member({
    "id": jackson_family._generateId(), # Usa el generador de ID
    "first_name": "John",
    "age": 33,
    "lucky_numbers": [7, 13, 22]
})
jackson_family.add_member({
    "id": jackson_family._generateId(),
    "first_name": "Jane",
    "age": 35,
    "lucky_numbers": [10, 14, 3]
})

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/members', methods=['GET'])
def handle_get_all_members():
    # this is how you can use the Family datastructure by calling its methods
    members = jackson_family.get_all_members()
    response_body = {
       
        "members": members
    }
    return jsonify(response_body), 200

@app.route('/member/<int:member_id>', methods=['GET'])
def handle_get_single_member(member_id):
    member = jackson_family.get_member(member_id)
    if member:
        return jsonify(member), 200
    else:
        return jsonify({"message": "Member not found"}), 404
    
@app.route('/member', methods=['POST'])
def handle_add_new_member():
    request_body = request.get_json()

    if not request_body:
        return jsonify({"message": "Request body is empty or not JSON"}), 400

    if "first_name" not in request_body or "age" not in request_body or "lucky_numbers" not in request_body:
        return jsonify({"message": "Missing required fields: first_name, age, lucky_numbers"}), 400

    if "id" in request_body:
        if not isinstance(request_body["id"], int) or request_body["id"] <= 0:
            return jsonify({"message": "Provided 'id' must be a positive integer if included"}), 400
            
    member_data = {
        "first_name": request_body["first_name"],
        "age": request_body["age"],
        "lucky_numbers": request_body["lucky_numbers"]
    }
    if "id" in request_body:
        member_data["id"] = request_body["id"]

    added_member = jackson_family.add_member(member_data)
    
    return jsonify(added_member), 200

@app.route('/member/<int:member_id>', methods=['DELETE'])
def handle_delete_one_member(member_id):
    was_deleted = jackson_family.delete_member(member_id)
    if was_deleted:
        return jsonify({"done": True}), 200
    else:
        return jsonify({"message": "Member not found or could not be deleted"}), 404

# también creé el de actualizar miembro
@app.route('/member/<int:member_id>', methods=['PUT'])
def handle_update_one_member(member_id):
    request_body = request.get_json()
    if not request_body:
        return jsonify({"message": "Request body is empty or not JSON"}), 400

    updated_member = jackson_family.update_member(member_id, request_body)
    if updated_member:
        return jsonify(updated_member), 200
    else:
        return jsonify({"message": "Member not found or could not be updated"}), 404

    

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
