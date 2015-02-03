#!/usr/bin/env python
# coding: utf-8
# Copyright 2015 Abram Hindle and Rooshil Patel
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

# HTTPClient implementation completed by Rooshil Patel

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    # gets the host and port information from a urlparse'd url
    def get_host_port(self, url_parsed):
        host = url_parsed.hostname
        port = url_parsed.port

        # if no port is provided, default is set to 80
        if port is None:
            port = 80

        return host, port

    # creates a socket and connects it to the provided host and port
    def connect(self, host, port):
        # use sockets!
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
        except socket.error as error_code:
            print("Failed to create socket!")
            print("Error code: " + str(error_code[0]) + 
                  ". Error Message: " + error_code[1])
            sys.exit()

        print("Socket created successfully!")
        
        try:
            s.connect((host, port))

        except socket.error as error_code:
            print("Failed to connect!")
            print("Error code: " + str(error_code[0]) + 
                  ". Error Message: " + error_code[1])
            sys.exit()

        print("Socket sucessfully connected!")

        return s

    # returns the HTTP code received from the connected host
    def get_code(self, data):
        code = data.split(" ")[1]

        return code

    # returns the header received from the connected host
    def get_headers(self,data):
        headers = data.split("\r\n\r\n")[0]

        return headers

    # returns the body of content received from the connected host
    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]

        return body

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    # method parses url provided, creates and connects a socket to the parsed host and port,
    # generates an HTTP GET request, sends the request, waits for a response, parses the 
    # response and returns an HTTPRequest object with the parsed info.
    def GET(self, url, args=None):
        # parses url with the urlparse library and retrieves the required information
        url_parsed = urlparse.urlparse(url)
        host, port = self.get_host_port(url_parsed)
        path = url_parsed.path
        net_loc = url_parsed.netloc
       
        # creates and connects a socket using host and port
        s = self.connect(host, port)
        
        # generates HTTP GET request
        request = "GET %s HTTP/1.1\r\n" % path
        request += "Host: %s\r\n\r\n" % net_loc
        
        s.sendall(request)
        
        data = self.recvall(s)
        
        # parses received data from host
        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(int(code), body)
    
    # method parses url provided, creates and connects a socket to the parsed host and port,
    # encodes any arguments provided, generates an HTTP POST request, sends the request, 
    # waits for a response, parses the response and returns an HTTPRequest object with the parsed info.
    def POST(self, url, args=None):
        # parses url with the urlparse library and retrieves the required information
        url_parsed = urlparse.urlparse(url)
        host, port = self.get_host_port(url_parsed)
        path = url_parsed.path
        net_loc = url_parsed.netloc
       
        # creates and connects a socket using host and port
        s = self.connect(host, port)
        
        # creates content string and, if arguments are present, encodes them
        content = ""
        if args is not None:
            content = urllib.urlencode(args)
        
        content_length = len(content)
      
        # Generates HTTP PoST request and adds encoded content
        request = "POST %s HTTP/1.1\r\n" % path
        request += "Host: %s\r\n" % net_loc
        request += "Content-Type: application/x-www-form-urlencoded\r\n"
        request += "Content-Length: %i\r\n\r\n" % content_length
        request += content

        s.sendall(request)
        
        data = self.recvall(s)
        
        # parses received data from host
        code = self.get_code(data)
        body = self.get_body(data)
        
        return HTTPRequest(int(code), body)

    def command(self, command, url, args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[1], sys.argv[2] )
    else:
        print client.command( command, sys.argv[1] )    