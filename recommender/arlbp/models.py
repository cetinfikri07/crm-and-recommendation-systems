from recommender.sharedbp import db
from datetime import datetime

class Base(db.Model):
     __abstract__ = True
     id = db.Column(db.Integer, primary_key=True)


class Rules(Base):
    __tablname__ = "rules"
    antecedents = db.Column(db.String(500))
    consequents = db.Column(db.String(500))
    antecedent_support = db.Column(db.Float())
    consequent_support = db.Column(db.Float())
    support = db.Column(db.Float())
    confidence = db.Column(db.Float())
    lift = db.Column(db.Float())
    leverage = db.Column(db.Float())
    conviction = db.Column(db.Float())



