from bs4 import BeautifulSoup
from glob import glob
from rutermextract import TermExtractor

te = TermExtractor()

for xml_file in glob('data/*svg'):
    x = BeautifulSoup(open(xml_file).read(), 'xml')
    titles = set([ y.text for y in x('title') if '->' not in y.text ])

dictionary = {}

for title in titles:
    kw = [ x for x in te(title, strings=1) ]
    dictionary.update({title: kw})
    