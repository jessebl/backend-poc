from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_restful import Resource, reqparse

from db import db

class ListingModel(db.Model):
    #used to be ^^ class ListingModel(db.Model):
    __tablename__ = 'listings' #our items database

    listing_id = db.Column(db.Integer, primary_key=True) # listing id's are assigned by integer key, not used by constructor
    price = db.Column(db.Float(precision = 2))
    condition = db.Column(db.String(15))
    isbn = db.Column(db.Integer, db.ForeignKey('books.isbn'))
    book = db.relationship('BookModel')
    google_tok = db.Column(db.String, db.ForeignKey('users.google_tok'))
    user = db.relationship('UserModel')
    status = db.Column(db.String(15))


    def __init__(self, price, condition, isbn, google_tok, status):
        self.price = price
        self.condition = condition
        self.isbn = isbn
        self.google_tok = google_tok
        self.status = status

    def json(self):
        return {"listing_id": self.listing_id, 'price': self.price, 'condition': self.condition, 'isbn': self.isbn, 'google_tok': self.google_tok, 'status': self.status}

    @classmethod
    def find_by_isbn(cls, isbn): # abstracted and redifined from get
        listings = ListingModel.query.filter_by(name=isbn).all() # returns all listings of isbn as a list
        if len(listings) > 0:
            return listings
        return None

    @classmethod
    def find_by_listing_id(cls, listing_id):
        listings = ListingModel.query.filter_by(name=listing_id).first()
        #For next time... How to search ONLY listing_id column???


    def save_to_db(self):
        # write to database
        # abstracted just like find_by_name so that it can be used by both post and put
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

class Listing(Resource):
    parser = reqparse.RequestParser() #Item class parser
    parser.add_argument("listing_id", #requests must be in format { "price": float}
        type=int,
        required=False,
        help="FORMAT ERROR: This request must have be string : integer "
    )
    parser.add_argument("price", #requests must be in format { "price": float}
        type=float,
        required=True,
        help="FORMAT ERROR: This request must have be string : float where string == price "
    )
    parser.add_argument("condition",
        type=str,
        required=True,
        help="FORMAT ERROR: This request must have be string : string "
    )
    parser.add_argument("isbn",
        type=int,
        required=True,
        help="FORMAT ERROR: This request must have be string : integer where string == price "
    )
    parser.add_argument("google_tok",
        type=str,
        required=True,
        help="FORMAT ERROR: This request must have be string : integer where string == price "
    )
    parser.add_argument("status",
        type=str,
        required=True,
        help="FORMAT ERROR: This request must have be string : string where string == price "
    )

    def get(self, isbn): # get request, looking for item called "name",
        l = ListingModel.find_by_isbn(isbn)
        if l:
            return l.json()
        return {"message": "Item not found"}, 404

    def post(self, isbn):
        #Code below shouldn't be necessary
        #if ListingModel.find_by_isbn(isbn):
        #    return {'message': 'An item with isbn ' + isbn + 'already exists.'}, 400
        data = Listing.parser.parse_args() # what the user will send to the post request (in good format)
        # In our case, the user sends the price as JSON, but the item name gets passed into the function
        item = ListingModel(data["price"], data["condition"], isbn, data["google_tok"], data["status"])
        try:
            item.save_to_db()
        except:
            return{"message": "An error occurred while inserting"}, 500 # internal server error

        return item.json(), 201 #post was successful

    def delete(self, listing_id):
        item = ListingModel.find_by_listing_id(listing_id)
        if item:
            item.delete_from_db()
            return {"message": "Item deleted"}
        return {"message": listing_id + " does not exist"}

    def put(self, listing_id, price, condition, isbn, google_tok, status): # aka "mostly just use to change status"
        data = Listing.parser.parse_args() # only add valid JSON requests into data

        if(listing_id):
            item = ListingModel.find_by_listing_id(listing_id) # find item
            if item:
                item.condition = condition # returns one element or None,
            else:
                return {"message": "listing not found"}

        else: # no listing found, add listing (probably unnecessary)
            item = ListingModel(data['price'], data["condition"], data["isbn"], data["google_tok"], data["status"])

        item.save_to_db()

        return item.json()


class allListings(Resource):
    def get(self):
        return{"listings": [item.json() for item in ListingModel.query.all()]}
