# taken from http://www.piware.de/2011/01/creating-an-https-server-in-python/
# generate server.xml with the following command:
#    openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
# run as follows:
#    python simple-https-server.py
# then in your browser, visit:
#    https://localhost:4443

import http.server
import ssl

key_dir = "/home/pi/sota/SotaTeam3/keys/"
master_cerfile_name = key_dir+'Mastercert/MasterCert.pem'
master_keyfile_name = key_dir+'Mastercert/MasterPriv.pem'
master_chain_name = key_dir+'Mastercert/MasterChain.pem'
server_cerfile_name = key_dir+'ServerCert/ServerCert.pem'
server_keyfile_name = key_dir+'ServerCert/ServerPriv.pem'
server_chain_name = key_dir+'ServerCert/ServerChain.pem'


httpd = http.server.HTTPServer(('localhost', 33341), http.server.SimpleHTTPRequestHandler)
#httpd.socket = ssl.wrap_socket (httpd.socket, certfile='/home/pi/python_test/server.pem', server_side=True)
httpd.socket = ssl.wrap_socket (httpd.socket, cert_reqs=ssl.CERT_REQUIRED, ca_certs=master_chain_name, certfile=server_cerfile_name, keyfile=server_keyfile_name, server_side=True)
httpd.serve_forever()
