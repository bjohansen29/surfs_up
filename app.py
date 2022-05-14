import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///hawaii.sqlite")
#set up database engine for Flask application

Base = automap_base()
# reflects database into our classes

Base.prepare(engine, reflect=True)
#reflects tables

Measurement = Base.classes.measurement
Station = Base.classes.station
#create a variable for each of the classes to reference them later

session = Session(engine)
#create a session link from Python to database

#define flask app
app = Flask(__name__)

#define welcome route of app
@app.route("/")
#add routing information for each route (function, then f string as reference to each)
def welcome():
    return(
    '''
    Welcome to the Climate Analysis API! <br>
    Available Routes: <br>
    /api/v1.0/precipitation <br>
    /api/v1.0/stations <br>
    /api/v1.0/tobs <br>
    /api/v1.0/temp/start/end <br>
    ''')
#using convention /api/v.1.0/ followed by route name- signifies version1
#I added <br> to each line to split them in browser- otherwise it was just one line

#create route for precip analysis
@app.route("/api/v1.0/precipitation")
def precipitation():
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)
#added code to calc date one yr ago from most recent date in db
#then added query to get date/precip for prev yr, including ".\" to show query continues to next line
#then added jsonify to format into json structured file

#create route for station analysis
@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    #creatae query  to get all stations in db
    stations = list(np.ravel(results))
    #unravel results into 1-d array with numpy, with results as parameter
    return jsonify(stations=stations)
    #to return list as Json, added stations=stations- this formats the list according to flask documentation https://flask.palletsprojects.com/en/2.0.x/api/#flask.json.jsonify

#create route for temp obs
@app.route("/api/v1.0/tobs")
def temp_monthly():
    #calc date one yr from last date in db
    prev_year = dt.date(2017,8,23) - dt.timedelta(days=365)
    #query primary station for all tobs from previous yr
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= prev_year).all()
    #unraval results into 1-d array, convert into list, jsonify list
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#create route for summ stats rpt
#needs both starting and ending date
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)