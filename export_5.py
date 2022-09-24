import xlwt

from utilites import load
from itertools import product

_in = load('/tmp/LQ_0.7_0.9.json')

years = sorted(_in.keys())
regions = list(_in['2019'].keys())
industries = _in['2019'][regions[0]].keys()

wb = xlwt.Workbook()

for year in years:
	ws = wb.add_sheet(year)

	for industry, n in zip(industries, range(1, len(industries)+1)):
		ws.write(0, n, industry)

	for region, n in zip(regions, range(1, len(regions)+1)):
		ws.write(n, 0, region)

	for (industry, c), (region, r) in product(zip(industries, range(1, len(industries)+1)), zip(regions, range(1, len(regions)+1))):
		ws.write(r, c, _in[year][region][industry])

wb.save('/tmp/LQ_0.7_0.9.xls')
