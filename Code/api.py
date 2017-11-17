from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
	return 'Hello, World!'

@app.route('/search')
def search():
	carrier = request.args.get('carrier')
	flightNum = request.args.get('flight')
	departureTime = request.args.get('time')
	originAirport = request.args.get('origin')
	destinationAirport = request.args.get('destination')
	zipcode = request.args.get('zipcode')

	time = departureTime[:-6].replace('T', ' ') + ' EST' # YYYY-MM-DD HH:MM
	origin = zipcode # origin of surface transportation
	destination = originAirport # destination of surface transportation

	return  carrier+flightNum+" from "+origin+" to "+destination+" at "+time

