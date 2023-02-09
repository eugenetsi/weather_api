# app.py

# API top level runner - initializes the API and sets up the relevant config files

# populate database
import populate
populate.run()

from flask import request, jsonify, render_template
import config
from models import Weather
import logging

# init app and set API config file - swagger.yml
app = config.connex_app
app.add_api(config.basedir/"swagger.yml")

# homepage
@app.route("/")
def home():
    weather_mult = Weather.query.all()
    return render_template("home.html", weather_mult=weather_mult) # jinja rendering engine

if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=8000, debug=True)
    app.run(host="0.0.0.0", port=8000)

