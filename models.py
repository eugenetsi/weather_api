# models.py

# defining the class models that are needed for the db interaction
# for sqlalachemy and marshmallow

from datetime import datetime
from config import db, ma

# table model that ingests the db table
class Weather(db.Model):
    __tablename__ = "weather_data"
    index = db.Column(db.Integer, primary_key=True)
    loc = db.Column(db.String(128))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    date = db.Column(db.DateTime)
    temp = db.Column(db.Float)
    rain = db.Column(db.Float)
    wind = db.Column(db.Float)

# schema for serialization
class WeatherSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Weather
        load_instance = True
        sqla_session = db.session

# final objects that are going to be used
weather_schema = WeatherSchema()
weather_mult_schema = WeatherSchema(many=True)
