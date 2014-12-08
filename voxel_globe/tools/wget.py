import urllib2

from StringIO import StringIO
import zlib

def download(url, filename, chunkSize=2**20, user=None, password=None, realm=None, uri=None):
  #start simple, add feautres as time evolves
  if user and password and realm and uri:
    auth_handler = urllib2.HTTPBasicAuthHandler()
    auth_handler.add_password(realm=realm, uri=uri, user=user, passwd=password)
    opener = urllib2.build_opener(auth_handler)
    urllib2.install_opener(opener)
  
  request = urllib2.Request(url);
  request.add_header('Accept-encoding', 'gzip');
  response = urllib2.urlopen(request);
  if response.info().get('Content-Encoding') == 'gzip':
    gzipped = True;
    decompressor = zlib.decompressobj(16+zlib.MAX_WBITS)
    #Why 16+zlib.MAX_WBITS???
    #http://www.zlib.net/manual.html
    #Basically means gzip for zlib
  else:
    gzipped = False;
  
  with open(filename, 'wb') as output:
    buf = 'do';
    while buf:
      buf = response.read(chunkSize);
      if gzipped:
        output.write(decompressor.decompress(buf))
      else:
        output.write(buf);
