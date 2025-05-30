from flask import Blueprint, request, jsonify
from app.db import db
from app.models.user import User
from app.decorators import login_required, admin_required
from flask_jwt_extended import get_jwt_identity

bp = Blueprint("user", __name__, url_prefix="/users")


@bp.route("/", methods=["GET"])
@admin_required
def get_all_users():
    current_user_id = get_jwt_identity()
    users = User.query.all()
    result = [
        {"id": u.id, "email": u.email, "name": u.name, "role": u.role.name}
        for u in users
    ]
    return jsonify(result)


@bp.route("/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({"id": user.id, "email": user.email, "name": user.name, "role": user.role.name})


@bp.route("/", methods=["POST"])
@admin_required
def create_user():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(
        email=data["email"],
        name=data["name"],
        role=data.get("role", "user")  # default role user
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created"}), 201


@bp.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(email=data["email"], name=data["name"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201


@bp.route("/<int:user_id>", methods=["PUT"])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    user.name = data.get("name", user.name)
    user.email = data.get("email", user.email)
    if data.get("password"):
        user.set_password(data["password"])
    if data.get("role"):
        user.role = data["role"]
    db.session.commit()
    return jsonify({"message": "User updated"})


@bp.route("/<int:user_id>", methods=["DELETE"])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})
