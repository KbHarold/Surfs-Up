##################################################
#Import Dependencies
##################################################
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

#Creates precipitation API
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return a dictionary of all dates and rainfall amounts"""
    session = Session(engine)
    year_ago = dt.date(2017, 8, 23)- dt.timedelta(days=365)

    precp_results_12_mo = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= year_ago).order_by(Measurement.date).all()

    precp = []
    for date, precip in precp_results_12_mo:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = precip
        precp.append(precip_dict)
 
    return jsonify(precp)

#Creates stations API
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations"""
    session = Session(engine)
    station_results = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()

    stations =[]
    for station, observation in station_results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["number of observations"] = observation
        stations.append(station_dict)
        
    return jsonify(stations)

#Creates Temperature observations API
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""
    session = Session(engine)
    year_ago = dt.date(2017, 8, 23)- dt.timedelta(days=365)
    most_active = session.query(Measurement.station).\
    group_by(Measurement.station).order_by((func.count(Measurement.tobs)).desc()).first()

    tobs_results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date >= year_ago).filter_by(station = most_active[0]).\
    order_by(Measurement.date.desc()).all()

    tobs_list = []
    for date, temp in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature"] = temp
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)

#Creates API for temp min, max and avg from given date forward
@app.route("/api/v1.0/<start_date>")
def start(start_date):
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date"""
    session = Session(engine)
    mnmxav_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    tobs_start_list = []
    for min, avg, max in mnmxav_results:
        min_max_avg_start_dict = {}
        min_max_avg_start_dict["min"] = min
        min_max_avg_start_dict["average"] = avg
        min_max_avg_start_dict["max"] = max
        tobs_start_list.append(min_max_avg_start_dict)

    return jsonify(tobs_start_list)

#Creates API for temp min, max and avg given date range    
@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date):
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    session = Session(engine)
    mnmxav_results_all = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    tobs_start_all_list = []

    for min, avg, max in mnmxav_results_all:
        min_max_avg_all_start_dict = {}
        min_max_avg_all_start_dict["min"] = min
        min_max_avg_all_start_dict["average"] = avg
        min_max_avg_all_start_dict["max"] = max
        tobs_start_all_list.append(min_max_avg_all_start_dict)

    return jsonify(tobs_start_all_list)

if __name__ == '__main__':
    app.run(debug=True)