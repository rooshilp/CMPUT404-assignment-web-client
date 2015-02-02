#!/usr/bin/env python
# coding: utf-8
# Copyright 2015 Abram Hindle, Rooshil Patel
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

    def get_code(self, data):
        code = data.split(" ")[1]

        return code

    def get_headers(self,data):
        headers = data.split("\r\n\r\n")[0]

        return headers

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

    def GET(self, url, args=None):
        url2 = urlparse.urlparse(url)
        host = url2.hostname
        port = url2.port
        path = url2.path
        net_loc = url2.netloc

        if port is None:
            port = 80
       
        s = self.connect(host, port)
        
        request = "GET %s HTTP/1.1\r\n" % path
        request += "Host: %s\r\n\r\n" % net_loc
        
        print(request)
        
        s.sendall(request)
        
        data = self.recvall(s)
        print(data)

        code = self.get_code(data)
        body = self.get_body(data)

        return HTTPRequest(int(code), body)

    def POST(self, url, args=None):
        url2 = urlparse.urlparse(url)
        host = url2.hostname
        port = url2.port
        path = url2.path
        net_loc = url2.netloc

        if port is None:
            port = 80
       
        s = self.connect(host, port)
        
        content = ""
        if args is not None:
            content = urllib.urlencode(args)
        
        content_length = len(content)
      

        request = "POST %s HTTP/1.1\r\n" % path
        request += "Host: %s\r\n" % net_loc
        request += "Content Type: application/x-www-form-urlencoded\r\n"
        request += "Content Length: %i\r\n\r\n" % content_length
        request += content

        s.send(request)
        
        data = self.recvall(s)
        
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
