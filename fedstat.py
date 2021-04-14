from okpd2okved import okpd2okved, okved
from rutermextract import TermExtractor as TE
from requests import get, post
from utilites import dump, load
from reg
ions import emiss_to_yandex, regions
#from pysal import W, Moran, Moran_Local

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

def calc_sums(IN = {}):
    rez_reg, rez_all, rez_ind = {}, {}, {}
    for year in range(2009, 2017):
        rez_all.update({str(year):0})
    for region in IN["По регионам"].keys():
        y = {}
        for year in range(2009, 2017):
            y.update({str(year):0})
        rez_reg.update({region:y})
        for industry in IN["По регионам"][region].keys():
            for year in IN["По регионам"][region][industry].keys():
                yearv = IN["По регионам"][region][industry][year]
                rez_reg[region].update({year:rez_reg[region][year] + yearv})
    for industry in IN["По кластерам"].keys():
        y = {}
        for year in range(2009, 2017):
            y.update({str(year):0})
        rez_ind.update({industry:y})
        for region   in IN["По кластерам"][industry].keys():
            for year in IN["По кластерам"][industry][region].keys():
                yearv = IN["По кластерам"][industry][region][year]
                rez_ind[industry].update({year:rez_ind[industry][year] + yearv})
                rez_all[year] += yearv
    
    return {"По регионам": rez_reg, "По кластерам" : rez_ind, 'Всего': rez_all }

def calc_lq(INA = {}, INB = {}):
    rez = {}
    for region in INA['По регионам']:
        reg = {}
        for industry in INA['По кластерам']:
            ind = {}
            for year in INA['Всего']:
                try:
                    B2  = INB["По регионам"][region][industry][year]
                except KeyError:
                    B2  = 0
                G2  = INA['По регионам'][region][year]
                B7  = INA['По кластерам'][industry][year]
                B10 = INA['Всего'][year]
                try:
                    v = (B2/G2)/(B7/B10)
                except ZeroDivisionError:
                    v = 0
                ind.update({year:v})
            reg.update({industry:ind})
        rez.update({region:reg})
                
    return rez
        
def clusters_from_dot(filename = 'clusters.dot'):
    def get_cl_name(a):
        conv = {
            '1':'Металлообработка',
            '2':'Химическая промышленность',
            '3':'Пищевая промышленность',
            '4':'Горнодобывающее производство',
            '5':'Лесная промышленность, деревообработка, целлюлозно-бумажная обработка',
            '6':'Обработка цветных и драгоценных металлов',
            '7':'Строительные материалы',
            '8':'Легкая промышленность',
            '9':'Нефтегазовая промышленность',
            '10':'Угольная промышленность',
            '11':'Высокотехнологичное оборудование и ИТ',
        }

        return conv[a]

    industry = ''
    rez = {}
    for line in open(filename).readlines():
        if line.count('->') == 0:
            industry += line.replace('\n', ' ').replace('\t', ' ')
            if line.count('[cluster') == 1:
                cnumber = line.split('="')[1].split('"')[0]
                industry = industry.strip()
                industry = industry.replace('"', ' ')
                industry = industry.split('[')[0]
                industry = industry.strip()
                words1 = industry.split()
                for okpd in okpd2okved.keys():
                    words2 = okpd.split()
                    n = 0
                    for word in words1:
                        n += words2.count(word)
                    if n/len(words1) > 0.9:
                        key = okpd2okved[okpd]
                        rez.update({key:cnumber})
                        break
                industry = ''
    rex = {}
    for clusternumber in set(rez.values()):
        clustercontent = [ a[0] for a in rez.items() if a[1] == clusternumber ]
        clustername = get_cl_name(clusternumber)
        rex.update({clustername:clustercontent})
        
    return {'По индустриям':rez, 'По кластерам':rex}

def make_spec_data(IN = {}, CL = {}):
    def calc_PCA(a):
        return 0
    
    res = {}
    for region in IN.keys():
        for cl_name in CL['По кластерам'].keys():
            for industry in CL['По кластерам'][cl_name]:
                for year in [ str(y) for y in range(2009, 2017) ]:
                    try:
                        res[(region, cl_name, year)] += IN[region][industry][year]
                    except KeyError:
                        try:
                            res.update({(region, cl_name, year):IN[region][industry][year]})
                        except KeyError:
                            pass
                        
    rez_reg = {}
    rez_clu = {}
    for region in IN.keys():
        clu = {}
        for cluster in CL['По кластерам'].keys():
            years = {}
            for year in [ str(y) for y in range(2009, 2017) ]:
                try:
                    years.update({year:res[(region,cluster,year)]})
                except KeyError:
                    pass
            clu.update({cluster:years})
        rez_reg.update({region:clu})

    for cluster in CL['По кластерам'].keys():
        reg = {}
        for region in IN.keys():
            years = {}
            for year in [ str(y) for y in range(2009, 2017) ]:
                try:
                    years.update({year:res[(region,cluster,year)]})
                except KeyError:
                    pass
            reg.update({region:years})
        rez_clu.update({cluster:reg})
    
                
    return {'По регионам':rez_reg, 'По кластерам':rez_clu }

def get_hi_lo_regions(lq, regions, distances):
    data = {}
    clusters = lq[list(lq.keys())[0]].keys()
    for cluster in clusters:
        clu = {}
        DLQ_min, DLQ_max = 10000, -10000
        for region in regions.keys():
            lq_a = lq[region][cluster]['2016']
            D_lq = 0
            for neib in regions[region]['neighbors']:
                lq_b = lq[neib][cluster]['2016']
                D = distances["%s<->%s" % (region, neib)]
                if D == 0: D = 4
                D_lq += (lq_a - lq_b) * 1 / D
            D_lq /= len(regions[region]['neighbors'])
            if D_lq < DLQ_min: DLQ_min = D_lq
            if D_lq > DLQ_max: DLQ_max = D_lq
                
            clu.update({region:D_lq})
        clu.update({'min':DLQ_min})
        clu.update({'max':DLQ_max})
        data.update({cluster:clu})
    res = {}
    for cluster in clusters :
        clu = {'hi':[],'lo':[]}
        for region in regions.keys():
            LQ = lq[region][cluster]['2016']
            DLQ = data[cluster][region]
            B = data[cluster]['min'] / 53
            A = data[cluster]['max'] / 53
            if DLQ > A:
                clu['hi'].append((region,LQ))
            elif DLQ < B:
                clu['lo'].append((region,LQ))
        res.update({cluster:clu})
    return res

def get_neib_regions(hi_lo_regions, regions, distances):
    res = {}
    for cluster in hi_lo_regions.keys():
        clu = {}
        for regionA,lq in hi_lo_regions[cluster]['hi']:
            dst = []
            for regionB in set(regions.keys()) - {regionA}:
                dst += [(regionB, distances["%s<->%s" % (regionA, regionB)])]
            dst.sort(key=lambda x:x[1])
            neib_candidates = set([ _[0] for _ in dst[:3] ])
            hi_regions = set([ _[0] for _ in hi_lo_regions[cluster]['hi']])
            neib = list(neib_candidates - hi_regions)
            clu.update({regionA:neib})
        res.update({cluster:clu})
    return res

def get_region_colors(regions, neib_regions):
    colors = []
    for cluster in neib_regions.keys():
        clu = {'name':cluster}
        all_neib = []
        for region in neib_regions[cluster]:
            all_neib += neib_regions[cluster][region]
        for region in regions:
            code = regions[region]["code"]
            if region in neib_regions[cluster].keys():
                clu.update({code:"#FB6C3F"})
            elif region in all_neib:
                clu.update({code:"#F0F075"})
            else:
                clu.update({code:"#8A92AB"})
        colors += [clu]
    return colors

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
