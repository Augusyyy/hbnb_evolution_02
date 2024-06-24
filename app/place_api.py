import re
from datetime import datetime

from flask import request
from flask_restx import Resource, fields

from app import place_api, db
from config import Config
from models.place import Place
from models.user import User
from models.city import City

"""Define the Place model for the API documentation"""
place_model = place_api.model('Place', {
    'id': fields.String(readonly=True, description='The place unique identifier'),
    'host_user_id': fields.String(required=True, description='The host user identifier'),
    'city_id': fields.String(required=True, description='The city identifier'),
    'name': fields.String(required=True, description='The place name'),
    'description': fields.String(description='The place description'),
    'address': fields.String(description='The place address'),
    'latitude': fields.Float(description='The geographical latitude of the place'),
    'longitude': fields.Float(description='The geographical longitude of the place'),
    'number_of_rooms': fields.Integer(required=True, description='The number of rooms available at the place'),
    'number_of_bathrooms': fields.Integer(required=True, description='The number of bathrooms available at the place'),
    'price_per_night': fields.Integer(required=True, description='The price per night for staying at the place'),
    'max_guests': fields.Integer(required=True, description='The maximum number of guests allowed'),
    'created_at': fields.DateTime(readonly=True, description='The time the place was created'),
    'updated_at': fields.DateTime(readonly=True, description='The time the place was last updated')
})


@place_api.route("")
class PlaceList(Resource):
    @place_api.doc("get all places")
    def get(self):
        """Query all places from the database"""
        places = Place.query.all()
        result = []
        """Convert each Place object to a dictionary"""
        for place in places:
            result.append({
                "id": place.id,
                "host_user_id": place.host_user_id,
                "city_id": place.city_id,
                "name": place.name,
                "description": place.description,
                "address": place.address,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "number_of_rooms": place.number_of_rooms,
                "number_of_bathrooms": place.number_of_bathrooms,
                "price_per_night": place.price_per_night,
                "max_guests": place.max_guests,
                "created_at": place.created_at.strftime(Config.datetime_format),
                "updated_at": place.updated_at.strftime(Config.datetime_format)
            })
        return result

    @place_api.doc('create a new place')
    @place_api.expect(place_model)
    @place_api.response(201, 'Place created successfully')
    @place_api.response(400, 'Invalid input')
    @place_api.response(404, 'User or City not found')
    def post(self):
        """Create a new place"""
        data = request.get_json()

        if not data.get('host_user_id') or not data.get('city_id') or not data.get('name') or not data.get(
                'number_of_rooms') or not data.get('number_of_bathrooms') or not data.get(
                'price_per_night') or not data.get('max_guests'):
            place_api.abort(400, message='Invalid input')

        user = User.query.filter_by(id=data['host_user_id']).first()
        city = City.query.filter_by(id=data['city_id']).first()
        if not user or not city:
            place_api.abort(404, message='User or City not found')

        new_place = Place(
            host_user_id=data['host_user_id'],
            city_id=data['city_id'],
            name=data['name'],
            number_of_rooms=data['number_of_rooms'],
            number_of_bathrooms=data['number_of_bathrooms'],
            price_per_night=data['price_per_night'],
            max_guests=data['max_guests'],
            description=data.get('description', ''),
            address=data.get('address', ''),
            latitude=data.get('latitude'),
            longitude=data.get('longitude')
        )
        db.session.add(new_place)
        db.session.commit()

        return {
            "id": new_place.id,
            "host_user_id": new_place.host_user_id,
            "city_id": new_place.city_id,
            "name": new_place.name,
            "description": new_place.description,
            "address": new_place.address,
            "latitude": new_place.latitude,
            "longitude": new_place.longitude,
            "number_of_rooms": new_place.number_of_rooms,
            "number_of_bathrooms": new_place.number_of_bathrooms,
            "price_per_night": new_place.price_per_night,
            "max_guests": new_place.max_guests,
            "created_at": new_place.created_at.strftime(Config.datetime_format),
            "updated_at": new_place.updated_at.strftime(Config.datetime_format)
        },

@place_api.route('/place/<string:place_id>')
class PlaceById(Resource):
    @place_api.doc('get_place')
    def get(self, place_id):
        """Query the place by ID from the database"""
        place = Place.query.filter_by(id=place_id).first()
        if place is None:
            place_api.abort(404, message='Place not found!')
        else:
            """Convert the Place object to a dictionary"""
            return {
                "id": place.id,
                "host_user_id": place.host_user_id,
                "city_id": place.city_id,
                "name": place.name,
                "description": place.description,
                "address": place.address,
                "latitude": place.latitude,
                "longitude": place.longitude,
                "number_of_rooms": place.number_of_rooms,
                "number_of_bathrooms": place.number_of_bathrooms,
                "price_per_night": place.price_per_night,
                "max_guests": place.max_guests,
                "created_at": place.created_at.strftime(Config.datetime_format),
                "updated_at": place.updated_at.strftime(Config.datetime_format)
            }

    @place_api.doc('update_place')
    @place_api.expect(place_model)
    @place_api.response(200, 'Place updated successfully')
    @place_api.response(400, 'Invalid input')
    @place_api.response(404, 'Place not found')
    def put(self, place_id):
        data = request.get_json()
        if not data:
            place_api.abort(400, "Invalid input")

        place = Place.query.filter_by(id=place_id).first()
        if not place:
            place_api.abort(404, 'Place not found')

        if 'name' in data:
            place.name = data['name']
        if 'description' in data:
            place.description = data['description']
        if 'address' in data:
            place.address = data['address']
        if 'latitude' in data:
            place.latitude = data['latitude']
        if 'longitude' in data:
            place.longitude = data['longitude']
        if 'number_of_rooms' in data:
            place.number_of_rooms = data['number_of_rooms']
        if 'number_of_bathrooms' in data:
            place.number_of_bathrooms = data['number_of_bathrooms']
        if 'price_per_night' in data:
            place.price_per_night = data['price_per_night']
        if 'max_guests' in data:
            place.max_guests = data['max_guests']

        place.updated_at = datetime.now()
        db.session.commit()

        return {
            "id": place.id,
            "host_user_id": place.host_user_id,
            "city_id": place.city_id,
            "name": place.name,
            "description": place.description,
            "address": place.address,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "number_of_rooms": place.number_of_rooms,
            "number_of_bathrooms": place.number_of_bathrooms,
            "price_per_night": place.price_per_night,
            "max_guests": place.max_guests,
            "created_at": place.created_at.strftime(Config.datetime_format),
            "updated_at": place.updated_at.strftime(Config.datetime_format)
        }, 200

    @place_api.doc('delete_place')
    def delete(self, place_id):
        place = Place.query.filter_by(id=place_id).first()
        if place is None:
            return place_api.abort(400, 'User not found')
        try:
            db.session.delete(place)
            db.session.commit()
            return "delete successfully", 200
        except Exception as e:
            db.session.rollback()
            place_api.abort(400, message='Create fail')