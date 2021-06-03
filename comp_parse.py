import re
from xlrd import open_workbook
from utilites import dump, load

comp = open_workbook('/tmp/comp.xlsx')

sheet = comp.sheet_by_index(0)
mapping_table_a = {}
for row in range(0, sheet.nrows):
    k, v = [ " ".join(x.strip().lower().split()) for x in [ sheet.cell(row,0).value, sheet.cell(row,1).value] ]
    mapping_table_a.update({k:v})
    mapping_table_a.update({v:k})
 
dump(mapping_table_a, 'data/mapping_table_a.json')  
mapping_table_b = load('data/mapping_table_b.json')

for k in mapping_table_a.keys():
    try:
        x = mapping_table_b[k]
    except KeyError:
        x = None
    print(mapping_table_a[k], x)