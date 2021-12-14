from utilites import load, dump
from voc import voc
from itertools import product

LQP = [1, .7, 0.8, 1.5, 2]
SSP = [.8, .99, .9, .2]

data = load('data/normalized_table.json')

x_regions = [ x.lower() for x in ["Алтайский край", "Амурская область", "Архангельская область (кроме Ненецкого автономного округа)", "Астраханская область", "Белгородская область", "Брянская область"] ]
x_industries = [ x.lower() for x in [
"Выращивание однолетних культур",
"Выращивание многолетних культур",
"Животноводство",
"Смешанное сельское хозяйство",
"Деятельность вспомогательная в области производства сельскохозяйственных культур и послеуборочной обработки сельхозпродукции",
"Охота, отлов и отстрел диких животных, включая предоставление услуг в этих областях",
"Лесоводство и прочая лесохозяйственная деятельность",
"Лесозаготовки",
"Предоставление услуг в области лесоводства и лесозаготовок",
"Рыболовство",
"Рыбоводство",
]]

def sigma_p_region(x, region, Ss, lqp):
    return 1 if x >= lqp and region in Ss else 0

def filter_industries(industries):
    return [ x for x in industries if voc[x] != '🚫' ]

for lqp, ssp in product(LQP, SSP):
    print('lqp =', lqp, 'ssp =', ssp)
    sum_by_region = {}
    sum_by_industry = {}
    sum_by_region_total = {}
    
    years = data.keys()

    years_to_calc = years
    
    for year in years:
        sum_by_region.update({year:{}})
        sum_by_industry.update({year:{}})
        regions = data[year]
        for region in regions:
            sum_by_region[year].update({region:0})
            industries = data[year][region]
            for industry in filter_industries(industries):
                sum_by_region[year][region] += data[year][region][industry]
    
        for industry in (industries):
            sum_by_industry[year].update({industry:0})
            for region in regions:
                sum_by_industry[year][industry] += data[year][region][industry]
                
    for year in years:
        sum_by_region_total.update({year:0})
        regions = sum_by_region[year]
        for region in regions:
            sum_by_region_total[year] += sum_by_region[year][region]
            
    LQ = {}
    for year in years:
        regions = data[year]
        LQ.update({year:{}})
        for region in regions:
            industries = data[year][region]
            LQ[year].update({region:{}})
            for industry in filter_industries(industries):
                B2  = data[year][region][industry]
                _E2 = sum_by_region[year][region]
                B_8 = sum_by_industry[year][industry]
                _E_8 = sum_by_region_total[year]
                try:
                    v = (B2/_E2)/(B_8/_E_8)
                except ZeroDivisionError:
                    v = 0
                LQ[year][region].update({industry:v})
                
    dump(LQ, '/tmp/data/LQ_%s_%s.json' % (lqp, ssp))
    
    S = {}
    for year in years:
        regions = data[year]
        S.update({year:{}})
        for region in regions:
            industries = data[year][region]
            S[year].update({region:{}})
            for industry in filter_industries(industries):
                B2  = data[year][region][industry]
                A = sum_by_industry[year][industry]
                v = B2 / A
                S[year][region].update({industry:v})
                
    dump(S, '/tmp/data/S_%s_%s.json' % (lqp, ssp))
    
    Ss = {}
    for year in years:
        Ss.update({year:{}})
        for industry in filter_industries(industries):
            X = []
            x = 0
            Ss[year].update({industry:{}})
            n = 0
            while x < ssp: # x < 0.99:
                max_r = ("", 0)
                for region in [ x for x in regions if x not in [y[0] for y in X ] ]:
                    if S[year][region][industry] > max_r[1]:
                        max_r = (region, S[year][region][industry])
                X += [max_r] 
                x = sum([x[1] for x in X])
                if n > 1000:
                    print(x)
                    n = 0
                n += 1
            Ss[year].update({industry:[ x[0] for x in X]})
    
    dump(Ss, '/tmp/data/Sss_%s_%s.json' % (lqp, ssp))
    
    M = {}
    for year in LQ:
        regions = LQ[year]
        M.update({year:{}})
        for region in regions:
            industries = LQ[year][region]
            M[year].update({region:{}})
            for industry in filter_industries(industries):
                B12 = LQ[year][region][industry]
                v = sigma_p_region(B12, region, Ss[year][industry], lqp)
                M[year][region].update({industry:v})
                
    dump(M, '/tmp/data/M__%s_%s.json' % (lqp, ssp))
    
    ubiquity = {}
    
    for year in M:
        regions = M[year]
        ubiquity.update({year:{}})
        for region in regions:
            industries = M[year][region]
            for industry in filter_industries(industries):
                try:
                    ubiquity[year][industry] += M[year][region][industry]
                except KeyError:
                    ubiquity[year].update({industry:M[year][region][industry]})
                    
    dump(ubiquity, '/tmp/data/ubiquity_%s_%s.json' % (lqp, ssp))
    
    diversity = {}
    
    for year in M:
        diversity.update({year:{}})
        for region in regions:
            for industry in filter_industries(industries):
                try:
                    diversity[year][region] += M[year][region][industry]
                except KeyError:
                    diversity[year].update({region:M[year][region][industry]})
                    
    dump(diversity, '/tmp/data/diversity_%s_%s.json' % (lqp, ssp))
    
