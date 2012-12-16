# -*- coding: utf-8 -*-
import cookielib, os, string, StringIO
import os, time, base64, logging, calendar
import urllib, urllib2, re, sys, math
import xbmcaddon, xbmc, simplejson

scriptID = 'plugin.video.polishtv.live'
scriptname = "Polish Live TV"
ptv = xbmcaddon.Addon(scriptID)

import pLog, xppod, Parser, settings, pCommon

log = pLog.pLog()
sets = settings.TVSettings()

DEBUG = True
HOST = 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.18) Gecko/20110621 Mandriva Linux/1.9.2.18-0.1mdv2010.2 (2010.2) Firefox/3.6.18'

chars_table = {
  'f': 'A',
  'F': 'a',
  'a': 'F',
  'A': 'f',
  'k': 'B',
  'K': 'b',
  'b': 'K',
  'B': 'k',
  'm': 'I',
  'M': 'i',
  'i': 'M',
  'I': 'm',
  'D': 'x',
  'x': 'D',
  'O': 'y',
  'y': 'O',
  'C': 'z',
  'z': 'C'
}


class urlparser:
  def __init__(self):
    self.cm = pCommon.common()
    pass

  def replaceChars(self, char):
      out_char = char
      for char_in, char_out in chars_table.items():
          if char == char_in:
              out_char = char_out
              break
      return out_char  


  def createString(self, string):
      string_in_tab = list(string)
      string_out_tab = []
      string_out = string
      for i in range(len(string_in_tab)):
          string_out_tab.append(self.replaceChars(string_in_tab[i]))
      for a in range(len(string_out_tab)):
          if a == 0:
              string_out = string_out_tab[a]
          else:
              string_out += string_out_tab[a]
      return string_out


  def getHostName(self, url, nameOnly = False):
    hostName = ''       
    match = re.search('http://(.+?)/',url)
    if match:
      hostName = match.group(1)
      
      if (nameOnly):
	n = hostName.split('.')
	hostName = n[-2]
    return hostName


  def requestData(self, url, postdata = {}):
	req = urllib2.Request(url)
	req.add_header('User-Agent', HOST)
	response = urllib2.urlopen(req)
	data = response.read()
	response.close()	
	return data


  def getVideoLink(self, url):
    nUrl=''
    host = self.getHostName(url)
    log.info("video hosted by: " + host)

    if host == 'www.putlocker.com':
        nUrl = self.parserPUTLOCKER(url)
    if host == 'www.sockshare.com':
        nUrl = self.parserSOCKSHARE(url)
    if host == 'megustavid.com':
        nUrl = self.parserMEGUSTAVID(url)
    #if host == 'hd3d.cc':
    #    nUrl = self.parserHD3D(url)
    if host == 'sprocked.com':
        nUrl = self.parserSPROCKED(url)
    if host == 'odsiebie.pl':
        nUrl = self.parserODSIEBIE(url) 
    if host == 'www.wgrane.pl':
        nUrl = self.parserWGRANE(url)
    if host == 'www.cda.pl':
        nUrl = self.parserCDA(url)
    if host == 'maxvideo.pl':
        nUrl = self.parserMAXVIDEO(url)
    if host == 'nextvideo.pl':
        nUrl = self.parserNEXTVIDEO(url)
    if host == 'video.anyfiles.pl':
        nUrl = self.parserANYFILES(url)
    if host == 'www.videoweed.es' or host == 'www.videoweed.com' or host == 'videoweed.es' or host == 'videoweed.com':
        nUrl = self.parserVIDEOWEED(url)
    if host== 'www.novamov.com':
        nUrl = self.parserNOVAMOV(url)
    if host== 'www.nowvideo.eu':
        nUrl = self.parserNOWVIDEO(url)
	
    return nUrl

#nUrl - "" ; brak obslugi hosta
#nUrl - False ; broken parser, cos sie pewnie zmienilo
#nUrl - "http:...." ; link do streamu


  def parserPUTLOCKER(self,url):
    link = self.requestData(url)    
    r = re.search('value="(.+?)" name="fuck_you"', link)
    if r:
      if DEBUG: log.info("hash: " + r.group(1))
      postdata = {'fuck_you' : r.group(1), 'confirm' : 'Close Ad and Watch as Free User'}
      data = urllib.urlencode(postdata)
      req = urllib2.Request(url,data)
      req.add_header('User-Agent', HOST)
      cj = cookielib.LWPCookieJar()
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
      resp = opener.open(req)
      link = resp.read()
      resp.close()
      match = re.compile("playlist: '(.+?)'").findall(link)
      if len(match) > 0:
        if DEBUG: log.info("get_file.php:" + match[0])
        url = "http://www.putlocker.com" + match[0]
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        resp = opener.open(req)
        link = resp.read()
        resp.close()
        if DEBUG: log.info(link)
        match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
        if len(match) > 0:
          url = match[0].replace('&amp;','&')
          if DEBUG: log.info("final link: " + url)
          return url
        else:
          return False
      else:
        return False
    else:
      return False


  def parserMEGUSTAVID(self,url):
    link = self.requestData(url)    
    match = re.compile('value="config=(.+?)">').findall(link)
    if len(match) > 0:
      p = match[0].split('=')
      url = "http://megustavid.com/media/nuevo/player/playlist.php?id=" + p[1]
      if DEBUG: log.info("newlink: " + url)     
      link = self.requestData(url)      
      if DEBUG: log.info(link)
      match = re.compile('<file>(.+?)</file>').findall(link)
      if len(match) > 0:
        if DEBUG: log.info("final link: " + match[0])
        return match[0]
      else:
        return False
    else: 
      return False


  def parserHD3D(self,url):
    link = self.requestData(url)
    if DEBUG: log.info(link)
    match = re.compile("""url: ["'](.+?)["'],.+?provider:""").findall(link)
    if len(match) > 0:
      if DEBUG: log.info("final link: " + match[0])
      ret = match[0]
    else:
     ret = False
    return ret


  def parserSPROCKED(self,url):
    link = self.requestData(url)
    if DEBUG: log.info(link)
    match = re.search("""url: ['"](.+?)['"],.*\nprovider""",link)
    if match:
      if DEBUG: log.info("final link: " + match.group(1))       
      return match.group(1)
    else: 
      return False


  def parserODSIEBIE(self,url):
    link = self.requestData(url)
    if DEBUG: log.info(link)
    (v_ext, v_file, v_dir, v_port, v_host) = re.search("\|\|.*SWFObject",link).group().split('|')[40:45]
    url = "http://%s.odsiebie.pl:%s/d/%s/%s.%s" % (v_host, v_port, v_dir, v_file, v_ext);
    return url


  def parserWGRANE(self,url):
    hostUrl = 'http://www.wgrane.pl'            
    playlist = hostUrl + '/html/player_hd/xml/playlist.php?file='
    key = url[-32:]
    nUrl = playlist + key
    if DEBUG: log.info("playlist: " + nUrl)
    link = self.requestData(nUrl)
    if DEBUG: log.info(link)
    match = re.search("""<mainvideo url=["'](.+?)["']""",link)
    if match:
      ret = match.group(1).replace('&amp;','&')
      if DEBUG: log.info("final link: " + ret)
      return ret
    else: 
      return False


  def parserCDA(self,url):
    link = self.requestData(url)
    if DEBUG: log.info(link)
    match = re.search("""file: ['"](.+?)['"],""",link)
    if match:
      if DEBUG: log.info("final link: " + match.group(1))       
      return match.group(1)
    else: 
      return False


  def parserNOVAMOV(self,url):
    link = self.requestData(url)
    if DEBUG: log.info(link)
    match = re.search("""file: ['"](.+?)['"],""",link)
    if match:
      if DEBUG: log.info("final link: " + match.group(1))       
      return match.group(1)
    else: 
      return False


  def parserDWN(self,url):
    link = self.requestData(url)
    if DEBUG: log.info(link)
    #<iframe src="http://dwn.so/player/embed.php?v=DS301459CC&width=850&height=440"
    match = re.search("""<iframe src="(.+?)&""",link)
    if match:
      link = self.requestData(match.group(1))
      if DEBUG: log.info(link)  
    else: 
      return False


  def parserANYFILES(self,url):
	hostUrl = 'http://video.anyfiles.pl'
	data = self.requestData(url)
	if DEBUG: log.info(data)
	#var flashvars = {"uid":"player-vid-8552","m":"video","st":"c:1LdwWeVs3kVhWex2PysGP45Ld4abN7s0v4wV"};
	match = re.search("""var flashvars = {.+?"st":"(.+?)"}""",data)
	if match:
		nUrl = xppod.Decode(match.group(1)[2:]).encode('utf-8').strip()
		if 'http://' in nUrl:
			url = nUrl
		else:
			url = hostUrl + nUrl
		data = self.requestData(url)
		data = xppod.Decode(data).encode('utf-8').strip()
		#{"file":"http://50.7.221.26/folder/776713c560821c666da18d8550594050_8552.mp4 or http://50.7.220.66/folder/776713c560821c666da18d8550594050_8552.mp4","ytube":"0",
		match = re.search("""file":"(.+?)","ytube":"(.+?)",""",data)
		if match:
			if 'or' in match.group(1):
				links = match.group(1).split(" or ")
				if DEBUG: log.info("final link: " + links[1])
				return links[1]			
			else:
				if match.group(2)=='1':
				    p = match.group(1).split("/")
				    if 'watch' in p[3]:
					videoid = p[3][8:19]
				    else:	
					videoid = p[3]
				    plugin = 'plugin://plugin.video.youtube/?action=play_video&videoid=' + videoid
				    return plugin
				else:	
				    return match.group(1)
		else:
			return False
	else: 
		return False


  def parserWOOTLY(self,url):
    link = self.requestData(url)
    if DEBUG: log.info(link)
    #c.value="9ee163b21f5b018544e977cf1fe87569231e4816";
    c = re.search("""c.value="(.+?)";""",link)
    #log.info("match: " +str(c.group(1)))
    if c:
      cval = c.group(1)   
    else: 
      return False    
    #<input type="hidden" value="148184646935bc200ed80035c2d16304" class="textbox" name="9ee163b21f5b018544e977cf1fe87569231e4816"
    match = re.compile("""<input type=['"]hidden['"] value=['"](.+?)['"].+?name=['"](.+?)['"]""").findall(link)
    if len(match) > 0:
      postdata = {};
      for i in range(len(match)):
        if (len(match[i][0])) > len(cval):
          postdata[cval] = match[i][1]
        else:
          postdata[match[i][0]] = match[i][1]
      if DEBUG: log.info(str(postdata))
      data = urllib.urlencode(postdata)
      req = urllib2.Request(url,data)
      req.add_header('User-Agent', HOST)
      cj = cookielib.LWPCookieJar()
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
      resp = opener.open(req)
      link = resp.read()
      resp.close()
      if DEBUG: log.info(link)
      #<video src="http://r012.wootly.ch/v/01/d6f5ec9acce1bf5c370fac5cb401fe02c30ee4fc.mp4" 
      match = re.search("""<video.*\n.*src=['"](.+?)['"]""",link)
      #log.info("match: " +str(match.group(1)))
      if match:
        if DEBUG: log.info("final link: " + match.group(1))
        return match.group(1)
      else: 
        return False
    else: 
      return False


  def parserMAXVIDEO(self, url):
      self.servset = sets.getSettings('maxvideo')
      self.cm.checkDir(ptv.getAddonInfo('path') + os.path.sep + "cookies")
      self.COOKIEFILE = ptv.getAddonInfo('path') + os.path.sep + "cookies" + os.path.sep + "maxvideo.cookie" 
      self.cm.saveURLToFileCookieData('http://maxvideo.pl/api/login.php',self.COOKIEFILE, {'login' : self.servset['maxvideo_login'], 'password' : self.servset['maxvideo_password'] })
      videoHash = url.split('/')[-1]
      data = self.cm.postURLFromFileCookieData('http://maxvideo.pl/api/get_link.php',self.COOKIEFILE,{'v' : videoHash})
      
      result = simplejson.loads(data)
      if (result['premium']):
	premium_until = result['premium_until']
	premium_until = premium_until.split(' ')
	notification = '(Zalogowany,Premium maxvideo.pl aktywne do ' + premium_until[0] + ',10000)'
      else:
	notification = '(Niezalogowany, Oplac konto maxvideo.pl by w pelni korzystac z serwisu,30000)'
      xbmc.executebuiltin("XBMC.Notification" + notification +'"')

      videoUrl = result['ok']
      return videoUrl
           
      
  def parserNEXTVIDEO(self, url):
      link = self.requestData(url)
      match = re.compile('file\: "(.+?)",').findall(link)
      if len(match) > 0:
	  if DEBUG: log.info("final link: " + match[0])
          return match[0]
      else:
          return False
      
      
  def parserVIDEOWEED(self, url):
      link = self.requestData(url)
      match_domain = re.compile('flashvars.domain="(.+?)"').findall(link)
      match_file = re.compile('flashvars.file="(.+?)"').findall(link)
      match_filekey = re.compile('flashvars.filekey="(.+?)"').findall(link)
      if len(match_domain) > 0 and len(match_file) > 0 and len(match_filekey) > 0:
          get_api_url = ('%s/api/player.api.php?user=undefined&codes=1&file=%s&pass=undefined&key=%s') % (match_domain[0], match_file[0], match_filekey[0])
	  link_api = self.requestData(get_api_url)
	  if 'url' in link_api:
              parser = Parser.Parser()
              params = parser.getParams(link_api)
              if DEBUG: log.info("final link: " + parser.getParam(params, "url"))
              return parser.getParam(params, "url")
          else:
              return False
      else:
          return False
	
      
  def parserNOVAMOV(self, url):
      link = self.requestData(url)
      match_file = re.compile('flashvars.file="(.+?)";').findall(link)
      match_key = re.compile('flashvars.filekey="(.+?)";').findall(link)
      if len(match_file) > 0 and len(match_key) > 0:
          get_api_url = ('http://www.novamov.com/api/player.api.php?key=%s&user=undefined&codes=1&pass=undefined&file=%s') % (match_key[0], match_file[0])
	  link_api = self.requestData(get_api_url)
          match_url = re.compile('url=(.+?)&title').findall(link_api)
          if len(match_url) > 0:
              return match_url[0]
          else:
              return False

  def parserNOWVIDEO(self, url):
      link = self.requestData(url)
      match_file = re.compile('flashvars.file="(.+?)";').findall(link)
      match_key = re.compile('flashvars.filekey="(.+?)";').findall(link)
      if len(match_file) > 0 and len(match_key) > 0:
          get_api_url = ('http://www.nowvideo.eu/api/player.api.php?codes=1&key=%s&user=undefined&pass=undefined&file=%s') % (match_key[0], match_file[0])
	  link_api = self.requestData(get_api_url)
          match_url = re.compile('url=(.+?)&title').findall(link_api)
          if len(match_url) > 0:
              return match_url[0]
          else:
              return False


  def parserSOCKSHARE(self,url):
    link = self.requestData(url)    
    r = re.search('value="(.+?)" name="fuck_you"', link)
    if r:
      if DEBUG: log.info("hash: " + r.group(1))
      postdata = {'fuck_you' : r.group(1), 'confirm' : 'Close Ad and Watch as Free User'}
      data = urllib.urlencode(postdata)
      req = urllib2.Request(url,data)
      req.add_header('User-Agent', HOST)
      cj = cookielib.LWPCookieJar()
      opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
      resp = opener.open(req)
      link = resp.read()
      resp.close()
      match = re.compile("playlist: '(.+?)'").findall(link)
      if len(match) > 0:
        if DEBUG: log.info("get_file.php:" + match[0])
        url = "http://www.sockshare.com" + match[0]
        req = urllib2.Request(url)
        req.add_header('User-Agent', HOST)
        resp = opener.open(req)
        link = resp.read()
        resp.close()
        if DEBUG: log.info(link)
        match = re.compile('</link><media:content url="(.+?)" type="video').findall(link)
        if len(match) > 0:
          url = match[0].replace('&amp;','&')
          if DEBUG: log.info("final link: " + url)
          return url
        else:
          return False
      else:
        return False
    else:
      return False




          