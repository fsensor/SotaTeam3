from OpenSSL import crypto

def verify(cert, sig, msg):
    try:
        print('do verify')
        crypto.verify(cert, sig, msg, "sha256")
        print('done verify')
        return True
    except:
        print('verify func exception')
        return False

with open("sig.bin", 'rb+') as f:
    sig = f.read()
with open("data", 'rb+') as f:
    msg = f.read()
#with open("server.pub", 'rb+') as f:
#with open("client.pub", 'rb+') as f:
#    pub_key = crypto.load_publickey(crypto.FILETYPE_PEM, f.read())
with open("server.crt", 'rb+') as f:
#with open("client.crt", 'rb+') as f:
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

#x509 = crypto.X509()
#x509.set_pubkey(pub_key)

try:
    print('lets try')
#    if (verify(x509, sig, msg)):
    if (verify(cert, sig, msg)):
        print('verify ok')
    else:
        print('verify ng')
except:
    print('main exception')
