import re
from xlrd import open_workbook
# ^^^ 2
# Извлечение данных из Excel

bd2009_2019 = open_workbook('data/БД2009-2019.a.xls')

out = {}

for sheet_name in bd2009_2019.sheet_names():
    try:
        int(sheet_name)
        sheet = bd2009_2019.sheet_by_name(sheet_name)
        region = {}
        for col in range(2, sheet.ncols):
            industry = {}
            for row in range(1, sheet.nrows):
                x = sheet.cell(row,col).value
                x = x if x else 0
                try:
                    industry_name = sheet.cell(row,1).value
                    assert re.match(r'.*[а-я]+.*', industry_name)
                except (AssertionError, TypeError):
                    industry_name = sheet.cell(row,0).value
                industry_name = " ".join(industry_name.strip().lower().split())
                industry.update({industry_name: x})
            region_name = " ".join(sheet.cell(0,col).value.strip().lower().split())
            region.update({region_name:industry})
        year = sheet_name
        out.update({year:region})            
    except ValueError:
        if sheet_name == "Таблица сопоставления":
            sheet = bd2009_2019.sheet_by_name(sheet_name)
            mapping_table = {}
            for row in range(2, sheet.nrows):
                k, v = [ " ".join(x.strip().lower().split()) for x in [ sheet.cell(row,1).value, sheet.cell(row,2).value] ]
                mapping_table.update({k:v})
                mapping_table.update({v:k})
            
    
            

from utilites import dump

dump(out, 'data/BD2009-2019.json')

dump(mapping_table, 'data/mapping_table_b.json')