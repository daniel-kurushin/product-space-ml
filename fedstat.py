from okpd2okved import okpd2okved, okved
from rutermextract import TermExtractor as TE
from requests import get, post
from utilites import dump, load
from regions import emiss_to_yandex, regions
#from pysal import W, Moran, Moran_Local
# ^^^ 1
# Извлечение данных из ЕМИСС

FNAME = 'out.4.json'
te = TE()

def download_fedstat():
    from json import loads
    gget = get('https://www.fedstat.ru/indicator/43007')
    cookies = gget.cookies.get_dict()
    headers = {}
    for header in open('fedstat.headers').readlines():
        key, value = [ _.strip() for _ in header.split(':', maxsplit = 1) ]
        headers.update({key:value})
    data = []
    for item in open('fedstat.post').read().split('&'):
        key, value = item.split('=', maxsplit = 1)
        data += [(key, value)]
    ppost = post('https://www.fedstat.ru/indicator/dataGrid.do?id=43007', 
               headers = headers,
               data = data,
               cookies = cookies)
    rez = loads(ppost.content.decode('utf-8'))
    return rez
    #print(dumps(loads(rez), ensure_ascii=1, indent=2))
    
def filter_fedstat(FD = []):
    for item in FD:
        if item['dim32155'] in okved and \
           item['dim32251'] in [ regions[r]['emissname'] for r in regions.keys() ]:
            yield item
        
def make_structure(FD = []):
    rez_reg = {}
    rez_ind = {}
    kyears = range(2009, 2017)
    for item in FD:
        region = emiss_to_yandex(item['dim32251'])
        industry = item['dim32155']
        year_values = {}
        for ky in kyears:
            year_values.update({ky:0})
            for k in item.keys():
                if k.startswith("dim%s_" % ky):
                    v = int(item[k].split(',')[0])
                    year_values.update({ky:v})
                    
        try:
            rez_reg[region].update({industry:year_values})
        except KeyError:
            rez_reg.update({region:{}})
            rez_reg[region].update({industry:year_values})
        try:
            rez_ind[industry].update({region:year_values})
        except KeyError:
            rez_ind.update({industry:{}})
            rez_ind[industry].update({region:year_values})
    return {"По регионам": rez_reg, "По отраслям" : rez_ind }

if __name__ == '__main__':
    end = False
    while not end:
        try:
            fedstat_data = load('fedstat_data.json')
            filtered_data = load('filtered_data.json')
            structured_data = load('structured_data.json')

            end = True
        except FileNotFoundError as e:
            if e.filename == 'fedstat_data.json':
                fedstat_data = download_fedstat()
                dump(fedstat_data, 'fedstat_data.json')
            if e.filename == 'filtered_data.json':
                filtered_data = filter_fedstat(fedstat_data['results'])
                dump(list(filtered_data), 'filtered_data.json')
            if e.filename == 'structured_data.json':
                structured_data = make_structure(filtered_data)
                dump(structured_data, 'structured_data.json')
