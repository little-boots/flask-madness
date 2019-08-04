import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, distinct

from flask import Flask, jsonify

import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Functions
#################################################
def calc_temps(start_date, end_date, session):
    if end_date is None:
        return session.query(func.min(Measurement.tobs),
                         func.avg(Measurement.tobs),
                         func.max(Measurement.tobs))\
        .filter(Measurement.date >= start_date)\
        .all()[0]

    else: return session.query(func.min(Measurement.tobs),
                         func.avg(Measurement.tobs),
                         func.max(Measurement.tobs))\
         .filter(Measurement.date >= start_date)\
         .filter(Measurement.date <= end_date)\
         .all()[0]

def last_date(session):
    lastdate = dt.date.fromisoformat((session.query(func.max(Measurement.date)).all()[0][0]))
    lastdate12 = dt.date(lastdate.year - 1, lastdate.month, lastdate.day)
    return lastdate12

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start]/[end]"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a list of all station IDs and preciptation readings"""
    # Query all Measurements
    session = Session(engine)
    results = session.query(Measurement.station, Measurement.prcp).all()

    all_precip =  []
    for station, prcp in results:
        precip_dict = {}
        precip_dict["station"] = station
        precip_dict["prcp"] = prcp
        all_precip.append(precip_dict)

    return jsonify(all_precip)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all station IDs and names"""
    # Query all passengers
    session = Session(engine)
    results = session.query(distinct(Station.station), Station.name).all()

    # Create a dictionary from the row data and append to a list of all_tobs
    all_stations =  []
    for station, name in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        all_stations.append(stations_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of station IDs, dates, and temperature observations"""
    # Query all passengers
    session = Session(engine)

    cutoff = last_date(session)

    results = session.query(Measurement.station,
                            Measurement.date,
                            Measurement.tobs)\
              .filter(Measurement.date >= cutoff).all()

    # Create a dictionary from the row data and append to a list of all_tobs
    all_tobs =  []
    for station, date, tobs in results:
        tobs_dict = {}
        tobs_dict["station"] = station
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def mystart(start):
    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    session = Session(engine)
    tmin, tave, tmax = calc_temps(start, None, session)

    return jsonify(tmin, tave, tmax)

@app.route("/api/v1.0/<start>/<end>")
def myend(start, end):
    """Return a list of passenger data including the name, age, and sex of each passenger"""
    # Query all passengers
    session = Session(engine)
    tmin, tave, tmax = calc_temps(start, end, session)

    return jsonify(tmin, tave, tmax)


if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True)
