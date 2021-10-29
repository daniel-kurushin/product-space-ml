from utilites import load, dump
from xlrd import open_workbook

complexity = load('data/complexity.json')
regions = list(complexity.keys())

region_to_region = load('data/region-to-region.json')

neib85 = open_workbook('data/neib85.xls').sheet_by_index(0)
cluster_data = open_workbook('data/cluster_in_data.xlsx').sheet_by_index(0)


def get_reg_name(x):
    try:
        regname = region_to_region[x]
    except KeyError:
        assert x in regions
        regname = x
    return regname

M = {}

for row in range(1, neib85.nrows):
    for col in range(1, neib85.ncols):
        a, b = [ region_to_region[x.lower()] for x in [neib85.cell(col, 0).value, neib85.cell(0, row).value]]
        key = (a, b)
        if neib85.cell(col, row).value:
            M.update({key:1})
            
N = {}
            
for row in range(1, cluster_data.nrows):
    regname = get_reg_name(cluster_data.cell(row, 0).value.lower().strip())
    ind_parks =         int(cluster_data.cell(row, 1).value)
    cluster_in_region = int(cluster_data.cell(row, 2).value)
    sp_econ_zone =      int(cluster_data.cell(row, 3).value)
    
    N.update({
        regname:
            {
                "индустриальные парки": ind_parks,
                "наличие кластера" : cluster_in_region,
                "особая экономическая зона" : sp_econ_zone,

            }
        }
    )
