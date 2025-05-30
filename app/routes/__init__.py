from flask import Blueprint
from . import auth, user, books, cart

def register_routes(app):
    app.register_blueprint(auth.bp)
    app.register_blueprint(user.bp)
    app.register_blueprint(books.bp)
    app.register_blueprint(cart.bp)
