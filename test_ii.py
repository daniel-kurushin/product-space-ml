from requests import get, post
from rutermextract import TermExtractor
from bs4 import BeautifulSoup
from pprint import pprint
from itertools import product
from math import tanh
from time import sleep

te = TermExtractor()

stopterms = ['англ', 'такой образ']
def open_graph(file_name):
    open(file_name, 'w').write("digraph g {\n")
#    open(file_name, 'a').write("rankdir = LR\n")
    
def close_graph(file_name):
    open(file_name, 'a').write("}")
        
def write_graph(file_name, x, y):
	x = x.replace(' ','\n')
	y = y.replace(' ','\n')
	open(file_name, 'a').write('"%s" -> "%s"\n' % (x, y))
    
def parse_yandex_referats(url):
    content = get (url) .content
    html = BeautifulSoup (content, features="html5lib")
    text = html.find("div", {"class": "referats__text"}).text
    
    return text

def parse_dukcduckgo (term):
    sleep (2)
    x = post(
		'https://html.duckduckgo.com/html/', 
		data={'q':term.replace(' ', '+')}, 
		headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
    ).content
    dom = BeautifulSoup(x, features="html5lib")
    snippets = [ x.text for x in dom('a', {'class':'result__snippet'}) ]
    text = " ".join(snippets)

    return text

def parse_habr (url):
    content = get (url) .content
    html = BeautifulSoup (content, features="html5lib")
    text = html.find ("div", {"class": "post__wrapper"}).text
    
    return text

def get_url_keywords(url):
    text = parse_habr(url)    
    return get_text_keywords(text)

def get_text_keywords(text):
    keywords = [
		t for t in te(text, strings=1, limit=50) if t.count(' ') > 0 and t not in stopterms 
	]
    
    return keywords
#https://github.com/daniel-kurushin/product-space-ml/blob/main/utilites.py 
def compare(S1,S2):
    ngrams = [S1[i:i+3] for i in range(len(S1))]
    count = 0
    for ngram in ngrams:
        count += S2.count(ngram)

    return count/max(len(S1), len(S2))

def compare_phrase(P1, P2):
    def func(x, a=0.00093168, b=-0.04015416, c=0.53029845):
        return a * x ** 2 + b * x ** 1 + c 
    
    P1 = P1.lower().split() if type(P1) == str else [ x.lower() for x in P1 ]
    P2 = P2.lower().split() if type(P2) == str else [ x.lower() for x in P2 ]
    n, v = 0, 0
    for a, b in set([ tuple(sorted((a, b))) for a, b in product(P1, P2)]):
        v += compare(a,b)
        n += 1
    try:
        return tanh((v / n) / func(max(len(P1),len(P2))))
    except ZeroDivisionError:
        return 0       
   
def filter_keywords (keywords):
    try:
        rez = [keywords[0]]
        for kw in keywords:
            tmp = []
            for a,b in set([ tuple(sorted((a, b))) for a, b in product(rez, [kw])]):
                v = compare_phrase(a,b)
                tmp += [(v, a)]        
                w = sorted(tmp, reverse=1)[0][0]
            if w < 0.5:
                rez += [kw]
        return rez
    except IndexError:
        return []
     
term_list = []
pair_list = []

region = 'химическая промышленность'

for term in ['пермский край', 'свердловская область', "республика чувашия"]:
    text = parse_dukcduckgo (region + ' ' + term)
    kw_for_kw = [ x.replace(region, '') for x in get_text_keywords(text) ]
    filtered_kw_for_kw = filter_keywords(kw_for_kw)
    term_list += filtered_kw_for_kw
    pair_list += [ (term, x) for x in filtered_kw_for_kw ]

open_graph('/tmp/big-graph.dot')
for a,b in pair_list:
    write_graph('/tmp/big-graph.dot', a, b)
close_graph('/tmp/big-graph.dot')
