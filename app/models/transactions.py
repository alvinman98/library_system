from app import db
from datetime import datetime, timedelta

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="borrowed")  # borrowed, returned, late, etc
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))  # default 7 hari
    returned_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref="transactions")
    details = db.relationship("TransactionDetail", backref="transaction", cascade="all, delete-orphan")


class TransactionDetail(db.Model):
    __tablename__ = "transaction_details"

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey("transactions.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    book = db.relationship("Product", backref="transaction_details")
