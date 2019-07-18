#!/usr/bin/python

import os
import sys
import struct
import argparse
import datetime
import hashlib

import ssl
import socket
from urllib.request import urlopen
from urllib.request import HTTPError
import json,ast,base64
import http.server
import threading

from subprocess import Popen
from subprocess import PIPE
from OpenSSL import crypto
from Crypto.Hash import SHA256
import time
import binascii

server_url="https://192.168.0.10:33341/"
#server_url="https://localhost:33341/"
#master_addr="178.5.1.1"
master_addr="192.168.0.4"
tmp_current_imgfile_name = "sample_data_file"
current_imgfile_name = "img.signed"
version_file_name = "version.signed"

key_dir = "../keys/"
keyfile_name = key_dir+"./SigningServer/SignPriv.pem"
cerfile_name = key_dir+"./SigningServer/SignCert.pem"
master_cerfile_name = key_dir+'./Mastercert/MasterCert.pem'
master_keyfile_name = key_dir+'./Mastercert/MasterPriv.pem'
master_chain_name = key_dir+'./Mastercert/MasterChain.pem'
server_cerfile_name = key_dir+'ServerCert/ServerCert.pem'
server_keyfile_name = key_dir+'ServerCert/ServerPriv.pem'
server_chain_name = key_dir+'ServerCert/ServerChain.pem'
slave1_cerfile_name = key_dir+'./Slave1Cert/Slave1Cert.pem'
slave1_keyfile_name = key_dir+'./Slave1Cert/Slave1Priv.pem'
slave1_chain_name = key_dir+'./Slave1Cert/Slave1Chain.pem'
slave2_cerfile_name = key_dir+'./Slave2Cert/Slave2Cert.pem'
slave2_keyfile_name = key_dir+'./Slave2Cert/Slave2Priv.pem'
slave2_chain_name = key_dir+'./Slave2Cert/Slave2Chain.pem'

#server data
server_version = 0
server_file_name = "sample_data_file_server"
server_file_name_signed = "update_img.signed"
#image structure
current_magic = ''
current_version = '0'
current_body_len = 0
current_body = ''
current_sig = ''

LGE_METADATA_HDR_MAGIC  = '\x4C\x47\x45\x31' # 'LGE!'
LGE_SHA256_SIZE   = 32
LGE_RSASIGN_SIZE  = 512

#----------------------------------------------------------------------------
# Sign boot image
#----------------------------------------------------------------------------
def sign_image(img_name):
  # read image file
  print ("sign_image")

  with open(img_name, 'rb') as f:
      f.seek(0, 2)
      imgfile_size = f.tell()
      f.seek(0)
      img_data = f.read(imgfile_size)
      f.close()

  # sign with private RSA key
  with open(keyfile_name, 'rb+') as f:
      pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())

  rsa_sign = crypto.sign(pkey, img_data, 'sha256')

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
  try:
    with open(current_imgfile_name, 'rb') as f:
        f.seek(0, 2)
        imgfile_size = f.tell()  
        f.seek(0)
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
        f.close()

    current_version = current_version[0]
    os.system('cat ' + current_imgfile_name)

    return True
  except:
    return False

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
  print ("firmware update")
  print (cerfile_name) 
  with open(cerfile_name, 'rb+') as f:
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
    f.close()
  print(server_file_name_signed)

  with open(server_file_name_signed, 'rb+') as f:
  #with open("msg.bin.signed", 'rb+') as f:
    f.seek(0,2)
    img_len = f.tell()
    f.seek(0)
    if img_len <= LGE_RSASIGN_SIZE:
      print("update image file too short! ", img_len, "bytes")
      return False
    msg = f.read(img_len-LGE_RSASIGN_SIZE)
    sig = f.read(LGE_RSASIGN_SIZE)
    f.close()
#      dgst = SHA256.new(str(msg).encode('utf-8')).digest()
    print("sig: ", sig)
#      print("msg: ", msg)
#  with open("./sig.bin", 'wb') as f:
#      f.write(sig)

#  with open("./msg.bin", 'wb') as f:
#      f.write(msg)

#  with open(keyfile_name, 'rb+') as f:
#      pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())

#  with open("./sig_py.bin", 'wb+') as f:
#      sig_py = crypto.sign(pkey, msg, 'sha256')
#      f.write(sig_py)

  if (verify_signature(cert, sig, msg)):
      print ("verify ok")
  else:
      print ("verify ng")
      return False
  print ("change")

  os.remove(current_imgfile_name)
  os.rename(server_file_name_signed, current_imgfile_name)
  print("end firmware update")
  return read_current_image()

def read_local_image():
    print("read local image")
    with open("./lufei.signed", 'rb') as f:
        new = f.read()
    with open(server_file_name_signed, 'wb') as f:
        f.write(new)
#----------------------------------------------------------------------------
# image_down SCRIPT BEGIN
#----------------------------------------------------------------------------

def image_down():
  print ("image_down")
  global server_file_name_signed
  try:
    server_file_response = https_connection(server_url, "GetLatestImage")
    if server_file_response is False:
      return False
    content = json.loads(server_file_response)
    content = base64.b64decode(content)
#  print("content: ", content)
    f = open(server_file_name_signed, "wb") #sample_data_file_server.signed
    f.write(content)
    f.close()
    return True
  except:
    print("image down fail")
    return False
#does it need to error handling?

#----------------------------------------------------------------------------
# GET VERSION INFO
#----------------------------------------------------------------------------

def get_version_to_server():
  global server_version

  server_file_response = https_connection(server_url, "GetVersion")
  if server_file_response is False:
      return False
  content = json.loads(server_file_response)
  server_version = (int(content['version'].replace(".","")))
  print("get version: ", server_version)
  sig_bin = binascii.unhexlify(content['sign'])

  with open(server_cerfile_name, 'rb+') as f:
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

  if (verify_signature(cert, sig_bin, content['version'])):
      with open(version_file_name, "w") as f:
          f.write(server_file_response)
      print ("verify ok")
      return True
  else:
      server_version = 0
      print ("verify ng")
      return False

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
  try:
      response = urlopen(url+data, context=context)
  except HTTPError as e:
      print(e)
      return False
  except:
      print('network error')
      return False
  byte_data = response.read()
  text_data = byte_data.decode('utf-8')
  return text_data

#----------------------------------------------------------------------------
# Slave CONNECTION
#----------------------------------------------------------------------------

def slave1_connection():
  global master_addr
  httpsd = http.server.HTTPServer((master_addr, 33341), http.server.SimpleHTTPRequestHandler)
  httpsd.socket = ssl.wrap_socket (httpsd.socket, cert_reqs=ssl.CERT_REQUIRED, ca_certs=slave1_chain_name, certfile=master_cerfile_name, keyfile=master_keyfile_name, server_side=True)
  thread = threading.Thread(target = httpsd.serve_forever)
  thread.daemon = True

  try:
    thread.start()
    print ("slave1 connection thread start")
  except:
    print ("slave1 connection thread error")
    httpsd.shutdown()
    sys.exit()

#----------------------------------------------------------------------------
# Slave CONNECTION
#----------------------------------------------------------------------------

def slave2_connection():
  global master_addr
  httpsd = http.server.HTTPServer((master_addr, 33342), http.server.SimpleHTTPRequestHandler)
  httpsd.socket = ssl.wrap_socket (httpsd.socket, cert_reqs=ssl.CERT_REQUIRED, ca_certs=slave2_chain_name, certfile=master_cerfile_name, keyfile=master_keyfile_name, server_side=True)
  thread = threading.Thread(target = httpsd.serve_forever)
  thread.daemon = True

  try:
    thread.start()
    print ("slave2 connection thread start")
  except:
    print ("slave2 connection thread error")
    httpsd.shutdown()
    sys.exit()

#----------------------------------------------------------------------------
# MAIN SCRIPT BEGIN
#----------------------------------------------------------------------------

def main():
  global current_version
  global server_version
  ret = False
  ret = read_current_image()
  if ret == False:
    print("no such file")
  slave1_connection()
  while True:
    time.sleep(5)
    print ("i'm alive")
    ret = get_version_to_server()
    if ret == False:
      print ("connection failed")
      continue
    print ("server version ",  server_version)
    print ("current version ", current_version)
    if int(server_version) > int(current_version):
      ret = image_down()
      if ret == False:
        continue
      #sign_image("./msg.bin")
#      read_local_image()
      ret = firmware_update()
      if ret == False:
        continue
    else :
      continue
    if ret == True:
      print ("change current version")
      current_version = server_version
      server_version = 0
      print ("server version ", server_version)
      print ("current version ", current_version)
    else : 
      continue
  sys.exit()

if __name__ == "__main__":
    main()

#----------------------------------------------------------------------------
# MAIN SCRIPT END
#----------------------------------------------------------------------------
