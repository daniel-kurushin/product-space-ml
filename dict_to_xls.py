from utilites import load

# ignore

def dict_to_xls(filename = 'out.xlsx', 
                 IN = {}, 
                 structure = {
                         "sheets":1,
                         "columns":2,
                         "rows":0}):
    def shorter(name):
        try:
            assert len(name) <= 31, "Excel limitation!"
            short_name = name
        except AssertionError:
            short_name = name.split()[0]
        return {name:short_name}
    
    import xlwt
    wb = xlwt.Workbook(encoding = 'UTF-8')
    levels = []
    levels += [sorted(list(IN.keys()))]
    levels += [sorted(list(IN[levels[0][0]].keys()))]
    levels += [sorted(list(IN[levels[0][0]][levels[1][0]].keys()))]
    sheetnames = {}
    for key0 in levels[structure['sheets']]:
        sheetnames.update(shorter(key0))
        ws = wb.add_sheet(sheetnames[key0])
        i = 1
        for key1 in levels[structure['columns']]:
            ws.write(0, i, key1)
            j = 1
            for key2 in levels[structure['rows']]:
                ws.write(j, i, IN[key0][key1][key2])
                j += 1
            i += 1
        i = 1
        for key2 in levels[structure['rows']]:
            ws.write(i, 0, key2)
            i += 1
    
    
    wb.save(filename)

if __name__ == "__main__":    
    data = load('data/normalized_table.json')

    dict_to_xls('/tmp/out.xlsx', data, {'sheets':0,'columns':1, 'rows':2})