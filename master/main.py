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

url="https://localhost/"
tmp_current_imgfile_name = "sample_data_file"

current_imgfile_name = "sample_data_file.signed"
keyfile_name = "test.key" 
cerfile_name = 'test.crt'

#server data
server_version = 2
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

  # hash boot image
  # img_hash = hashlib.sha256(img_data).digest()
  img_hash = SHA256.new(img_data.encode('utf-8')).digest()

  # sign with private RSA key
  #p = Popen(["openssl", "rsautl", "-sign", "-inkey", keyfile_name], stdin = PIPE, stdout = PIPE)
  #rsa_sign = p.communicate(img_hash)[0]
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
  print current_body_len[0]
#  body_len2 = (int)body_len
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

  with open(server_file_name_signed, 'rb+') as f:
      f.seek(0,2)
      img_len = f.tell()
      f.seek(0)
      msg = f.read(img_len-LGE_RSASIGN_SIZE)
      sig = f.read(LGE_RSASIGN_SIZE)
      dgst = SHA256.new(msg.encode('utf-8')).digest()

  if (verify_signature(cert, sig, dgst)):
      print "verify ok"
  else:
      print "verify ng"
  print "change"

  os.remove(current_imgfile_name)
  os.rename(server_file_name_signed, current_imgfile_name)


#----------------------------------------------------------------------------
# image_down SCRIPT BEGIN
#----------------------------------------------------------------------------

def image_down():
  print "image_down"
  global server_file_name
  global server_file_name_signed
#temp code, Local data needs to be changed to server data.
#  sign_image(server_file_name)
  server_file_response = https_connection(url, "sample_data_file.signed")
  content = server_file_response.read();
  f = open("test/"+server_file_name_signed, "w")
  f.write(content)
  f.close()
  server_file_name_signed = "test/"+server_file_name_signed

#end temp code
  firmware_update()
#----------------------------------------------------------------------------
# COMPARE SCRIPT BEGIN
#----------------------------------------------------------------------------

def compare_version():
  global current_version
  global server_version
  print "compare_version"
  print server_version
  print current_version
  if server_version > current_version[0]:
    image_down()
  else :
   return True

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

#----------------------------------------------------------------------------
# MAIN SCRIPT BEGIN
#----------------------------------------------------------------------------

def main():
  global tmp_current_imgfile_name
  sign_image(tmp_current_imgfile_name)

  read_current_image()
  compare_version()
  sys.exit()

if __name__ == "__main__":
    main()

#----------------------------------------------------------------------------
# MAIN SCRIPT END
#----------------------------------------------------------------------------
