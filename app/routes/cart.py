from flask import Blueprint, request, jsonify
from datetime import datetime
from app.db import db
from app.models.cart import Cart, Favorite
from app.models.transactions import Transaction, TransactionDetail
from app.models.books import Product
from app.decorators import login_required
from flask_jwt_extended import get_jwt_identity

bp = Blueprint("cart", __name__, url_prefix="/cart")

# ---- CART ----

@bp.route("/", methods=["GET"])
@login_required
def get_cart():
    user_id = int(get_jwt_identity())
    items = Cart.query.filter_by(user_id=user_id).all()
    result = [
        {
            "id": item.id,
            "product_id": item.product.id,
            "product_name": item.product.name,
            "qty": item.qty,
        }
        for item in items
    ]
    return jsonify(result)

@bp.route("/", methods=["POST"])
@login_required
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data["product_id"]
    qty = data.get("qty", 1)

    book = Product.query.get(product_id)
    if not book:
        return jsonify({"msg": "Book not found"}), 404

    existing = Cart.query.filter_by(user_id=user_id, product_id=product_id).first()
    total_requested = qty
    if existing:
        total_requested += existing.qty

    if total_requested > book.qty:
        return jsonify({
            "msg": f"Only {book.qty} item(s) available in stock"
        }), 400

    if existing:
        existing.qty += qty
    else:
        new_cart = Cart(user_id=user_id, product_id=product_id, qty=qty)
        db.session.add(new_cart)

    db.session.commit()
    return jsonify({"message": "Added to cart"})

@bp.route("/<int:item_id>", methods=["DELETE"])
@login_required
def remove_from_cart(item_id):
    data = request.get_json()
    qty = data.get("qty", 1)
    user_id = int(get_jwt_identity())
    existing = Cart.query.filter_by(user_id=user_id, product_id=item_id).first()
    if existing.user_id != user_id:
        return jsonify({"error": "Not authorized"}), 403
    if existing.qty - qty < 1:
        db.session.delete(existing)
    else:
        existing.qty -= qty
    db.session.commit()
    return jsonify({"message": "Removed from cart"})

# ---- FAVORITES ----

@bp.route("/favorites", methods=["GET"])
@login_required
def get_favorites():
    user_id = int(get_jwt_identity())
    items = Favorite.query.filter_by(user_id=user_id).all()
    result = [
        {
            "id": fav.id,
            "product_id": fav.product.id,
            "product_name": fav.product.name,
        }
        for fav in items
    ]
    return jsonify(result)

@bp.route("/favorites", methods=["POST"])
@login_required
def add_favorite():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data["product_id"]

    exists = Favorite.query.filter_by(user_id=user_id, product_id=product_id).first()
    if exists:
        return jsonify({"message": "Already favorited"}), 400

    fav = Favorite(user_id=user_id, product_id=product_id)
    db.session.add(fav)
    db.session.commit()
    return jsonify({"message": "Added to favorites"})

@bp.route("/favorites/<int:item_id>", methods=["DELETE"])
@login_required
def remove_favorite(item_id):
    user_id = int(get_jwt_identity())
    item = Favorite.query.get_or_404(item_id)
    if item.user_id != user_id:
        return jsonify({"error": "Not authorized"}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Removed from favorites"})

# ---- CHECK OUT ----

@bp.route("/checkout", methods=["POST"])
@login_required
def checkout():
    user_id = int(get_jwt_identity())
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    if not cart_items:
        return jsonify({"msg": "Cart is empty"}), 400

    # Validasi stok
    for item in cart_items:
        if item.product.qty < item.qty:
            return jsonify({
                "msg": f"Not enough stock for book '{item.product.title}' (available: {item.product.qty})"
            }), 400

    # Buat transaksi utama
    transaction = Transaction(user_id=user_id, status='borrowed', created_at=datetime.utcnow())
    db.session.add(transaction)
    db.session.flush()  # agar bisa akses transaction.id

    # Tambahkan detail & update stok
    for item in cart_items:
        # Buat detail transaksi
        tx_detail = TransactionDetail(
            transaction_id=transaction.id,
            product_id=item.product_id,
            qty=item.qty
        )
        db.session.add(tx_detail)

        # Kurangi stok buku
        item.product.qty -= item.qty

    # Hapus cart
    Cart.query.filter_by(user_id=user_id).delete()

    db.session.commit()
    return jsonify({"msg": "Checkout successful", "transaction_id": transaction.id})
