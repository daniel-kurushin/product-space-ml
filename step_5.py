# Индекс Тейпа

from xlrd import open_workbook

bd2010_2018 = open_workbook('data/ВРП.xls')

out = {}

for sheet_name in bd2010_2018.sheet_names():
    try:
        sheet = bd2010_2018.sheet_by_name(sheet_name)
        for col in range(1, sheet.ncols):
            year = int(sheet.cell(0,col).value)
            out.update({year:{}})
            for row in range(1, sheet.nrows):
                region = sheet.cell(row,0).value
                out[year].update({region: sheet.cell(row,col).value})
    except ValueError:
        pass
            

from utilites import dump, load

dump(out, 'data/BD2010-2018.json')

out = load('data/BD2010-2018.json')

years = list(out.keys())
regions = list(out["2010"].keys())
R = len(out["2010"])

from math import log

for year in years:
    Y = sum([ v for v in out[year].values() ])
    T_m = 0
    for region in regions:
        Y_r = out[year][region]
        v = (Y_r / Y) * log(Y_r/(Y/R))
        print(region, v)
        T_m += v
    print(year, T_m)