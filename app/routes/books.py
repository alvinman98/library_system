from flask import Blueprint, jsonify, request
from app.models.books import Product
from app.db import db
from app.services.redis_cache import get_cache, set_cache, get_redis_client
from app.models.books import Product
from app.decorators import login_required, admin_required

bp = Blueprint("product", __name__, url_prefix="/products")

@bp.route("/", methods=["GET"])
def list_products():
    cached = get_cache("product_list")
    if cached:
        return jsonify(eval(cached))  # gunakan literal_eval jika perlu lebih aman

    products = Product.query.all()
    result = [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "qty": p.qty,
            "available": p.available,
        }
        for p in products
    ]
    set_cache("product_list", str(result), 300)  # cache 60 detik
    return jsonify(result)

@bp.route("/", methods=["POST"])
@admin_required
def create_product():
    data = request.get_json()
    product = Product(
        name=data["name"],
        description=data.get("description", ""),
        qty=data.get("qty", 0)
    )
    db.session.add(product)
    db.session.commit()
    r = get_redis_client()
    r.delete("product_list")
    return jsonify({"message": "Product created"}), 201

@bp.route("/<int:product_id>", methods=["PUT"])
@admin_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    product.name = data.get("name", product.name)
    product.description = data.get("description", product.description)
    product.qty = data.get("qty", product.qty)
    db.session.commit()
    r = get_redis_client()
    r.delete("product_list")
    return jsonify({"message": "Product updated"})

@bp.route("/<int:product_id>", methods=["DELETE"])
@admin_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    r = get_redis_client()
    r.delete("product_list")
    return jsonify({"message": "Product deleted"})
