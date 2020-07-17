############################
# Dependencies import
############################
import datetime as dt
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np

from flask import Flask, jsonify

###############
# DB setup
###############
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

####################
# Flask Setup
####################

app = Flask(__name__)

######################
# Flask Routes
######################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/(<start>/<end><br/>"
    )


"""Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
      * Return the JSON representation of your dictionary."""


@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)

    results = (session.query(Measurement.date, Measurement.prcp).\
                       order_by(Measurement.date).all())
                 
    session.close()

    precipData = []
    for result in results:
        precipDict = {result.date: result.prcp}
        precipData.append(precipDict)

    return jsonify(precipData)
    
    

"""Return a JSON list of stations from the dataset."""
@app.route("/api/v1.0/Stations")
def stations():

    session = Session(engine)

    results = session.query(Station.station).all()

    session.close()

    station_list = list(np.ravel(results))

    return jsonify(station_list)


"""* Query the dates and temperature observations of the most active 
     station for the last year of data."""


@app.route("/api/v1.0/tobs")
def temperature():

    session = Session(engine)

    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    temperature_results = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
         filter(Measurement.date > last_year).\
         filter(Measurement.station == 'USC00519281').all()

    session.close()

    temperature_list = list(np.ravel(temperature_results))

    return jsonify(temperature_list)


"""* Return a JSON list of the minimum temperature, the average temperature,
 and the max temperature for a given start or start-end range."""


@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)

    start_date = dt.datetime.strptime("%Y-%m-%d")

    stats = session.query(func.min(Measurement.tobs),
                          func.max(Measurement.tobs),
                          func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

    session.close()

    summary = list(np.ravel(stats))

    return jsonify(summary)


@app.route("/api/v1.0/(<start>/<end>")
def start_end_dates(start, end):

    session = Session(engine)

    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d")

    stats = session.query(func.min(Measurement.tobs),
                          func.max(Measurement.tobs),
                          func.avg(Measurement.tobs)).\
        filter(Measurement.date.between(start_date, end_date)).all()

    session.close()

    summary = list(np.ravel(stats))

    return jsonify(summary)


if __name__ == '__main__':
    app.run(debug=True)
