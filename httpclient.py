#!/usr/bin/env python3
# coding: utf-8
# Copyright 2023 Abram Hindle, Courtenay Laing-Kobe, https://github.com/tywtyw2002, and https://github.com/treedust
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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        parse = urllib.parse.urlparse(url)
        test = parse.netloc.split(":")
        if len(test) > 1:
            return (test[0], int(test[1]))
        data = socket.getaddrinfo(parse.netloc, 80)
        (host, port) = data[-1][-1]
        return (host, port)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return None

    def get_headers(self, command, url, args=None):
        parse = urllib.parse.urlparse(url)
        hostname = parse.netloc
        path = parse.path
        end = "\r\n"
        headers = command + " " + path + " HTTP/1.1" + end
        headers += "Host: " + hostname + end
        headers += "Accept: */*" + end
        headers += "User-Agent: IAmCourtenaysClient1.0" + end
        if args != None:
            headers += "Content-Length: " + str(len(args)) + end
        headers += end

        return headers

    def read_response(self, data):
        code = int(data.split(" ", maxsplit=2)[1])
        body = data.split("\r\n\r\n")[1]
        return (code, body)
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        (host, port) = self.get_host_port(url)
        self.connect(host, port)
        request = self.get_headers("GET", url)
        print(request)
        self.sendall(request)
        returned = self.recvall(self.socket)
        self.close()
        print(returned)

        (code, body) = self.read_response(returned)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        (host, port) = self.get_host_port(url)
        self.connect(host, port)
        if args == None:
            new_args = ""
        else:
            new_args = urllib.parse.urlencode(args)
            print("\n ARGS:" + new_args +"\n")
        request = self.get_headers("POST", url, new_args) + new_args
        print(request)
        self.sendall(request)
        returned = self.recvall(self.socket)
        self.close()
        print(returned)

        (code, body) = self.read_response(returned)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
