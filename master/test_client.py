#!/bin/env python
"""
A simple example of using Python sockets for a client HTTPS connection.
"""

import ssl
import socket
import urllib2
import pprint

url="https://localhost/FILE/image"

context = ssl.SSLContext(ssl.PROTOCOL_TLS)
context.verify_mode = ssl.CERT_REQUIRED
context.check_hostname = False #This is check for DNSNAME
context.load_verify_locations("/home/hyun/11/server.pem") #modify this path

response = urllib2.urlopen(url, context=context)
html = response.read()

print html # contents of url

"""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ssl_sock = context.wrap_socket(s, server_hostname='localhost')
ssl_sock.connect(('localhost', 443))
ssl_sock.sendall("GET / HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
pprint.pprint(ssl_sock.getpeercert())

while True:
    new = ssl_sock.recv(4096)
    if not new:
        ssl_sock.close()
        break
    print new
"""
