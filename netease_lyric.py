#! -*- coding=utf-8 -*-

import requests
import json


headers = {
            "Accept" : "*/*",
            "Accept-Encoding": "gzip,default,sdch" ,
            "Accept-Language": "zh-CN,zh;q=0.8,gl,zh-TW;q=0.4",
            "Connection": "keep-alive",
            "Host": "music.163.com",
            "Referer": "http://music.163.com/search",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36')"
            }

def showOptions(song_name):
    base_url = "http://music.163.com/api/search/get/web"
    content = {
         "s" : song_name,
         "type" : 1 ,
         "offset": 0 ,
         "limit" : 20,
        }

    ret = requests.post(base_url, headers=headers, data=content)
    if ret.status_code == 200 :
         d = ret.json()
         for i,s in enumerate(d["result"]["songs"]):
             author = ""
             if len(s["artists"]) > 0 :
                 for artist in s["artists"]:
                     author = author + "/" + artist["name"]
             print("option %s : song id %s , song name %s , author name %s"%(i ,s["id"], s["name"],author))
         op = input("enter your song id:")
         download(op)
    else:
        print("request failed at searching")

def download(song_id):
    url = "http://music.163.com/api/song/lyric?lv=1&kv=1&tv=-1&id=%s"%song_id
    ret = requests.get(url, headers=headers)
    if ret.status_code == 200 :
        d = ret.json()
        if d.get("lrc") and d["lrc"].get("lyric") :
            with open("ori.lrc","w") as f :
                f.write(d["lrc"]["lyric"] + "\n")
        if d.get("tlyric") and d["tlyric"].get("lyric"):
            with open("another.lrc","w") as f :
                f.write(d["tlyric"]["lyric"] + "\n")
        print("download finished")
    else:
        print("request failed at downloading")

if __name__ == '__main__':
    name = input("input a song name:")
    showOptions(name)
