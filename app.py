#import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import pandas as pd

#database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# determine the classes
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a dictionary of dates and their corresponding precipitation values"""
    # Query all passengers
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    dateprecip_dict = {}
    for date, precip in results:
        dateprecip_dict.update({date: precip})

    return jsonify(dateprecip_dict)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """Return a list of all the stations"""
    # Query all stations
    results = session.query(Station.id, Station.station, Station.name).all()

    session.close()

    list_of_stations = []
    for id, station, name in results:
        station_info = (id, station, name)
        list_of_stations.append(station_info)
    
    return jsonify(list_of_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Determines the most active station and its previous 12 months of data. Returns list of temperature observations"""
    #list station_ids based on the amount of observations
    stations_id = session.query(Station.id).\
                    filter(Measurement.station == Station.station).group_by('station').order_by(func.count(Station.station).desc())
    
    most_active_station = stations_id[0][0]
    
    #find most recent date for this station
    most_recent_date_station = session.query(Measurement.date).\
                                filter(Measurement.station == Station.station).\
                                filter(Station.id == most_active_station).\
                                order_by(Measurement.date.desc()).first()
    
    most_recent_date_station[0]
    #most_recent_date 2017-08-18

    #determine 12 months before
    query_date_station = dt.date(2017, 8, 18) - dt.timedelta(days=365.25)
    query_date_station
    
    #query the past year of data of the most active station
    active_station_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == Station.station).filter(Station.id == most_active_station).\
                filter(Measurement.date < most_recent_date_station[0]).\
                filter(Measurement.date > query_date_station).all()

    session.close()

    dates_tobs = []
    for date, tobs in active_station_data:
        datetobs_dict = {}
        datetobs_dict['date'] = date
        datetobs_dict['tobs'] = tobs
        dates_tobs.append(datetobs_dict)

    return jsonify(dates_tobs)

@app.route("/api/v1.0/<start>")
def startpoint(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return tmins, tmaxs, and tavgs for a given start date until most recent"""
    # Query the tobs from start date until most recent 
    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()
    session.close()

    # Convert query results into dictionary
    tobs_dict = {'tobs_avg': results[0][0],
                 'tobs_min': results[0][1],
                 'tobs_max': results[0][2]}
    

    return jsonify(tobs_dict)

@app.route("/api/v1.0/<start>/<end>")
def startendrange(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return tmins, tmaxs, and tavgs for a given range of dates"""
    # Query cannnonicalize the date arguments passengers
    results = session.query(func.avg(Measurement.tobs), func.min(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    # Convert list of tuples into normal list
    tobs_dict = {'tobs_avg': results[0][0],
                 'tobs_min': results[0][1],
                 'tobs_max': results[0][2]}
    

    return jsonify(tobs_dict)

if __name__ == "__main__":
    app.run(debug=True)