#!/usr/bin/python

import os
import sys
import struct
import argparse
import datetime
import hashlib

import ssl
import socket
import urllib2

from subprocess import Popen
from subprocess import PIPE
from OpenSSL import crypto
from Crypto.Hash import SHA256
import time
url="https://localhost/"
tmp_current_imgfile_name = "sample_data_file"

current_imgfile_name = "sample_data_file.signed"
keyfile_name = "test.key" 
cerfile_name = 'test.crt'

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
  print "sign_image"

  with open(img_name, 'rb') as f:
      f.seek(0, 2)
      imgfile_size = f.tell()
      f.seek(0);
      img_data = f.read(imgfile_size)

  img_hash = SHA256.new(img_data.encode('utf-8')).digest()

  # sign with private RSA key
  with open(keyfile_name, 'rb+') as f:
      pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())

  rsa_sign = crypto.sign(pkey, img_hash, 'sha256')

  # write signed boot image
  tmp = img_name + '.signed'
  with open(tmp, 'wb') as f:
      f.write(img_data)
      f.write(rsa_sign)
  print "end sign_image"
  return True

def read_current_image():
  global current_magic 
  global current_version
  global current_body_len
  global current_body 
  global current_sig 
  global current_imgfile_name

  print "read_current_image"
  print current_imgfile_name
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

  print current_magic
  print current_version[0]
  current_version = current_version[0]
  print current_body_len[0]
  print current_body
  print len(current_sig)
  print type(current_sig)
  print current_sig.encode("hex")
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
  print "verify"
  
  with open(cerfile_name, 'rb+') as f:
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
    f.close()
  with open(server_file_name_signed, 'rb+') as f:
      f.seek(0,2)
      img_len = f.tell()
      f.seek(0)
      msg = f.read(img_len-LGE_RSASIGN_SIZE)
      sig = f.read(LGE_RSASIGN_SIZE)
      dgst = SHA256.new(msg.encode('utf-8')).digest()
      f.close()
  if (verify_signature(cert, sig, dgst)):
      print "verify ok"
  else:
      print "verify ng"
      return False
  print "change"

  os.remove(current_imgfile_name)
  os.rename(server_file_name_signed, current_imgfile_name)
  return True

#----------------------------------------------------------------------------
# image_down SCRIPT BEGIN
#----------------------------------------------------------------------------

def image_down():
  print "image_down"
  global server_file_name_signed
#temp code, Local data needs to be changed to server data.
  server_file_response = https_connection(url, server_file_name)
  content = server_file_response.read();
  f = open(server_file_name_signed, "w") #sample_data_file_server.signed
  f.write(content)
  f.close()
#does it need to error handling?

#----------------------------------------------------------------------------
# HTTPS CONNECTION
#----------------------------------------------------------------------------
def https_connection(url, data):
  context = ssl.SSLContext(ssl.PROTOCOL_TLS)
  context.verify_mode = ssl.CERT_REQUIRED
  context.check_hostname = False #This is check for DNSNAME
  context.load_verify_locations(cerfile_name) #certificate file
  print url+data
  response = urllib2.urlopen(url+data, context=context)
  return response

def get_version_to_server():
  global server_version
  server_version = 2
  return True
#----------------------------------------------------------------------------
# MAIN SCRIPT BEGIN
#----------------------------------------------------------------------------

def main():
  global current_version
  global server_version
  global tmp_current_imgfile_name #sample_data_file - no signed
  sign_image(tmp_current_imgfile_name)
  read_current_image()
  while True:
    time.sleep(5)
    print "i'm alive"
    ret = get_version_to_server()
    if ret == False:
      print "connection failed"
      continue
    print "server _version "
    print server_version
    print "currten version "
    print current_version
    if ret == True and server_version > current_version:
      image_down()
      ret = firmware_update()
    else :
      continue
    if ret == True:
      print "change current version"
      current_version = server_version
      server_version = 0
      print "server _version "
      print server_version
      print "currten version "
      print current_version
    else : 
      continue
  sys.exit()

if __name__ == "__main__":
    main()

#----------------------------------------------------------------------------
# MAIN SCRIPT END
#----------------------------------------------------------------------------
