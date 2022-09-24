import xlwt

from utilites import load
from itertools import product

_in = load('/tmp/complexity_1.0_0.9.json')

regions = _in.keys()
years = ['2019']

wb = xlwt.Workbook()
ws = wb.add_sheet('complexity_1.0_0.9.json')

for year, n in zip(years, range(1, len(years)+1)):
	ws.write(0, n, year)

for region, n in zip(regions, range(1, len(regions)+1)):
	ws.write(n, 0, region)

for (year, c), (region, r) in product(zip(years, range(1, len(years)+1)), zip(regions, range(1, len(regions)+1))):
	ws.write(r, c, _in[region])

wb.save('/tmp/complexity_1.0_0.9.xls')