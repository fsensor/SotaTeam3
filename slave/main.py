#!/usr/bin/python

import os
import sys
import struct
import argparse
import datetime
import hashlib
import binascii
import ssl
import socket

import json,ast,base64
import http.server
import threading
from urllib.request import urlopen
from subprocess import Popen
from subprocess import PIPE
from OpenSSL import crypto
from Crypto.Hash import SHA256
import time
server_url="https://192.168.0.4:33341/"
master_addr="192.168.0.4"
tmp_current_imgfile_name = "sample_data_file"

current_imgfile_name = "sample_data_file.signed"
version_file_name = "version.signed"

key_dir = "/home/pi/sota/SotaTeam3_0718/keys/"
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
slave1_chain_name = key_dir+'./Slave1Cert/SlaveChain.pem'
slave2_cerfile_name = key_dir+'./Slave2Cert/Slave2Cert.pem'
slave2_keyfile_name = key_dir+'./Slave2Cert/Slave2Priv.pem'
slave2_chain_name = key_dir+'./Slave2Cert/Slave2Chain.pem'

#server data
server_version = 0
version_sig = ''

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
LGE_RSASIGN_SIZE  = 512

#----------------------------------------------------------------------------
# Sign image
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
  print(rsa_sign)
  # write signed boot image
  with open(server_file_name_signed, 'wb') as f:
      f.write(img_data)
      f.write(rsa_sign)
      f.close()
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
#    print (current_magic)
#    print (current_version)
#    print (current_body_len[0])
#    print (current_body)
#    print (len(current_sig))
#    print (current_sig.hex())
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
      print(msg)

      dgst = SHA256.new(str(msg).encode('utf-8')).digest()
      f.close()
  if (verify_signature(cert, sig, msg)):
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
  global server_file_name
#temp code, Local data needs to be changed to server data.
  print(server_file_name)
  print(server_file_name_signed)
  try:
    server_file_response = https_connection(server_url, server_file_name)
    content = server_file_response.read()
    f = open(server_file_name_signed, "wb") #sample_data_file_server.signed
    f.write(content)
    f.close()
    return True
  except:
    print("image down fail")
    return False
#does it need to error handling?

#----------------------------------------------------------------------------
# VERSION Verify
#----------------------------------------------------------------------------
def version_verify():
  global version_file_name
  global server_version
  j_version = ''
  j_sig = ''
  b_sig = ''

  print ("version_verify")
  with open(version_file_name, "r") as json_file:
    json_data = json.load(json_file)
    j_version = json_data["version"]
    j_sig = json_data["sign"]
    json_file.close()

  b_sig = (binascii.unhexlify(j_sig))

  with open(server_cerfile_name,'rb+') as f:
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())
    f.close()
  if verify_signature(cert, b_sig, j_version)is False :
      return False
  else :
      server_version =  (int(j_version.replace(".","")))
      return True
  
#----------------------------------------------------------------------------
# GET VERSION INFO
#----------------------------------------------------------------------------

def get_version_to_master():
  global server_version
  try:
    server_file_response = https_connection(server_url, version_file_name)
    content = server_file_response.read()
    with open(version_file_name, "wb") as f:
      f.write(content)
    f.close()
    return True
  except : 
    print("get_version_download_fail")
    return False

#----------------------------------------------------------------------------
# HTTPS CONNECTION
#----------------------------------------------------------------------------

def https_connection(url, data):
  context = ssl.SSLContext(ssl.PROTOCOL_TLS)
  context.verify_mode = ssl.CERT_REQUIRED
  context.check_hostname = False #This is check for DNSNAME
  context.load_verify_locations(server_chain_name) #certificate file
  context.load_cert_chain(certfile=slave1_cerfile_name, keyfile=slave1_keyfile_name)
  print (url+data)
  response = urlopen(url+data, context=context)
  return response

#----------------------------------------------------------------------------
# MAIN SCRIPT BEGIN
#----------------------------------------------------------------------------

def main():
  global current_version
  global server_version
  global tmp_current_imgfile_name #sample_data_file - no signed
  sign_image("sample_data_file_server_nosigned")
  ret = False
  ret = read_current_image()
  if ret == False:
    print("no such file")
  while True:
    time.sleep(5)
    print ("i'm alive")
    ret = get_version_to_master()
    if ret == False:
      print ("connection failed")
      continue
    ret = version_verify()
    if ret == False:
      print ("server version verify fail")
      continue
    print ("server version ")
    print (server_version)
    print ("current version ")
    print (current_version)
    server_version = 2
    if server_version > current_version:
      ret = image_down()
      if ret == False:
        continue
      ret = firmware_update()
      if ret == False:
        continue
      else :
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
