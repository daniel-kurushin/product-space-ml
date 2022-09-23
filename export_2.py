import xlwt

from utilites import load
from itertools import product

_in = load('/tmp/diversity_1.0_0.9.json')

regions = _in['2019'].keys()
years = sorted(_in.keys())

wb = xlwt.Workbook()
ws = wb.add_sheet('diversity_1.0_0.9.json')

for year, n in zip(years, range(1, len(years)+1)):
	ws.write(0, n, year)

for region, n in zip(regions, range(1, len(regions)+1)):
	ws.write(n, 0, region)

for (year, c), (region, r) in product(zip(years, range(1, len(years)+1)), zip(regions, range(1, len(regions)+1))):
	ws.write(r, c, _in[year][region])

wb.save('/tmp/diversity_1.0_0.9.xls')