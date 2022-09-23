import xlwt

from utilites import load
from itertools import product

_in = load('/tmp/ubiquity_0.7_0.9.json')

industries = _in['2019'].keys()
years = sorted(_in.keys())

wb = xlwt.Workbook()
ws = wb.add_sheet('ubiquity_0.7_0.9.json')

for year, n in zip(years, range(1, len(years)+1)):
	ws.write(0, n, year)

for industry, n in zip(industries, range(1, len(industries)+1)):
	ws.write(n, 0, industry)

for (year, c), (industry, r) in product(zip(years, range(1, len(years)+1)), zip(industries, range(1, len(industries)+1))):
	ws.write(r, c, _in[year][industry])

wb.save('/tmp/ubiquity_0.7_0.9.xls')