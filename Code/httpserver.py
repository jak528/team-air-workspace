
#!/usr/bin/env python
 
from http.server import BaseHTTPRequestHandler, HTTPServer
import http.client
import json
import requests

 
# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
 
  # GET
  def do_GET(self):
        # Send response status code
        self.send_response(200)
 
        # Send headers
        self.send_header('Content-type','text/html')
        self.end_headers()
 
        # Send message back to client
        message = "Hello world!"
        # Write content as utf-8 data
        self.wfile.write(bytes(message, "utf8"))
        return
 
def run():
  print('starting server...')
 
  # Server settings
  # Choose port 8080, for port 80, which is normally used for a http server, you need root access
  server_address = ('127.0.0.1', 8081)
  httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
  print('running server...')

  origin = input("origin: ")
  destin = input("destination: ")
  date = input("YYYY-MM-DD: ")
  search(origin, destin, date)
  """
  data = {
  "request": {
    "slice": [
      {
        "origin": "JFK",
        "destination": "LAX",
        "date": "2017-10-14"
      }
    ],
    "passengers": {
      "adultCount": 1,
      "infantInLapCount": 0,
      "infantInSeatCount": 0,
      "childCount": 0,
      "seniorCount": 0
    },
    "solutions": 3,
    "refundable": "false"
  }
}"""

  """
  headers = {"Content-type": "application/json"}
  c = http.client.HTTPConnection('https://www.googleapis.com', 80)
  c.request('POST', '/qpxExpress/v1/trips/search?=AIzaSyDotnuacvhryCdrIoYJ5b-yYPyN6tm4t-4', json.dumps(data), headers, encode_chunked = False)
  doc = c.getresponse().read()
  print(doc)
  """
  
  










 
  httpd.serve_forever()
 
def search(origin, destin, date):

  api_key = "AIzaSyDotnuacvhryCdrIoYJ5b-yYPyN6tm4t-4"
  url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=" + api_key
  headers = {'content-type': 'application/json'}

  params = {
    "request": {
      "slice": [
        {
          "origin": origin,
          "destination": destin,
          "date": date
        }
      ],
      "passengers": {
        "adultCount": 1
      },
      "solutions": 2,
      "refundable": "false"
    }
  }

  response = requests.post(url, data=json.dumps(params), headers=headers)
  data = response.json()
  print(data)


run()