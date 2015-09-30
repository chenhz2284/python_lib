# encoding: utf8
import urllib2


# support for http and https
def post(url, postData=None, headers={}):
    _request = urllib2.Request(url, postData, headers) 
    return urllib2.urlopen(_request).read()
    
    
    
if __name__=="__main__":
    
    print __name__;
    
    url = "http://localhost:8080/op-20141110.1/test/a.jsp";
    headers = {"my_header": "my_header"}
    print post(url, headers=headers)