#!/usr/bin/python3

import argparse
import code
import six
import sys
import threading
import websocket
import time
import sqlite3
import os
import datetime
import html
import traceback
from termcolor import colored
import urllib
from urllib.request import Request, urlopen
from random import shuffle

try:
    import readline
except:
    pass

proxy_host = ""
proxy_port = ""

agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/63.0.3239.84 Chrome/63.0.3239.84 Safari/537.36"
cookie=""
cookie="__cfduid=dd8d7ebb774d21374af0e2fda567940311517576244"

auth_string="AUTHSTRINGGOESHERE"

channel_name=None

OPCODE_DATA = (websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY)
ENCODING = getattr(sys.stdin, "encoding", "").lower()
db=None
conn=None

class VAction(argparse.Action):
    def __call__(self, parser, args, values, option_string=None):
        if values==None:
            values = "1"
        try:
            values = int(values)
        except ValueError:
            values = values.count("v")+1
        setattr(args, self.dest, values)

def parse_args():
    parser = argparse.ArgumentParser(description="WebSocket Simple Dump Tool")
    parser.add_argument("url", metavar="ws_url",
                        help="websocket url. ex. ws://echo.websocket.org/")
    parser.add_argument("-v", "--verbose", default=0, nargs='?', action=VAction,
                        dest="verbose",
                        help="set verbose mode. If set to 1, show opcode. "
                        "If set to 2, enable to trace  websocket module")

    return parser.parse_args()


class InteractiveConsole(code.InteractiveConsole):
    def write(self, data):
        sys.stdout.write("\033[2K\033[E")
        # sys.stdout.write("\n")
        sys.stdout.write("\033[34m" + data + "\033[39m")
        sys.stdout.write("\n> ")
        sys.stdout.flush()

    def raw_input(self, prompt):
        if six.PY3:
            line = input(prompt)
        else:
            line = raw_input(prompt)

        if ENCODING and ENCODING != "utf-8" and not isinstance(line, six.text_type):
            line = line.decode(ENCODING).encode("utf-8")
        elif isinstance(line, six.text_type):
            line = line.encode("utf-8")

        return line

def init_db():

    
    return (db,conn)
def truncate(s):
    if len(s) > 350:
            s = s[0:349]
    return s

def main():

    global news_map
    news_map = {}
    news_map["index"] = 1
    news_map["links"] = []
    news_map["url"] = "https://old.reddit.com/r/worldnews/"
    
    global dick_map
    dick_map = {}
    dick_map["index"] = 1
    dick_map["links"] = []
    dick_map["url"] = "https://old.reddit.com/r/massivecock/"
    
    global wild_map
    wild_map = {}
    wild_map["index"] = 1
    wild_map["links"] = []
    wild_map["url"] = "https://old.reddit.com/r/gonewild/"
    
    global science_map
    science_map = {}
    science_map["index"] = 1
    science_map["links"] = []
    science_map["url"] = "https://old.reddit.com/r/science/"

    global space_map
    space_map = {}
    space_map["index"] = 1
    space_map["links"] = []
    space_map["url"] = "https://old.reddit.com/r/space/"

    global tech_map
    tech_map = {}
    tech_map["index"] = 1
    tech_map["links"] = []
    tech_map["url"] = "https://old.reddit.com/r/technology/"

    global jedi_map
    jedi_map = {}
    jedi_map["index"] = 1
    jedi_map["links"] = []
    jedi_map["url"] = "https://old.reddit.com/r/conspiracy/"

    global wtf_map
    wtf_map = {}
    wtf_map["index"] = 1
    wtf_map["links"] = []
    wtf_map["url"] = "https://old.reddit.com/r/wtf/"
    
    channel_name = sys.argv[1]
    global trivia_on
    global answer
    global answered
    
    my_url=sys.argv[2]
    connection_origin = sys.argv[3]
    
    channel="#vl-" + channel_name
    join_string="JOIN " + channel
    chat_string="CHAT " + channel + " :/me - "
    console = InteractiveConsole()
    websocket.enableTrace(True)
    headers = ["Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Language: en-US,en;q=0.5","Accept-Encoding: gzip, deflate, br","Sec-WebSocket-Extensions: permessage-deflate","User-Agent: " + agent,"DNT: 1","Connection: keep-alive, Upgrade","Pragma: no-cache","Cache-Control: no-cache"]
    print("here")
    started = False
    while not started:
        try:
            ws = websocket.create_connection(my_url, header=headers, origin=connection_origin, cookie=cookie, http_proxy_host=proxy_host, http_proxy_port=proxy_port)
            started = True
        except:
            time.sleep(2)
            started = False
    
    print("Press Ctrl+C to quit")

    def recv():
        try:
            frame = ws.recv_frame()
            if not frame:
                raise websocket.WebSocketException("Not a valid frame %s" % frame)
            elif frame.opcode in OPCODE_DATA:
                return (frame.opcode, frame.data)
            elif frame.opcode == websocket.ABNF.OPCODE_CLOSE:
                ws.send_close()
                return (frame.opcode, None)
            elif frame.opcode == websocket.ABNF.OPCODE_PING:
                ws.pong("Hi!")
                return frame.opcode, frame.data

            return frame.opcode, frame.data
        except:
            time.sleep(5)
            main()
            
    def parse_html(html,query,query_end, contains=None):
        returnable = []
        cont = True
        s = 0
        lower = html.lower()
        while cont:
            start = lower.find(query, s)
            if start == -1:
                cont=False
                break
            if query_end == '"' or query_end == "'":
                q_end = lower[start + len(query)]
                end = lower.find(q_end, start + len(query) + 1)
                match = html[start + len(query) + 1:end]
                s = end
            else:
                end = lower.find(query_end, start + len(query))
                match = html[start + len(query):end]
                s = end
            
            if match not in returnable and not match == "":
                if not contains == None:
                    if contains in match:
                         returnable.append(match)
                else:
                    returnable.append(match)
        return returnable
    
    def open_url(page_url):
        
        agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'
        cookie = ''
        
        req=Request(urllib.parse.quote(page_url,":;_.-/&?=%"))
        req.add_header('user-agent', agent)
        req.add_header('Cookie', 'over18=1;')
        req.add_header('accept-language', 'en-US,en;q=0.9')
        req.add_header('upgrade-insecure-requests', '1')
        
        response=urlopen(req)
        content_type = response.info()['Content-Type']
        charset=response.info().get_content_charset()
        html = response.read().decode(charset)
        return content_type,html

    def strip_html(html,query,query_end):
        cont = True
        s = 0
        matches = []
        while cont:
            start = html.find(query, s)
            if start == -1:
                cont=False
                break
            end = html.find(query_end, start + len(query))
            match = html[start:end + len(query_end)]
            matches.append(match)
            s = end
        for match in matches:
            html = html.replace(match,"")
            
        return html
    
    def gen_im(user, data):
        return "MVN IM <vn:" + user + ">" + data + "</vn>"
    
    def wiki(q):
        try:
            query = ""
            for i in range(len(q)):
                query = query + q[i]
                if i!=len(q) - 1:
                    query = query + "_"
            url = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&titles=" + query + "&explaintext=1&redirects=&formatversion=2&exlimit=1&exchars=350&format=json"
            content_type, result = open_url(url)
            sums = parse_html(result,'"extract":','"}', contains=None)
            if len(sums) > 0:
                s = sums[0].strip()
                s = s[1:]
                s = s.replace("\\n"," ")
                s = s.replace('\\"','"')
                return s
            return "WIKI Error"
        except:
            return "WIKI Error"
    
    def imdb(q):
        try:
            query = ""
            for i in range(len(q)):
                query = query + q[i]
                if i!=len(q) - 1:
                    query = query + "+"
            url = "https://www.imdb.com/find?ref_=nv_sr_fn&q=" + query + "&s=all"
            content_type, result = open_url(url)
            tds = parse_html(result,'<td class="result_text">','</td>', contains=None)
            if len(tds) > 0:
                hrefs = parse_html(tds[0],'<a href="','" >', contains=None)
                if len(hrefs) > 0:
                    url = "https://www.imdb.com" + hrefs[0]
                    time.sleep(1)
                    content_type, result = open_url(url)
                    sums = parse_html(result,'<div class="summary_text">','</div>', contains=None)
                    if len(sums) > 0:
                        summ = sums[0].strip()
                        summ = strip_html(summ,"<a ",">")
                        summ = summ.replace("</a>","")
                        return  summ + " " + url
            return "IMDB Error"
        except:
            return "IMDB Error"
            
    def rational(q):
        try:
            query = ""
            for i in range(len(q)):
                query = query + q[i]
                if i!=len(q) - 1:
                    query = query + "_"
            url = "https://rationalwiki.org/w/index.php?search=" + query
            content_type, result = open_url(url)
            heading = parse_html(result,'<h1 id="firstHeading" ','</h1>', contains=None)
            if len(heading) > 0:
                if "Search results" in heading[0]:
                    return "RATIONAL Error"
            tds = parse_html(result,'<p>','</p>', contains=None)
            if len(tds) > 0:
                html = ""
                for td in tds:
                    text = td.strip()
                    text = strip_html(text,"<a ",">")
                    text = strip_html(text,"<span ",">")
                    text = strip_html(text,"<sup","</sup>")
                    text = strip_html(text,"<strong","</strong>")
                    text = text.replace("</a>","")
                    text = text.replace("</span>","")
                    text = text.replace("<b>","")
                    text = text.replace("</b>","")
                    text = text.replace("<i>","")
                    text = text.replace("</i>","")
                    text = text.replace("\r"," ")
                    text = text.replace("<br/>"," ")
                    text = text.replace("<br />"," ")
                    text = text.replace("\\'","'")
                    html = html + " " + text
                return html
            return "RATIONAL Error"
        except:
            return "RATIONAL Error"
        
    def urban(q):
        try:
            query = ""
            for i in range(len(q)):
                query = query + q[i]
                if i!=len(q) - 1:
                    query = query + "%20"
            url = "https://www.urbandictionary.com/define.php?term=" + query
            content_type, result = open_url(url)
            tds = parse_html(result,'<div class="meaning">','</div>', contains=None)
            
            if len(tds) > 0:
                
                html = tds[0].strip()
                html = strip_html(html,"<a ",">")
                html = html.replace("</a>","")
                html = html.replace("\r"," ")
                html = html.replace("<br/>","")
                ex = parse_html(result,'<div class="example">','</div>', contains=None)
                if len(ex) > 0:
                    
                    expl = ex[0].strip()
                    expl = strip_html(expl,"<a ",">")
                    expl = expl.replace("</a>","")
                    expl = expl.replace("\r"," ")
                    expl = expl.replace("<br/>","")
                    
                    html = html + " EX: " + expl
                html = html.replace("&apos;","'")
                html = html.replace("&quot;",'"')
                return html
            return "URBAN Error"
        except:
            return "URBAN Error"
    
    def news():
        global news_map
        try:
            if news_map["index"] >= len(news_map["links"]):
                print("Getting links")
                news_map["index"] = 1
                links = []
                for x in range(4):
                    time.sleep(2)
                    content_type, result = open_url(news_map["url"])
                    next = parse_html(result,'<a ','>', contains='rel="nofollow next"')
                    next = parse_html(next[0],'href=','"')[0]
                    news_map["url"] = next
                    hrefs = parse_html(result,'<p class="title">','</p>', contains=None)
                    for h in hrefs:
                        p = parse_html(h,'data-href-url=','"')
                        if len(p) > 0:
                            href = p[0]
                        t = parse_html(h,'rel="" >','</a>')
                        if len(t) > 0:
                            title = t[0]
                            title = title.replace("&quot;",'"')
                        links.append(title + " " + href)
                    print("len=",len(links))
                shuffle(links)
                news_map["links"] = links
                return links[0]
            else:
                link = news_map["links"][news_map["index"]]
                news_map["index"] = news_map["index"] + 1
                return link
        except Exception as e:
            print(e)
            return "NEWS Error"
            
    def dickpic():
        global dick_map
        try:
            if dick_map["index"] >= len(dick_map["links"]):
                print("Getting Dicks")
                dick_map["index"] = 1
                links = []
                for x in range(4):
                    time.sleep(2)
                    content_type, result = open_url(dick_map["url"])
                    next = parse_html(result,'<a ','>', contains='rel="nofollow next"')
                    next = parse_html(next[0],'href=','"')[0]
                    dick_map["url"] = next
                    hrefs = parse_html(result,'<p class="title">','</p>', contains=None)
                    for h in hrefs:
                        p = parse_html(h,'data-href-url=','"')
                        if len(p) > 0:
                            href = p[0]
                        t = parse_html(h,'rel="" >','</a>')
                        if len(t) > 0:
                            title = t[0]
                            title = title.replace("&quot;",'"')
                        if "imgur" in href:
                            links.append(href)
                    print("len=",len(links))
                shuffle(links)
                dick_map["links"] = links
                return links[0]
            else:
                link = dick_map["links"][dick_map["index"]]
                dick_map["index"] = dick_map["index"] + 1
                return link
        except Exception as e:
            print(e)
            return "CanT FiNd A DiCkPiC"
            
    def gonewild():
        global wild_map
        try:
            if wild_map["index"] >= len(wild_map["links"]):
                print("Getting Tits")
                wild_map["index"] = 1
                links = []
                for x in range(4):
                    time.sleep(2)
                    content_type, result = open_url(wild_map["url"])
                    next = parse_html(result,'<a ','>', contains='rel="nofollow next"')
                    next = parse_html(next[0],'href=','"')[0]
                    wild_map["url"] = next
                    hrefs = parse_html(result,'<p class="title">','</p>', contains=None)
                    for h in hrefs:
                        p = parse_html(h,'data-href-url=','"')
                        if len(p) > 0:
                            href = p[0]
                        t = parse_html(h,'rel="" >','</a>')
                        if len(t) > 0:
                            title = t[0]
                            title = title.replace("&quot;",'"')
                        if "imgur" in href:
                            links.append(href)
                    print("len=",len(links))
                shuffle(links)
                wild_map["links"] = links
                return links[0]
            else:
                link = wild_map["links"][wild_map["index"]]
                wild_map["index"] = wild_map["index"] + 1
                return link
        except Exception as e:
            print(e)
            return "CanT LoCaTe BeWbS"
            
    def science():
        global science_map
        try:
            if science_map["index"] >= len(science_map["links"]):
                science_map["index"] = 1
                links = []
                for x in range(4):
                    time.sleep(2)
                    content_type, result = open_url(science_map["url"])
                    next = parse_html(result,'<a ','>', contains='rel="nofollow next"')
                    next = parse_html(next[0],'href=','"')[0]
                    science_map["url"] = next
                    hrefs = parse_html(result,'<p class="title">','</p>', contains=None)
                    for h in hrefs:
                        p = parse_html(h,'data-href-url=','"')
                        if len(p) > 0:
                            href = p[0]
                        t = parse_html(h,'rel="" >','</a>')
                        if len(t) > 0:
                            title = t[0]
                            title = title.replace("&quot;",'"')
                        if "/r/science/" not in href:
                            links.append(title + " " + href)
                    print("len=",len(links))
                shuffle(links)
                science_map["links"] = links
                return links[0]
            else:
                link = science_map["links"][science_map["index"]]
                science_map["index"] = science_map["index"] + 1
                return link
        except Exception as e:
            print(e)
            return "SCIENCE Error"
            
    def space():
        global space_map
        try:
            if space_map["index"] >= len(space_map["links"]):
                space_map["index"] = 1
                links = []
                for x in range(4):
                    time.sleep(2)
                    content_type, result = open_url(space_map["url"])
                    next = parse_html(result,'<a ','>', contains='rel="nofollow next"')
                    next = parse_html(next[0],'href=','"')[0]
                    space_map["url"] = next
                    hrefs = parse_html(result,'<p class="title">','</p>', contains=None)
                    for h in hrefs:
                        p = parse_html(h,'data-href-url=','"')
                        if len(p) > 0:
                            href = p[0]
                        t = parse_html(h,'rel="" >','</a>')
                        if len(t) > 0:
                            title = t[0]
                            title = title.replace("&quot;",'"')
                        if "/r/space/" not in href:
                            links.append(title + " " + href)
                    print("len=",len(links))
                shuffle(links)
                space_map["links"] = links
                return links[0]
            else:
                link = space_map["links"][space_map["index"]]
                space_map["index"] = space_map["index"] + 1
                return link
        except Exception as e:
            print(e)
            return "SPACE Error"
        
    def tech():
        global tech_map
        try:
            if tech_map["index"] >= len(tech_map["links"]):
                tech_map["index"] = 1
                links = []
                for x in range(4):
                    time.sleep(2)
                    content_type, result = open_url(tech_map["url"])
                    next = parse_html(result,'<a ','>', contains='rel="nofollow next"')
                    next = parse_html(next[0],'href=','"')[0]
                    tech_map["url"] = next
                    hrefs = parse_html(result,'<p class="title">','</p>', contains=None)
                    for h in hrefs:
                        p = parse_html(h,'data-href-url=','"')
                        if len(p) > 0:
                            href = p[0]
                        t = parse_html(h,'rel="" >','</a>')
                        if len(t) > 0:
                            title = t[0]
                            title = title.replace("&quot;",'"')
                        if "/r/technology/" not in href:
                            links.append(title + " " + href)
                    print("len=",len(links))
                shuffle(links)
                tech_map["links"] = links
                return links[0]
            else:
                link = tech_map["links"][tech_map["index"]]
                tech_map["index"] = tech_map["index"] + 1
                return link
        except Exception as e:
            print(e)
            return "TECH Error"
            
    def jedi():
        global jedi_map
        try:
            if jedi_map["index"] >= len(jedi_map["links"]):
                jedi_map["index"] = 1
                links = []
                for x in range(4):
                    time.sleep(2)
                    content_type, result = open_url(jedi_map["url"])
                    next = parse_html(result,'<a ','>', contains='rel="nofollow next"')
                    next = parse_html(next[0],'href=','"')[0]
                    jedi_map["url"] = next
                    hrefs = parse_html(result,'<p class="title">','</p>', contains=None)
                    for h in hrefs:
                        p = parse_html(h,'data-href-url=','"')
                        if len(p) > 0:
                            href = p[0]
                        t = parse_html(h,'rel="" >','</a>')
                        if len(t) > 0:
                            title = t[0]
                            title = title.replace("&quot;",'"')
                        if "/r/conspiracy/" not in href:
                            links.append(title + " " + href)
                    print("len=",len(links))
                shuffle(links)
                jedi_map["links"] = links
                return links[0]
            else:
                link = jedi_map["links"][jedi_map["index"]]
                jedi_map["index"] = jedi_map["index"] + 1
                return link
        except Exception as e:
            print(e)
            return "JEDI Error"
            
    def wtf():
        global wtf_map
        try:
            if wtf_map["index"] >= len(wtf_map["links"]):
                wtf_map["index"] = 1
                links = []
                for x in range(4):
                    time.sleep(2)
                    content_type, result = open_url(wtf_map["url"])
                    next = parse_html(result,'<a ','>', contains='rel="nofollow next"')
                    next = parse_html(next[0],'href=','"')[0]
                    wtf_map["url"] = next
                    hrefs = parse_html(result,'<p class="title">','</p>', contains=None)
                    for h in hrefs:
                        p = parse_html(h,'data-href-url=','"')
                        if len(p) > 0:
                            href = p[0]
                        t = parse_html(h,'rel="" >','</a>')
                        if len(t) > 0:
                            title = t[0]
                            title = title.replace("&quot;",'"')
                        if "/r/space/" not in href:
                            links.append(title + " " + href)
                    print("len=",len(links))
                shuffle(links)
                wtf_map["links"] = links
                return links[0]
            else:
                link = wtf_map["links"][wtf_map["index"]]
                wtf_map["index"] = wtf_map["index"] + 1
                return link
        except Exception as e:
            print(e)
            return "WTF Error"
    
    def recv_ws():
        global asked
        global trivia_on
        global answer
        global answered
        conn = sqlite3.connect('trivia.db', timeout=30)
        db = conn.cursor()
        global question_time
        vote = False
        vote_yes = 0
        vote_no = 0
        vote_time = 0
        voters = []
        last_vote = 0
        chat_message = False;
        while True:
            opcode, data = recv()
            if data != None:
                msg = None
                
                msg = "< %s: %s" % (websocket.ABNF.OPCODE_MAP.get(opcode), data)
                if data==b'PING\x00':
                    message = "PONG"
                    message = message + "\00"
                    ws.send(message)
                elif (data != None):
                    message = data.decode("utf-8", "replace")
                    chat_message = False;
                    if "CHAT " + channel in message:
                        
                        user = message.partition(";")[0]
                        chan = message.partition("CHAT ")[2].partition(" :")[0]
                        chat_text = message.partition("CHAT ")[2].partition(" :")[2].replace("\x00","")
                        chat_text = html.unescape(chat_text)
                        date = datetime.datetime.now()
                        color = message.partition("CHAT ")[0].partition(";")[2].partition(";")[0].lower()
                        colors = ["grey", "red", "green", "yellow","blue","magenta","cyan","white"]
                        vcolors = {"firebrick": "red", "deeppink" : "magenta", "black": "white", "cadetblue": "blue","purple": "cyan", "goldenrod" : "yellow", "royalblue" : "blue", "orangered" : "red", "midnightblue" : "blue", "dodgerblue" : "blue", "tomato" : "red"}
                        if color in list(vcolors):
                            color = vcolors[color]
                        elif not color in colors:
                            color = "white"
                        try:
                            print(colored(str(user), color, attrs=['bold', 'underline']) + colored(" : " + str(chat_text), color, attrs=['bold']))
                        except:
                            print(colored(str(user.encode('utf-8')), color, attrs=['bold', 'underline']) + colored(" : " + str(chat_text.encode('utf-8')), color, attrs=['bold']))
                        chat_message = True
                        if chat_text[0]=="!":
                            args = chat_text[1:].split(" ")
                            try:
                                time.sleep(1)
                                operation = None
                                search_terms = None

                                if len(args) >= 1:
                                    operation = args[0]
                                    
                                if len(args) >= 2:
                                    search_terms = args[1:]
                                    search_terms = ' '.join(search_terms)

                                if operation=="triviastart":
                                    rows = db.execute('''select * from allowed where user=? and channel=? COLLATE NOCASE''', (user,chan))
                                    found_user = False
                                    for row in rows:
                                        found_user = True
                                    if found_user:
                                        time.sleep(3)
                                        message = chat_string + "Trivia Started" + "\00"
                                        ws.send(message)
                                        time.sleep(3)
                                        trivia_on =True
                                elif operation=="triviastop":
                                    rows = db.execute('''select * from allowed where user=? and channel=? COLLATE NOCASE''', (user,chan))
                                    found_user = False
                                    for row in rows:
                                        found_user = True
                                    if found_user:
                                        trivia_on = False
                                        asked = False
                                        answer = ""
                                        message = chat_string + "Trivia Stopped" + "\00"
                                        ws.send(message)
                                
                                elif operation=="score":
                                    rows = db.execute('''select score from scores where user=?''', (user,))
                                    score = 0
                                    for row in rows:
                                        score = row[0]
                                    message = chat_string + truncate(user + "'s" + " Current Score: " + str(score))
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="topscore":
                                    rows = db.execute('''select * from scores order by score desc limit 10''')
                                    out = ""
                                    for row in rows:
                                        out = out + row[0] + " [" + str(row[1]) + "], "
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="wiki":
                                    out = wiki(args[1:])
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="imdb":
                                    out = imdb(args[1:])
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="rational":
                                    out = rational(args[1:])
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="urban":
                                    out = urban(args[1:])
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="news":
                                    out = news()
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="paisley":
                                    out = dickpic()
                                    message = gen_im(user, truncate(out))
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="bewbs":
                                    out = gonewild()
                                    message = gen_im(user, truncate(out))
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="science":
                                    out = science()
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="technology":
                                    out = tech()
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="space":
                                    out = space()
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="jedi":
                                    out = jedi()
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="tf":
                                    out = wtf()
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="thot":
                                    out = "I Love You " + user
                                    message = chat_string + truncate(out)
                                    message = message + "\00"
                                    ws.send(message)
                                    
                                elif operation=="triviavote":
                                    elapsed_last_vote = time.time() - last_vote
                                    if elapsed_last_vote >= 600:
                                        out = "Trivia Vote Started: Vote Yes, or No for Starting Trivia (60 sec countdown)"
                                        vote = True
                                        vote_yes = 0
                                        vote_no = 0
                                        voters = []
                                        message = chat_string + truncate(out)
                                        message = message + "\00"
                                        ws.send(message)
                                        vote_time = time.time()
                                    else:
                                        message = chat_string + truncate("Trivia Vote Cooldown, Try Again In " + str(600-elapsed_last_vote) + " Seconds")
                                        message = message + "\00"
                                        ws.send(message)
                                elif operation=="help":
                                    message = chat_string + truncate("Commands: !triviavote, !triviastart, !triviastop, !score, !topscore, !allowed [user], !disallowed [user], !imdb [title], !wiki [query], !urban [query], !rational [query], !news, !science, !technology, !space, !jedi, !tf, !now, !setnow [name], !set [command value], !request [name], !requests")
                                    message = message + "\00"
                                    ws.send(message)
                                elif operation=="allowed":
                                    rows = db.execute('''select * from allowed where user=? and channel=? COLLATE NOCASE''', (user,chan))
                                    found_user = False
                                    for row in rows:
                                        found_user = True
                                    if found_user and search_terms != None:
                                        db.execute("insert into allowed values (?,?,?)", (chan,search_terms.strip(),user))
                                        message = chat_string + truncate("Allowed " + search_terms.strip())
                                        message = message + "\00"
                                        ws.send(message)
                                        conn.commit()
                                elif operation=="request":
                                    d = datetime.datetime.now()
                                    date = str(d)
                                    date = date.partition(" ")[0]
                                    rows = db.execute('''select * from requests where user=? and channel=? and date >=? COLLATE NOCASE''', (user,chan, date))
                                    found_user = False
                                    for row in rows:
                                        found_user = True
                                    if not found_user and search_terms != None:
                                        db.execute("insert into requests values (?,?,?,?)", (str(d),chan,user,search_terms.strip()))
                                        message = chat_string + truncate(user + " Requested: " + search_terms.strip())
                                        message = message + "\00"
                                        ws.send(message)
                                        conn.commit()
                                    else:
                                        message = chat_string + truncate(user + " Already Requested Today, Try Again Tomorrow")
                                        message = message + "\00"
                                        ws.send(message)
                                elif operation=="requests":
                                    d = datetime.datetime.now()
                                    date = str(d)
                                    date = date.partition(" ")[0]
                                    rows = db.execute('''select user,name from requests where channel=?''', (chan, ))
                                    output = ""
                                    for row in rows:
                                        output = output + row[0] + " : " + row[1] + ", " 
                                    n = 325
                                    ims = [output[i:i+n] for i in range(0, len(output), n)]
                                    for im in  ims:
                                        message = message = gen_im(user, truncate(im))
                                        message = message + "\00"
                                        ws.send(message)
                                        time.sleep(2)
                                elif operation=="requestsclear":
                                    if user.lower() == chan.partition("-")[2].lower():
                                        db.execute("delete from requests where channel=?", (chan,))
                                        message = message = message = gen_im(user, truncate("Requests Cleared"))
                                        message = message + "\00"
                                        ws.send(message)
                                        conn.commit()
                                elif operation=="now":
                                    rows = db.execute('''select * from settings where channel=? and type="now_playing" COLLATE NOCASE''', (chan,))
                                    now_playing = "None Set"
                                    for row in rows:
                                        now_playing = row[3]
                                        message = chat_string + truncate("Now Playing: " + now_playing)
                                        message = message + "\00"
                                        ws.send(message)
                                        conn.commit()
                                elif operation=="setnow":
                                    rows = db.execute('''select * from allowed where user=? and channel=? COLLATE NOCASE''', (user,chan))
                                    found_user = False
                                    for row in rows:
                                        found_user = True
                                    if found_user and search_terms != None:
                                        db.execute('''delete from settings where channel=? and type="now_playing"''', (chan,))
                                        db.execute("insert into settings values (?,?,?,?)", (chan,user,"now_playing",search_terms.strip()))
                                        message = chat_string + truncate("Now Playing Set To: " + search_terms.strip())
                                        message = message + "\00"
                                        ws.send(message)
                                        conn.commit()
                                elif operation=="set":
                                    rows = db.execute('''select * from allowed where user=? and channel=? COLLATE NOCASE''', (user,chan))
                                    found_user = False
                                    for row in rows:
                                        found_user = True
                                    if found_user:
                                        if search_terms != None:
                                            parts = search_terms.partition(" ")
                                            if parts[2] != "":
                                                name = parts[0].strip()
                                                value = parts[2].strip()
                                                db.execute('''delete from custom_commands where channel=? and name=?''', (chan,name))
                                                db.execute("insert into custom_commands values (?,?,?,?)", (chan,user,name,value))
                                                message = chat_string + truncate(name + " Set To: " + value)
                                                message = message + "\00"
                                                ws.send(message)
                                                conn.commit()
                                elif operation=="disallowed":
                                    rows = db.execute('''select * from allowed where user=? and channel=? COLLATE NOCASE''', (user,chan))
                                    found_user = False
                                    for row in rows:
                                        found_user = True
                                    if found_user and search_terms != None:
                                        db.execute("delete from allowed where channel=? and user=?", (chan,search_terms.strip()))
                                        message = chat_string + truncate("Disallowed " + search_terms.strip())
                                        message = message + "\00"
                                        ws.send(message)
                                        conn.commit()
                                else:
                                    rows = db.execute('''select name,value from custom_commands where channel=? COLLATE NOCASE''', (chan,))
                                    name = None
                                    value = None
                                    for row in rows:
                                        name = row[0]
                                        value = row[1]
                                        if operation == name:
                                            value = value.replace("%u",user)
                                            if search_terms != None:
                                                value = value.replace("%s",search_terms)
                                            else:
                                                value = value.replace("%s","")
                                            message = chat_string + truncate(value)
                                            message = message + "\00"
                                            ws.send(message)
                                

                            except:
                                print(traceback.format_exc())
                                sys.exit(0)
                                
                        if vote:
                            if chat_text.lower() == "yes":
                                if user not in voters:
                                    vote_yes = vote_yes + 1
                                    voters.append(user)
                            if chat_text.lower() == "no":
                                if user not in voters:
                                    vote_no = vote_no + 1
                                    voters.append(user)

                            elapsed_time = time.time() - vote_time
                            if elapsed_time >= 60:
                                if vote_yes > vote_no:
                                    message = chat_string + truncate("Trivia Enabled With " + str(vote_yes) + " Votes")
                                    message = message + "\00"
                                    ws.send(message)
                                    time.sleep(3)
                                    trivia_on =True
                                if vote_no > vote_yes:
                                    message = chat_string + truncate("Trivia Disabled With " + str(vote_no) + " Votes")
                                    message = message + "\00"
                                    ws.send(message)
                                    time.sleep(3)
                                    trivia_on =False
                                if vote_no == vote_yes:
                                    message = chat_string + truncate("Trivia Votes Tied With " + str(vote_no) + " Votes")
                                    message = message + "\00"
                                    ws.send(message)
                                    time.sleep(3)
                                    
                                vote = False
                                vote_yes = 0
                                vote_no = 0
                                vote_time = 0
                                voters = []
                                last_vote = time.time()
                                
                                

                        if not answered and trivia_on:
                            if "*" in answer:
                                for a in answer.split("*"):
                                    if chat_text.lower() == a.lower():
                                        answered = True
                                        answer = ""
                            else:
                                if chat_text.lower() == answer.lower():
                                    answered = True
                                    answer = ""
                            if answered:
                                rows = db.execute('''select score from scores where user=?''', (user,))
                                score = 0
                                for row in rows:
                                    
                                    score = row[0]
                                score = score + 1
                                if score == 1:
                                    db.execute("insert into scores values (?,?)", (user,score))
                                else:
                                    db.execute('''update scores set score=? where user=?''', (score,user))
                                conn.commit()
                                message = chat_string + truncate("Correct " + user + "!" + "  Current Score: " + str(score))
                                message = message + "\00"
                                ws.send(message)
                                
                if not chat_message and msg:
                    console.write(msg)
            else:
                time.sleep(5)
                main()
                #sys.exit(0)

    
    global trivia_on
    global answer
    global answered
    global asked
    global question_time
    asked = False
    conn = sqlite3.connect('trivia.db', timeout=30)
    db = conn.cursor()
    trivia_on = False
    answer = ""
    answered = False
    question_time = 35
    thread = threading.Thread(target=recv_ws)
    thread.daemon = True
    thread.start()

    time.sleep(10)
    ws.send(auth_string + "\00")
    time.sleep(10)
    ws.send(join_string + "\00")
    ask_time = time.time()
    time.sleep(3)
    poll_time = time.time()
    first_start = True
    while True:
        time.sleep(0.1)
        elapsed_poll_time = time.time() - poll_time
        if elapsed_poll_time >= 3600 or first_start:
            poll_time = time.time()
            if not trivia_on:
                message = chat_string + truncate("Trivia Available - !triviavote to Initiate Vote To Enable")
                message = message + "\00"
                #ws.send(message)
            first_start = False
        if trivia_on:
            if not asked:
                time.sleep(5)
                ask_time = time.time()
                rows = db.execute('''select * from trivia order by random() limit 1''')
                output = ""
                for row in rows:
                    category = row[1]
                    question = row[2]
                    answer = row[3]
                    try:
                        print("\n### - " + answer +"\n")
                    except:
                        print("answer contains weird characters")
                    if category == "NONE":
                        output = question
                    else:
                        output = category + ": " + question
                    
                    
                message = chat_string + truncate(output)
                message = message + "\00"
                ws.send(message)
                asked = True
                ask_time = time.time()
            
            if asked:
                elapsed_time = time.time() - ask_time
                if elapsed_time >= question_time and not answered:
                    message = chat_string + truncate("The Correct Answer Was: " + answer.partition("*")[0])
                    message = message + "\00"
                    ws.send(message)
                    answer = ""
                    asked = False
                if answered:
                    asked = False
                    answered = False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
        sys.exit(0)
