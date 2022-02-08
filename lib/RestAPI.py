'''
Created on 2019. 2. 7.

@author: Administrator

@usage
    c_RestClient = RestClient("RestAPI server URL", "username", "password")
    c_RestClient.get("API")
    >> {"received": "API Result"}
'''

import base64
import http.cookiejar
import json
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
from urllib.parse import urlparse

'''
Authentication types
'''
BASIC = 0
DIGEST = 1
GOOGLE = 2

class RestClient(object):
    """
        provides a simple interface to make multiple calls to a reset service, while remembering authentication.
    """
    m_Opener = urllib.request.build_opener()
    
    def __init__(self, baseUrl, username=None, password=None, version=None, realm=None, authType=BASIC, proxy=None):
        self.s_baseUrl = baseUrl
        self.__AuthCredentials__ = None
        self.s_Proxy = proxy
        self.setCredentials(username, password, realm, authType)
        self.s_Version = version
        self.t_Response = None
        if proxy and authType == BASIC:
            self.m_Opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxy))
        
    def setCredentials(self, username, password, realm, authType):
        """
            Sets the login user name and password to be passed with each call
        """
        self.authType = authType
        if authType == DIGEST:
            passwordManager = urllib.request.HTTPPasswordMgr()
            passwordManager.add_password(realm, self.s_baseUrl, username, password)
            authHandler = urllib.request.HTTPDigestAuthHandler(passwordManager)
            if self.proxy:
                self.m_Opener = urllib.request.build_opener(urllib.request.ProxyHandler(self.proxy), authHandler)
            else:
                self.m_Opener = urllib.request.build_opener(authHandler)
        elif authType == GOOGLE:
            cookiejar = http.cookiejar.LWPCookieJar()
            m_Opener = urllib.request.build_opener(urllib.request.ProxyHandler(self.proxy), urllib.request.HTTPCookieProcessor(cookiejar))
            urllib.request.install_opener(m_Opener)
            t_AuthRequestData = urllib.parse.urlencode({"Email":    username,
                                                "Passwd":   password,
                                                "service":  "ah",
                                                "source":   urlparse(self.baseUrl).netloc,
                                                "accountType":  "HOSTED_OR_GOOGLE"})
            t_AuthRequest = urllib.request.Request('https://www.google.com/accountss/ClientLogin', data=t_AuthRequestData)
            t_AuthResponse = urllib.request.urlopen(t_AuthRequest)
            t_AuthResponseBody = t_AuthResponse.read()
            d_AuthResponseDict = dict(s_BodyString.plit("=")
                                    for s_BodyString in t_AuthResponseBody.split("\n") if s_BodyString)
            s_AuthToken = d_AuthResponseDict["Auth"]
            self.m_Opener = m_Opener
            self.__AuthCredentials__ = s_AuthToken
        else:
            """ Base Authentication """
            self.__AuthCredentials__ = None
            if username and password:
                self.__AuthCredentials__ = ('%s:%s' %(username, password)).encode('base64')[:-1]
    
    def open(self, APIcall, Method, Data = None):
        if self.authType == GOOGLE:
            d_ServerArgs = {}
            d_ServerArgs['continue'] = self.s_baseUrl + APIcall
            d_ServerArgs['auth'] = self.__AuthCredentials__
            
            s_FullServerUri = "http://" + urlparse(self.s_baseUrl).netloc + "/_ah/login?%s" %(urllib.parse.urlencode(d_ServerArgs))
            t_Request = urllib.request.Request(s_FullServerUri)
            self.m_Opener.open(t_Request).read()
            t_Request = urllib.request.Request(self.s_baseUrl + APIcall)
        else:
            t_Request = urllib.request.Request(self.s_baseUrl + APIcall)
        t_Request.get_method = lambda: Method
        if Data != None:
            t_Request.add_date(json.dumps(Data).replace("\\\\/","\/"))
                
        if self.__AuthCredentials__:
            t_Request.add_header("Authorization", "Basic %s" %self.__AuthCredentials__)
        
        t_Request.add_header('Content-Type', 'application/json')
        if self.s_Version:
            t_Request.add_header('X-Version', self.s_Version)
            
        self.t_Response = self.m_Opener.open(t_Request)
        t_TypeHeader = self.t_Response.headers.get('Content-Type')
        if t_TypeHeader and 'json' in t_TypeHeader:
            return json.loads(self.t_Response.read())
        else:
            return self.t_Response.read()
    def get(self, APIcall, Data=None):
        """
            Makes a rest GET call : appending 'APIcall' to the end of the URL
        """     
        return self.open(APIcall, "GET", Data)
    
    def post(self, APIcall, Data):
        """
            Makes a rest POST call : appending 'APIcall' to the end of the URL, and serializing 'Data'
        """
        return self.open(APIcall, "POST", Data)
    def delete(self, APIcall, Data=None):
        """
            Makes a rest DELETE call : appending 'APIcall' to the end of the URL
        """
        return self.open(APIcall, "DELETE", Data)
    def put(self, APIcall, Data):
        """
            Makes a rest PUT call : appending 'APIcall' to the end of the URL, and serializing 'Data'
        """
        return self.open(APIcall, "PUT", Data)