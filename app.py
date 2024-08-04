# Import the dependencies.

from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create the engine to connect to your database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database tables into classes
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to the classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session to link Python to the database
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
#PART 1 
#Start at the homepage.
#List all the available routes
@app.route('/')
def home():
    routes = {
        "routes": {
            "homepage": "/",
            "precipitation": "/api/v1.0/precipitation",
            "stations": "/api/v1.0/stations",
            "temperature_observations": "/api/v1.0/tobs",
            "start_date": "/api/v1.0/<start>",
            "start_end_date": "/api/v1.0/<start>/<end>"
        }
    }
    return jsonify(routes)

if __name__ == '__main__':
    app.run(debug=True)   

#PART 2
#Convert the query results to a dictionary by using date as the key and prcp as the value.

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB.
    session = Session(engine)
    
    # Calculate the date one year from the most recent data point in the database.
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= prior_year).all()

    # close the session
    session.close()

    # Return the JSON representation of your dictionary.
    
    hawaii_prcp = []
    for date, prcp in results:
        results = {}
        results['date'] = date
        results['prcp'] = prcp
        hawaii_prcp.append(results)
    
    return jsonify(hawaii_prcp)

# PART 3
#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
   
    # Create our session 
    session = Session(engine)

    # Query the active stations
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
             group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    # Close the session
    session.close()

    # Convert to dictionary using station as key, station count as value
    all_stations = []
    for station, count in active_stations:
        active_stations = {}
        active_stations["station"] = station
        active_stations["count"] = count
        all_stations.append(active_stations)
    
    # Return JSON
    return jsonify(all_stations)

# PART 4
#Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session
    session = Session(engine)

    # Query the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]

    # To find all dates of the previous year, first find the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).first()

    # Next, calculate the date one year from the most recent date in the dataset
    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most active station for the previous year
    date_temps = session.query(Measurement.date, Measurement.tobs).\
        filter(
            Measurement.date >= prior_year,
            Measurement.station == most_active_station
        ).all()

    # Close the session
    session.close()

    # return a list of alall of the temperature observations for the previous year
    all_values = []
    for date, tobs in date_temps:
        date_tobs = {}
        date_tobs["date"] = date
        date_tobs["tobs"] = tobs
        all_values.append(date_tobs)
        
    # Return JSON
    return jsonify(all_values)
    
#Part 5
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

#For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/temp/<start>")
def start_date(start):
  
    # Create session (link) 
    session = Session(engine)

    # Query min temp, avg temp, and max temp for date greater than or equal to start date
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    start_date_query = session.query(
        func.min(Measurement.tobs),\
        func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    # Close the session
    session.close()

    # Convert query results to a dictionary
    start_date_values = []
    for tmin, tavg, tmax in start_date_query:
        start_dict = {}
        start_dict["min"] = tmin
        start_dict["avg"] = tavg
        start_dict["max"] = tmax
        start_date_values.append(start_dict)
    
    # Return JSON
    return jsonify(start_date_values)

#for a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
    
@app.route("/api/v1.0/temp/<start>/<end>")
def start_end_date(start, end):
    
    # Create session .
    session = Session(engine)

    # Query min temp, avg temp, and max temp for dates between start and end dates
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")
    start_end_date_query = session.query(
        func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= start, Measurement.date <= end).all()
    
    # Close the session
    session.close()

    # Convert query results to a dictionary
    start_end_date_values = []
    for tmin, tavg, tmax in start_end_date_query:
        start_end_dict = {}
        start_end_dict["min"] = tmin
        start_end_dict["avg"] = tavg
        start_end_dict["max"] = tmax
        start_end_date_values.append(start_end_dict)
        
    # Return JSON
    return jsonify(start_end_date_values)

if __name__ == '__main__':
    app.run(debug=True)

