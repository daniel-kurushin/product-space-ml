from utilites import load, dump

data = load('data/BD2009-2019.json')

for year in data:
    regions = data[year]
    for region in regions:
        industries = regions[region]
        a_sum = sum( [ industries[industry] for industry in industries ] )
        regions[region].update({'sum':a_sum})
            