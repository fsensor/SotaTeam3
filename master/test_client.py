import urllib2
from OpenSSL import SSL
try: 
    #response = urllib2.urlopen('https://localhost')
    response = urllib2.urlopen('https://www.naver.com')
    print 'response headers: "%s"' % response.info() 
except IOError, e: 
    if hasattr(e, 'code'): # HTTPError 
        print 'http error code: ', e.code 
    elif hasattr(e, 'reason'): # URLError 
        print "can't connect, reason: ", e.reason 
    else: 
        raise
