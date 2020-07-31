import json
import geoip2.database
from flask import Flask, Response, request
import os
import prometheus_client
from prometheus_client import Counter, generate_latest
import socket
import random
import struct

app = Flask(__name__)
reader= geoip2.database.Reader("datasets/GeoLite2-City.mmdb")

graphs = {}
graphs['c'] = Counter('nginx_remote_addr_info', 'remote_addr information', ['continentName', 'countryName',
                                                            'countryCode','cityName','cityLant','cityLong','host'])


graphs['default'] = Counter('nginx_remote_addr_default_info', 'remote_addr information by default nginx logs', ['continentName', 'countryName',
                                                            'countryCode','cityName','cityLant','cityLong'])


def getData(ip):
    response = reader.city(ip)
    continentName=response.continent.names["en"]
    countryName=response.country.name
    countryCode=response.country.iso_code
    cityName=response.city.name
    cityLant=response.location.latitude
    cityLong=response.location.longitude
    # reader.close()
    return (continentName,countryName,countryCode,cityName,cityLant,cityLong)



def createMetrics(data,ip):
    continentName,countryName,countryCode,cityName,cityLant,cityLong=getData(ip)
    if "host" in data:
        graphs['c'].labels(continentName,countryName,countryCode,cityName,cityLant,cityLong,data["host"]).inc()
    else:
        graphs['default'].labels(continentName,countryName,countryCode,cityName,cityLant,cityLong).inc()




@app.route("/",methods = ['GET'])
def main():

    return "OK"

@app.route("/",methods = ['POST'])
def put():
    data = json.loads(request.data)
    print(data)

    createMetrics(data,data["ipaddress"])

    return "OK"


@app.route("/metrics")
def requests_count():
    res = []
    for k,v in graphs.items():
        res.append(prometheus_client.generate_latest(v))
    return Response(res, mimetype="text/plain")


if __name__ == '__main__':
        app.run(debug=True,port=8080,host='0.0.0.0')
