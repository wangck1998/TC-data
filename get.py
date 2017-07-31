#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import cookielib
import getpass
import HTMLParser
import json
import os
import re
import string
import urllib  
import urllib2  
from ssl import SSLError

filename = 'cookie'
cookie = cookielib.MozillaCookieJar(filename)
if os.path.exists(filename):
  cookie.load(filename, ignore_discard=True, ignore_expires=True)
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie))
htmlParser = HTMLParser.HTMLParser()

def login():
  print 'please login'
  username = raw_input('username:');
  password = getpass.getpass('password:');

  postdata = urllib.urlencode({
             'nextpage': 'http://community.topcoder.com/stat?c=problem_solution&cr=10574855&rd=16554&pm=13986',
             'module': 'Login',
             'username': username,
             'password': password
             })
  loginUrl = 'https://community.topcoder.com/tc';
  getpage(loginUrl, postdata)
  cookie.save(ignore_discard=True, ignore_expires=True)

def getpage(url, postData = None):
  print 'send request', url 
  while True:
    try:
      request = opener.open(url, postData, 10)
      ret = request.read()
    except Exception as e:
      print 'request timeout (10s), send another one'
      continue
    return ret;

def getDataUrl(problemUrl):
  html = getpage(problemUrl);
  ref = re.findall(r'(/tc\?module=ProblemDetail[^"]*)"', html);
  assert len(ref) > 0
  statusUrl = 'http://community.topcoder.com' + ref[0];

  html = getpage(statusUrl);
  ref = re.findall(r'<a href="([^"]*)" class="statText">view</a>', html);
  assert len(ref) > 0
  return 'http://community.topcoder.com' + ref[-1].replace('&amp;', '&');

def output(data, layout):
  def getLabel(i, j):
    return string.uppercase[i] + '.' * j
  
  def checkTypeStr(s):
    if len(s) == 0: return False;
    s = s[0];
    return isinstance(s, str) or isinstance(s, unicode);

  for i, s in enumerate(data):
    if isinstance(s, list) and checkTypeStr(s):
      layout = layout.replace(getLabel(i, 2), str(len(s[0])));
  for i, s in enumerate(data):
    if isinstance(s, list):
      layout = layout.replace(getLabel(i, 1), str(len(s)));
  for i, s in enumerate(data):
    if isinstance(s, list):
      layout = layout.replace(getLabel(i, 0), 
          ('\n' if checkTypeStr(s) else ' ').join(map(str, s)));
    else:
      layout = layout.replace(getLabel(i, 0), str(s));
  return layout

def generateData(url):
  firstIn = True;
  while True:
    html = getpage(url);
    text = re.findall(r'<!-- System Testing -->([^!]*)!', html);
    if len(text) > 0: break;
    if firstIn: firstIn = False; 
    else: print 'Is username or password wrong?';
    login();
  data = re.findall(r'<TD (?:BACKGROUND="/i/steel_blue_bg.gif" )?CLASS="statText"[^>]*>([^<]*)</TD>', text[0])
  assert len(data) % 3 == 0

  def pretty(s):
    s = htmlParser.unescape(s)
    s = '[' + s.replace('\n', '').replace('{', '[').replace('}', ']') + ']';
    return json.loads(s);
  dataIn = map(pretty, data[::3]);
  dataOut = map(pretty, data[1::3]);
  
  count = len(dataIn);
  print "*** Remember to configure the layout files. ***"
  name = raw_input('file name:');
  group = input('group size:');
  
  handle = open('layout.in');
  layoutIn = handle.read();
  handle.close();

  handle = open('layout.out');
  layoutOut = handle.read();
  handle.close();

  if os.path.exists(name) == False: os.mkdir(name);
  for i in xrange(0, count, group):
    writerIn = open('%s/%d.in' % (name, i / group + 1), 'w');
    writerOut = open('%s/%d.out' % (name, i / group + 1), 'w');
    
    if group > 1: writerIn.write(str(min(count - i, group)) + '\n');

    for j in xrange(i, min(count, i + group)) :
      writerIn.write(output(dataIn[j], layoutIn));
      writerOut.write(output(dataOut[j], layoutOut));
    writerIn.close();
    writerOut.close();

problemUrl = raw_input('problem url:');
dataUrl = getDataUrl(problemUrl);
generateData(dataUrl);

