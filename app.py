import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#create engine to hawaii.sqlite
engine = create_engine(f"sqlite:///hawaii.sqlite")
conn = engine.connect()

#reflect existing database into a new model
Base = automap_base()

#reflect the tables
Base.prepare(engine, reflect=True)

#save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup
app = Flask(__name__)

#Flask Routes
@app.route("/")
def welcome():
    return(
        f"Welcome! Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def json_precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    prcp_data = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precipitation"] = prcp
        prcp_data.append(prcp_dict)
    return jsonify(prcp_data)


@app.route("/api/v1.0/stations")
def json_stations():
    session = Session(engine)
    result = session.query(Station.name).all()
    session.close()
    stations = []
    for s in result:
        stations.append(s[0])
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def json_tobs():
    session = Session(engine)
    active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    calculations = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.station=='USC00519281').all()

    previous_temperature_observations = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date > '2016-08-23').all()

    session.close()

    tobs_data = []
    for date, temperature in previous_temperature_observations :
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["temperature"] = temperature
        tobs_data.append(tobs_dict)
    return jsonify(tobs_data)


@app.route("/api/v1.0/<start>")
def temp_data_start(start):
    session = Session(engine)
    start_dt = dt.datetime.strptime(start,"%Y-%m-%d")
    end_dt = dt.datetime.strptime("2016-08-23", "%Y-%m-%d")
    start_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >start_dt).all()
    session.close()

    data = []
    for minimum, maximum, average in start_summary:
        start_dict = {}
        start_dict["min"] = minimum
        start_dict["max"] = maximum
        start_dict["avg"] = average
        data.append(start_dict)
    return jsonify(data)

@app.route("/api/v1.0/<start>/<end>")
def temp_data_start_end(start, end):
    session = Session(engine)
    start_dt = dt.datetime.strptime(start,"%Y-%m-%d")
    end_dt = dt.datetime.strptime("2016-08-23","%Y-%m-%d") 
    
    start_end_summary = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date > start_dt).\
        filter(Measurement.date < end_dt).all()
    session.close()

    data = []
    for minimum, maximum, average in start_end_summary:
        start_end_dict = {}
        start_end_dict["min"] = minimum
        start_end_dict["max"] = maximum
        start_end_dict["avg"] = average
        data.append(start_end_dict)
    return jsonify(data)



if __name__ =='__main__':
    app.run(debug=True)