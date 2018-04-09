from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from flask_restful import Resource, reqparse

from db import db


class BookModel(db.Model):
	"""The Book object stores information about the book, as well as
	the listing objects that are associated with it.
    Attributes:
        isbn (string): The isbn number for the book.
        title (string): The title of the book.
		author (string): The author/authors of the book.
		listings (Listing): The current listings of the book.
    """

    # Creates a table named 'book'
	__tablename__ = 'books'

	isbn = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	author = db.Column(db.String)
	# One to many relationship: Book to listings
	# Changing Owen's method a bit using different functions, hopefully desired effect
	listings = db.relationship('ListingModel')

	def __init__(self, isbn, title, author):
		self.isbn = isbn
		self.title = title
		self.author = author


	def get_listings(self):
		listing_ids = []
		for listing in self.listings:
			listing_ids.append(listing.json())
		return listing_ids

	# Returns a json object representing the book
	def json(self):
		return {'isbn': self.isbn, 'title': self.title, 'author': self.author, 'listings': self.get_listings()}

	@classmethod
	def find_by_isbn(cls, isbn): # Abstracted and redefined from get
		return BookModel.query.filter_by(isbn=isbn).first()

	def save_to_db(self):
		db.session.add(self)
		db.session.commit()
		return self.json()

	def delete_from_db(self):
		db.session.delete(self)
		db.session.commit()
		return json()

	# How the book class will be printed
	def __repr__(self):
		return "<Book(isbn='%s', title='%s', author='%s')>" % (
			self.isbn, self.title, self.author)


class Book(Resource):
	parser = reqparse.RequestParser() # Book class parser
	"""parser.add_argument('isbn',
		type=int,
        required=True,
		help="This field cannot be blank."
	)"""
	parser.add_argument('title',
		type=str,
		required=True,
		help="This field cannot be blank."
	)
	parser.add_argument('author',
		type=str,
		required=True,
		help="This field cannot be blank."
	)

	def get(self, isbn): # Get request, looking for isbn
		book = BookModel.find_by_isbn(isbn)
		if book:
			return book.json()
		return {"message": "Book not found"}, 404

	def post(self, isbn):
		data = Book.parser.parse_args()
		if BookModel.find_by_isbn(isbn):
			return {'message': 'A book with isbn ' + str(isbn) + 'already exists'}, 400
		book = BookModel(isbn, data['title'], data['author'])
		book.save_to_db()
		return {"message": "Book created successfully."}, 201

	def delete(self, isbn):
		book = BookModel.find_by_isbn(isbn)
		if book:
			book.delete_from_db()
			return {"message": "Book deleted"}
		return {"message": "Book with isbn (" + isbn + ") does not exist."}

	"""def put(self, isbn):
		data = Book.parser.parse_args()
      	# Find book with matching isbn
		book = BookModel.find_by_isbn(isbn)

		if book is None:
			book = BookModel(isbn, data['title'], data['author'])
		else:
			book.title = data['title']
			book.author = data['author']"""

class BookList(Resource):
	def get(self):
		return {"books": [book.json() for book in BookModel.query.all()]}
