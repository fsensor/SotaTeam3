#!/usr/bin/python

import os
import sys
import struct
import argparse
import datetime
import hashlib

import ssl
from twisted.internet.ssl import TLSVersion
import socket
from urllib.request import urlopen
import json,ast,base64
import http.server
import threading

from subprocess import Popen
from subprocess import PIPE
from OpenSSL import crypto
from Crypto.Hash import SHA256
import time

#server_url="https://192.168.0.14:33341/"
server_url="https://localhost:33341/"
master_addr="192.168.0.4"
tmp_current_imgfile_name = "sample_data_file"

current_imgfile_name = "sample_data_file.signed"
key_dir = "/home/pi/sota/SotaTeam3/keys/"
keyfile_name = key_dir+"./SigningServer/SignPriv.pem"
cerfile_name = key_dir+"./SigningServer/SignPub.pem"
master_cerfile_name = key_dir+'./Mastercert/MasterCert.pem'
master_keyfile_name = key_dir+'./Mastercert/MasterPriv.pem'
master_chain_name = key_dir+'./Mastercert/MasterChain.pem'
server_cerfile_name = key_dir+'ServerCert/ServerCert.pem'
server_keyfile_name = key_dir+'ServerCert/ServerPriv.pem'
server_chain_name = key_dir+'ServerCert/ServerChain.pem'
slave1_cerfile_name = key_dir+'./Slave1Cert/Slave1Cert.pem'
slave1_keyfile_name = key_dir+'./Slave1Cert/Slave1Priv.pem'
slave1_chain_name = key_dir+'./Slave1Cert/SlaveChain.pem'
slave2_cerfile_name = key_dir+'./Slave2Cert/Slave2Cert.pem'
slave2_keyfile_name = key_dir+'./Slave2Cert/Slave2Priv.pem'
slave2_chain_name = key_dir+'./Slave2Cert/Slave2Chain.pem'

#server data
server_version = 0
server_file_name = "sample_data_file_server"
server_file_name_signed = "sample_data_file_server.signed"
#image structure
current_magic = ''
current_version = 0
current_body_len = 0
current_body = ''
current_sig = ''

LGE_METADATA_HDR_MAGIC  = '\x4C\x47\x45\x31' # 'LGE!'
LGE_SHA256_SIZE   = 32
LGE_RSASIGN_SIZE  = 256

#----------------------------------------------------------------------------
# Sign boot image
#----------------------------------------------------------------------------
def sign_image(img_name):
  # read image file
  print (sign_image)

  with open(img_name, 'rb') as f:
      f.seek(0, 2)
      imgfile_size = f.tell()
      f.seek(0);
      img_data = f.read(imgfile_size)

  img_hash = SHA256.new(str(img_data).encode('utf-8')).digest()

  # sign with private RSA key
  with open(keyfile_name, 'rb+') as f:
      pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())

  rsa_sign = crypto.sign(pkey, img_hash, 'sha256')

  # write signed boot image
  tmp = img_name + '.signed'
  with open(tmp, 'wb') as f:
      f.write(img_data)
      f.write(rsa_sign)
  print ("end sign_image")
  return True

def read_current_image():
  global current_magic 
  global current_version
  global current_body_len
  global current_body 
  global current_sig 
  global current_imgfile_name

  print ("read_current_image")
  print (current_imgfile_name)
  with open(current_imgfile_name, 'rb') as f:
      f.seek(0, 2)
      imgfile_size = f.tell()  
      f.seek(0);
      img_data = f.read(imgfile_size)
      f.seek(0)
      current_magic = f.read(4)
      tmp = f.read(4)
      current_version = struct.unpack('i', tmp)
      tmp = f.read(4)
      current_body_len = struct.unpack('i', tmp)
      current_body = f.read(current_body_len[0])
      f.seek(imgfile_size-LGE_RSASIGN_SIZE)
      current_sig = f.read(LGE_RSASIGN_SIZE)

  print (current_magic)
  print (current_version[0])
  current_version = current_version[0]
  print (current_body_len[0])
  print (current_body)
  print (len(current_sig))
  print (type(current_sig))
  print (current_sig.hex())
#sig = f.read(imgfile_size-)

def verify_signature(cert, sig, dgst):
    try:
        print('do verify')
        crypto.verify(cert, sig, dgst, "sha256")
        print('done verify')
        return True
    except:
        print('verify func exception')
        return False

#----------------------------------------------------------------------------
# firmware_update SCRIPT BEGIN
#----------------------------------------------------------------------------

def firmware_update():
  global server_file_name_signed
  global current_imgfile_name
  print ("verify")
  
  with open(cerfile_name, 'rb+') as f:
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
    f.close()
  with open(server_file_name_signed, 'rb+') as f:
      f.seek(0,2)
      img_len = f.tell()
      f.seek(0)
      msg = f.read(img_len-LGE_RSASIGN_SIZE)
      sig = f.read(LGE_RSASIGN_SIZE)
      dgst = SHA256.new(str(msg).encode('utf-8')).digest()
      f.close()
  if (verify_signature(cert, sig, dgst)):
      print ("verify ok")
  else:
      print ("verify ng")
      return False
  print ("change")

  os.remove(current_imgfile_name)
  os.rename(server_file_name_signed, current_imgfile_name)
  return True

#----------------------------------------------------------------------------
# image_down SCRIPT BEGIN
#----------------------------------------------------------------------------

def image_down():
  print ("image_down")
  global server_file_name_signed
  server_file_response = https_connection(server_url, "GetLatestImage")
  content = base64.b64decode(server_file_response.read())
  f = open(server_file_name_signed, "w") #sample_data_file_server.signed
  f.write(str(content))
  f.close()
#does it need to error handling?

#----------------------------------------------------------------------------
# GET VERSION INFO
#----------------------------------------------------------------------------

def get_version_to_server():
  global server_version

  server_file_response = https_connection(server_url, "GetVersion")
  content = json.load(server_file_response)
  content = ast.literal_eval(content)
  server_version_info = content['version_info'][0]
  server_version = server_version_info.get('version')
  return True

#----------------------------------------------------------------------------
# HTTPS CONNECTION
#----------------------------------------------------------------------------

def https_connection(url, data):
  context = ssl.SSLContext(ssl.PROTOCOL_TLS)
  context.verify_mode = ssl.CERT_REQUIRED
  context.check_hostname = False #This is check for DNSNAME
  context.load_verify_locations(server_chain_name) #certificate file
  context.load_cert_chain(certfile=master_cerfile_name, keyfile=master_keyfile_name)
  print (url+data)
  response = urlopen(url+data, context=context)
  return response

#----------------------------------------------------------------------------
# Slave CONNECTION
#----------------------------------------------------------------------------

def slave_connection():
  global master_addr
  httpsd = http.server.HTTPServer((master_addr, 33341), http.server.SimpleHTTPRequestHandler)
  httpsd.socket = ssl.wrap_socket (httpsd.socket, certfile=master_cerfile_name, keyfile=master_keyfile_name, server_side=True)
  thread = threading.Thread(target = httpsd.serve_forever)
  thread.daemon = True

  try:
    thread.start()
    print ("slave connection thread start")
  except:
    print ("slave connection thread error")
    httpsd.shutdown()
    sys.exit()

#----------------------------------------------------------------------------
# MAIN SCRIPT BEGIN
#----------------------------------------------------------------------------

def main():
  global current_version
  global server_version
  global tmp_current_imgfile_name #sample_data_file - no signed
  sign_image(tmp_current_imgfile_name)
  read_current_image()
  slave_connection()
  while True:
    time.sleep(5)
    print ("i'm alive")
    ret = get_version_to_server()
    if ret == False:
      print ("connection failed")
      continue
    print ("server version ")
    print (server_version)
    print ("current version ")
    print (current_version)
    if ret == True and server_version > current_version:
      image_down()
      ret = firmware_update()
    else :
      continue
    if ret == True:
      print ("change current version")
      current_version = server_version
      server_version = 0
      print ("server version ")
      print (server_version)
      print ("current version ")
      print (current_version)
    else : 
      continue
  sys.exit()

if __name__ == "__main__":
    main()

#----------------------------------------------------------------------------
# MAIN SCRIPT END
#----------------------------------------------------------------------------
