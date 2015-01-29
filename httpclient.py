#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
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
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        if not port:
                port =80
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as msg:
            print 'Error code' + str(msg[0])+'Error message'+str(msg[1])
            sys.exit()   
        s.connect((host,port))
        return s
    def get_code(self, data):
        code = data.split(' ')
        return int(code[1])

    def get_headers(self,data):
        dataList = data.split("\r\n\r\n")
        header = dataList[0]
        return header

    def get_body(self, data):
        body =data.split('\r\n\r\n')
        return body[1]

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
    
    #send message and get reply, then return the reply back
    def send(self, host, port, msg):
        sock = self.connect(host,port) 
        try:
            sock.sendall(msg.encode("UTF-8"))
        except socket.error:
            #Send failed
            print 'Send failed'
            sys.exit()
        getReply = self.recvall(sock)
        code = self.get_code(getReply)
        body = self.get_body(getReply)
        sock.close()
        return code,body
    
    def GET(self, url, args=None):
        getUrl = urlparse(url)
        msg = "GET "+getUrl.path+" HTTP/1.1\r\nHost: "
        msg += getUrl.hostname+"\r\nAccept: */*\r\n"
        msg +="Connection: close\r\n\r\n"
        code,body = self.send(getUrl.hostname, getUrl.port, msg)
        
        return HTTPRequest(code, body)
    
    def POST(self, url, args=None):
        postUrl = urlparse(url)
        if args is not None:
            content = urllib.urlencode(args)
        else:
            content = ""               
        msg = "POST "+postUrl.path
        msg +=" HTTP/1.1\r\nHost: "+postUrl.hostname+"\r\n"
        msg +="Accept: */*\r\n"
        msg +="Content-Type: application/x-www-form-urlencoded\r\n"
        msg +="Content-Length: "+str(len(content))
        msg +="\r\n\r\n"+content+"\r\n" 
        code,body = self.send(postUrl.hostname, postUrl.port, msg)
        return HTTPRequest(code, body)

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
        print ( command, sys.argv[1] )    
