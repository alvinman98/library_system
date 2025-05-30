from app.db import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    qty = db.Column(db.Integer, default=0)

    @property
    def available(self):
        return self.qty > 0
