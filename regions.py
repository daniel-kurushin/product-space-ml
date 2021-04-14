from requests import get
from bs4 import BeautifulSoup as BS
from utilites import load, dump, compare

regions = load('data/regions.json')
#distances = load('data/distances.json')

def get_wiki_center(region):
    def is_city(region):
        x = soup.find('div', {'class':"mw-parser-output"}).table.tbody.tr.text
        return x.count('Город') > 0 or x.count('Столица') > 0
        
    try:
        return regions[region]['center']
    except KeyError:
        soup = BS(get('https://ru.wikipedia.org/wiki/%s' % region.replace(' ', '_')).content, features="lxml")    
        if is_city(region):
            regions[region].update({'center':region})
            return get_wiki_center(region)
        for th in soup('th'):
            if  th.text == 'Административный центр' or \
                th.text == 'Столица':
                cnt = th.parent.td.text.strip().strip('\n')
                regions[region].update({'center':cnt})
                return get_wiki_center(region)
        
def get_distance_adi(reg_A, reg_B):
    try:
        return distances['%s<->%s' % (reg_A, reg_B) ]
    except KeyError:
        try:
            center_A = get_wiki_center(reg_A).replace(' ', '+')
            center_B = get_wiki_center(reg_B).replace(' ', '+')
            soup = BS(get('https://www.avtodispetcher.ru/distance/?from=%s&to=%s' % (center_A, center_B)).content, features='lxml')
            d = int(soup.find(id="totalDistance").text)
        except AttributeError:
            d = 10000
        except ValueError:
            raise ValueError
        distances.update({'%s<->%s' % (reg_A, reg_B): d})
        distances.update({'%s<->%s' % (reg_B, reg_A): d})
        dump(distances, 'distances.json', quiet = 1)
        return get_distance_adi(reg_A, reg_B)

def get_distance_rdt(reg_A, reg_B):
    try:
        return distances['%s<->%s' % (reg_A, reg_B) ]
    except KeyError:
        try:
            center_A = get_wiki_center(reg_A).replace(' ', '+')
            center_B = get_wiki_center(reg_B).replace(' ', '+')
            soup = BS(get('https://ru.distance.to/%s/%s' % (center_A, center_B)).content, features='lxml')
            d = int(soup.find('span', "value km").text.replace('.','').replace(',','')) * 1.3 // 100
        except AttributeError:
            d = 10000
        except ValueError:
            raise ValueError
        distances.update({'%s<->%s' % (reg_A, reg_B): d})
        distances.update({'%s<->%s' % (reg_B, reg_A): d})
        dump(distances, 'distances.json', quiet = 1)
        return get_distance_rdt(reg_A, reg_B)

def emiss_to_yandex(emiss):
    for r in regions.keys():
        if regions[r]['emissname'] == emiss:
            return r

def get_yandex_name(wikiname):
    w0 = 0
    res = ''
    for rec in regions.keys():
        w1 = compare(rec, wikiname)
        if w1 > w0:
            res = rec
            w0 = w1
    try:
        assert w0 > 0.3
        return res
    except AssertionError:
        raise ValueError('Регион не найден')

def get_neighbors(region):
    def neighbors_from_a(pars):
        rez = []
        for p in pars:
            if  p.text.lower().count('граничит') > 0 or \
                p.text.lower().count('граница') > 0 or \
                p.text.lower().count('окружена') > 0:
                for a in p('a'):
                    try:
                        rez += [get_yandex_name(a['title'])]
                    except (KeyError, ValueError):
                        pass
        return rez
    
    def neighbors_from_text(pars):
        rez = []
        for p in pars:
            if  p.text.lower().count('граничит') > 0 or \
                p.text.lower().count('граница') > 0 or \
                p.text.lower().count('окружена') > 0:
                words = [ w for w in p.text.lower().split() 
                            if not ( w.startswith("област") or 
                                     w.startswith("край") or 
                                     w.startswith("края") or 
                                     w.startswith("респуб") ) ]
                for word in words:
                    try:
                        print(word)
                        rez += [get_yandex_name(word)]
                    except ValueError:
                        pass
        return rez

    try:
        return regions[region]['neighbors']
    except KeyError:
        try:
            soup = BS(get('https://ru.wikipedia.org/wiki/%s' % region.replace(' ', '_')).content, features="lxml")
            neighbor_candidates = neighbors_from_a(soup('p'))
            assert len(neighbor_candidates) > 1, 'Не найдены ссылки'
        except AssertionError:
            neighbor_candidates = neighbors_from_text(soup('p'))
                        
        neighbor_candidates = set(neighbor_candidates)
        same = {region}
        print(same, neighbor_candidates)
        neighbors = list(regnames & neighbor_candidates - same)
        regions[region].update({'neighbors':neighbors})
        dump(regions, 'regions.json', quiet = 1)
        return neighbors
    
def check_neighbors(regions):
    for regionA in regions.keys():
        neibA = regions[regionA]['neighbors']
        for regionB in neibA:
            neibB = regions[regionB]['neighbors']
            if regionA not in neibB:
                neibB += [regionA]
                print('.', end = '')
    print()
            
if __name__ == '__main__':
    regions = load('regions.json')
    print(111111111111)
    check_neighbors(regions)
    print(222222222222)
    check_neighbors(regions)
    dump(regions,'regions.json')
    

"""
Host: ati.su
User-Agent: Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0
Accept: application/json, text/plain, */*
Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
Referer: http://ati.su/trace/new?Ferries=1&Zimnik=1&Cities=1_3611%3B2_3064
Content-Type: application/json;charset=utf-8
Content-Length: 527
Cookie: ASP.NET_SessionId=kfl1ybd14cqyc1ckyhdfpmox
DNT: 1
Connection: keep-alive

{"cities":[3611,3064],"delays":{"0":0,"1":5,"2":10,"3":15,"4":30,"5":60,"6":90,"7":60,"8":120},"speeds":{"0":40,"1":40,"2":60,"3":60,"4":70,"5":80,"6":30,"10":20},"options":{"shortestRoute":false,"allowWinterRoads":true,"allowFerries":true,"withinCountry":true,"allowTollRoads":true,"excludeMkad":true},"excludedCities":[],"excludedRegions":[],"excludedCountries":[],"loadingPoints":[],"unloadingPoints":[],"departureDateUtc":"2018-12-06T04:00:00Z","workDay":{"workDayStartTime":"09:00:00","workingHours":8,"dailyMileage":500}}

POST /geo-search/v1.0/geo/search HTTP/1.1
Host: ati.su
User-Agent: Mozilla/5.0 (X11; Linux i686; rv:60.0) Gecko/20100101 Firefox/60.0
Accept: application/json, text/plain, */*
Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3
Accept-Encoding: gzip, deflate
Referer: http://ati.su/
Content-Type: application/json;charset=utf-8
Content-Length: 19
Cookie: ASP.NET_SessionId=kfl1ybd14cqyc1ckyhdfpmox; AtiGeo=182_3_4_1; last_visit=1544089862080::1544107862080; last_read_updates=0; announceae3196b734ed4f3c88783d1e9523b230=1
DNT: 1
Connection: keep-alive

"""