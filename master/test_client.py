import urllib2, ssl

try: 
    response = urllib2.urlopen('https://localhost', context=ssl._create_unverified_context())
    #response = urllib2.urlopen('https://www.naver.com')
    print 'response headers: "%s"' % response.info() 
except IOError, e: 
    if hasattr(e, 'code'): # HTTPError 
        print 'http error code: ', e.code 
    elif hasattr(e, 'reason'): # URLError 
        print "can't connect, reason: ", e.reason 
    else: 
        raise
