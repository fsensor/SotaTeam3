#!/usr/bin/python

import os
import sys
import struct
import argparse
import datetime
import hashlib
from subprocess import Popen
from subprocess import PIPE

tmp_current_imgfile_name = "sample_data_file"

current_imgfile_name = "sample_data_file.signed"
keyfile_name = "test.key" 
cerfile_name = ''

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

  f = open(img_name, 'rb')
  f.seek(0, 2)
  imgfile_size = f.tell()
  f.seek(0);
  img_data = f.read(imgfile_size)
  f.close()
  # hash boot image
 
  img_hash = hashlib.sha256(img_data).digest()
  # sign with private RSA key
  p = Popen(["openssl", "rsautl", "-sign", "-inkey", keyfile_name], stdin = PIPE, stdout = PIPE)
  rsa_sign = p.communicate(img_hash)[0]
  # write signed boot image

  tmp = img_name + '.signed'
  f = open(tmp, 'wb')
  f.write(img_data)
  f.write(rsa_sign)
  f.close()
  print "end signe_image"
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
  f = open(current_imgfile_name, 'rb')
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
  f.close()

#----------------------------------------------------------------------------
# firmware_update SCRIPT BEGIN
#----------------------------------------------------------------------------

def firmware_update():
  global server_file_name_signed
  global current_imgfile_name
  print "verify"
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
  sign_image(server_file_name)
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
