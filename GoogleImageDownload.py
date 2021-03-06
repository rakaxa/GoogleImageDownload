#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib.request
import re
import datetime
import random
import time
import os
from bs4 import BeautifulSoup

# ex:
# https://www.google.co.jp/search?q=arial+font+family&safe=off&tbm=isch&tbs=isz:l
# https://www.google.co.jp/search?q=a+b+c&safe=off&client=safari&biw=1095&bih=903&source=lnms&tbm=isch&sa=X&tbm=isch&tbs=isz:l
#

def is_ascii(string):
  if string:
    return max([ord(char) for char in string]) < 128
  return True

def make_url(keyword):
  url = 'http://www.google.co.jp/search?'
  q = 'q='
  is_first = True
  for word in keyword:
    if is_first:
      is_first = False
    else:
      q += '+'
    if word != '':
      q += urllib.parse.quote(word)

  safe = 'safe=off'     # セーフサーチ
  client = 'client=safari'
  biw = 'biw=1095'
  bih = 'bih=903'
  source = 'source=lnms'
  sa = 'sa=X'
  tbm = 'tbm=isch'      # 画像検索
  tbs = 'tbs=isz:l'     # 画像サイズ:大
  url += q + '&' + safe + '&' + client + '&' + biw + '&' + bih + '&' + source + '&' + sa +  '&' + tbm + '&' + tbs

  return url

def get_searchresult(url):
  # URLの情報を保存(IE10のユーザエージェント)
  req = urllib.request.Request(url)
  req.add_header("User-agent", 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)')
  response = urllib.request.urlopen(req)
  return response.read()

def get_image(url, dirname, now, count, ext):
  if '/?:*<>|' in ext:
    print(str(count) + ": Filename Error!!")
    print("ext : " + ext)
    return
  filename = dirname + '/' + "image_" + now + '_' + ("%03d" % (count)) + ext
  try:
    req = urllib.request.Request(url)
    req.add_header("User-agent", 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)')
    response = urllib.request.urlopen(req)
  except:
    print(str(count) + ": Download Error!!")
    print("URL : " + url)
    return

  try:
    f = open(filename, "wb")
    f.write(response.read())
    f.close()
  except:
    print(str(count) + ": FileOpen Error!!")
    print("Filename : " + filename)
    return
  print(str(count) + ": Success!!")
  return

keyword = []
dirname = ''
now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

# キーワードの取得
with open("keyword.txt") as f:
  for line in f:
    line = line.replace('\r','')
    line = line.replace('\n','')
    if not line.startswith("#"):
      keyword.append(line)
      dirname += line + '_'

# URLの組み立て
url = make_url(keyword)

# 検索情報取得
searchresult = get_searchresult(url)

if not os.path.exists(dirname):
  os.mkdir(dirname)

# BeautifulSoupを使って画像のURLを抽出
soup = BeautifulSoup(searchresult, 'html.parser')
imagelist = soup.find_all('div', class_='rg_meta notranslate')

# 画像取得
count = 0
for image in imagelist:
  m1 = re.search(u'"ou":"(.*?)"', image.string)
  if m1:
    m2 = re.search('(.*?)\?.*', m1.group(1))
    if m2:
      imgurl = m2.group(1)
    else:
      imgurl = m1.group(1)
    print(imgurl)
    match = re.search('.*(\..*?)$', imgurl)
    if match:
      ext = match.group(1)
      m_ext = re.search('(.*?)¥/.*', ext)
      if m_ext:
        ext = m_ext.group(1)
      if ext == 'jp':
        ext = 'jpg'
    get_image(imgurl, dirname, now, count, ext)
    count += 1
    time.sleep(random.randint(1, 10))
