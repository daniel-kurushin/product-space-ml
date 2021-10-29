from utilites import load, dump
from xlrd import open_workbook

complexity = load('data/complexity.json')

neib85 = open_workbook('data/neib85.xls')

neib = {}

neibs = neib85.sheet_by_name('neibs')
excel_regions = [ neibs.cell(0,col).value.lower() for col in range(1, neibs.ncols)]
real_regions = list(complexity.keys())

for region in real_regions:
    print(excel_regions.index(region))
#for :
#    
#    year = int(sheet.cell(0,col).value)
#    out.update({year:{}})
#    for row in range(1, sheet.nrows):
#        region = sheet.cell(row,0).value
#        out[year].update({region: sheet.cell(row,col).value})
