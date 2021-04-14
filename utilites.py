from sys import stderr
from json import  load as jload
from numpy import load as nload
from json import  dump as jdump
from numpy import save as ndump
from nltk.tokenize import WordPunctTokenizer

from constants import MIN_WEIGHT

def load(filename):
    filetype = filename.split('.')[-1]
    try:
        rez = None
        print('Loading %s ...' % filename, end = '', file = stderr)
        if filetype == 'json':
            rez = jload(open(filename))
        elif filetype == 'dat':
            rez = nload(open(filename, 'rb'))
        print(' done', file = stderr)
        return rez
    except Exception as e:
        print(' error! %s' % e, file = stderr)
        raise e
    
def dump(object, filename, quiet = 0):
    filetype = filename.split('.')[-1]
    if not quiet: print('Saving %s ...' % filename, end = '', file = stderr)
    if filetype == 'json':
        jdump(object, open(filename, 'w'), indent = 2, ensure_ascii = 0)
    elif filetype == 'dat':
        ndump(open(filename, 'wb'), object)
    if not quiet: print('done', file = stderr)

"""
LM - матрица связей
WM - матрица весов
CL - список кластеров
idx - имена нод
"""
def graph(LM, WM, CL, idx, filename, subgraphs = False):
    wpt = WordPunctTokenizer()
    f = open(filename, 'w')
    f.write('digraph a {\n')
    n = 0
    if subgraphs:
        for cl in CL:
            n += 1
            f.write('\tsubgraph cluster_%s {\n' % n)
#            f.write('\t\tcolor=lightgrey; style=filled;\n')
            for x in cl:
                f.write('\t"%s";\n' % wrap(wpt, x))
            f.write('\t};\n')
    else:
        for cl in CL:
            n += 1
            for x in cl:
                f.write('\t"%s" [cluster="%s"];\n' % (wrap(wpt, x), n))
    for i in range(len(LM)):
        for j in range(len(LM[i])):
            if i != j and LM[i,j] > 0:# and WM[i,j] > MIN_WEIGHT:
                a = wrap(wpt, idx[str(i)])
                b = wrap(wpt, idx[str(j)])
                c = int(WM[i,j] * 100)
                d = abs(int(WM[i,j] * 10))
                if d == 0: d = 1
                out = '\t"%s" -> "%s" [label="%s", penwidth="%s"];\n' % (a, b, c, d)
                f.write(out)
    f.write('}\n')
    f.close()
                
def join(tokens = ['очень', 'длинная', 'строка', ',', 'с', 'пробелами', ',', 'и', 'знаками', 'препинания']):
    PUNKT = list(".,:;-")
    rez = []
    for i in range(len(tokens)):
        token = tokens[i]
        if token in PUNKT:
            rez[-1] += token
        else:
            rez += [token]
    return rez

#def wrap(a, b):
#    return b

def wrap(wpt, _str = "очень длинная строка,с пробелами, и знаками препинания"):
    _len = 0
    rez = ""
    for token in join(wpt.tokenize(_str)):
        _len += len(token)
        rez += " " + token
        if _len > 20:
            rez += "\n"
            _len = 0
    return rez.strip()

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
    for key0 in levels[structure['sheets']]:# кластера
        sheetnames.update(shorter(key0))
        ws = wb.add_sheet(sheetnames[key0])
        i = 1
        for key1 in levels[structure['columns']]:# годы
            ws.write(0, i, key1)
            j = 1
            for key2 in levels[structure['rows']]:# регионы
                ws.write(j, i, IN[key2][key0][key1])
                j += 1
            i += 1
        i = 1
        for key2 in levels[structure['rows']]:
            ws.write(i, 0, key2)
            i += 1
    
    
    wb.save(filename)

def compare(S1,S2):
    ngrams = [S1[i:i+3] for i in range(len(S1))]
    count = 0
    for ngram in ngrams:
        count += S2.count(ngram)

    return count/max(len(S1), len(S2))

if __name__ == '__main__':
    print(compare('компутер', 'компьютеризация'))
