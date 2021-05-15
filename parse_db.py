import re
from xlrd import open_workbook

bd2009_2019 = open_workbook('data/БД2009-2019.xls')

out = {}

for sheet_name in bd2009_2019.sheet_names():
    try:
        int(sheet_name)
        sheet = bd2009_2019.sheet_by_name(sheet_name)
        region = {}
        for col in range(3, sheet.ncols):
            industry = {}
            for row in range(2, sheet.nrows):
                x = sheet.cell(row,col).value
                try:
                    industry_name = sheet.cell(row,1).value
                    assert re.match(r'.*[а-я]+.*', industry_name)
                except AssertionError:
                    industry_name = sheet.cell(row,0).value
                industry_name = industry_name.strip()
                industry.update({industry_name: x})
            region_name = sheet.cell(1,col).value
            region.update({region_name:industry})
        year = sheet_name
        out.update({year:region})            
    except ValueError:
        pass

from utilites import dump

dump(out, 'data/BD2009-2019.json')
