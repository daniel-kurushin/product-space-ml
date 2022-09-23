# ignore
import re
from glob import glob

def find_from_json(py_lines):
    try:
        return [ re.findall(r'\(\'(.*?)\'.*?\)', x)[0] for x in py_lines if 'load(' in x and "#" not in x ]
    except IndexError:
        return []

def find_from_xls(py_lines):
    try:
        return [ re.findall(r'\(\'(.*?)\'\)', x)[0] for x in py_lines if 'open_workbook(' in x and "#" not in x ]
    except IndexError:
        return []

def find_from_web(py_lines):
    try:
        return [ re.findall(r'\'(https://.*?)\'', x)[0] for x in py_lines if 'https://' in x and "#" not in x ]
    except IndexError:
        return []

def find_to_json(py_lines):
    try:
        return [ re.findall(r'\(.*?\'(.*?)\'.*?\)', x)[0] for x in py_lines if 'dump(' in x and "#" not in x ]
    except IndexError:
        return []

def find_to_xls(py_lines):
    try:
        return [ re.findall(r'\(\'(.*?)\'.*?\)', x)[0] for x in py_lines if 'dict_to_xls(' in x and "#" not in x ]
    except IndexError:
        return []

def find_to_graph(py_lines):
    try:
        return [ re.findall(r'\(\'(.*?\.dot)\'.*?\)', x)[0] for x in py_lines if '.dot' in x and "#" not in x ]
    except IndexError:
        return []
    
files = []
grphs = []
hrefs = []
xlsxs = []
progs = []
edges = []
for py in glob('*py'):
    lines = [ x.strip() for x in open(py).readlines() ]
    if '# ignore' not in lines:
        progs += [py]
        files += find_from_json(lines) + find_to_json(lines)
        hrefs += find_from_web(lines)
        xlsxs += find_from_xls(lines) + find_to_xls(lines)
        grphs += find_to_graph(lines)
        for x in find_from_json(lines) + find_from_web(lines) + find_from_xls(lines):
            edges += [f'\t"{x}" -> "{py}"\n']
        for x in find_to_json(lines) + find_to_xls(lines) + find_to_graph(lines):
            edges += [f'\t"{py}" -> "{x}"\n']
        
with open('/tmp/out.dot', 'w') as out:
    out.write('digraph g {\n\trankdir=LR\n')
    for item in progs:
        out.write(f'\t"{item}" [shape=rect]\n')
    for item in files:
        label = item.split('/')[-1]
        out.write(f'\t"{item}" [shape=cylinder, label="{label}"]\n')
    for item in xlsxs:
        label = item.split('/')[-1]
        out.write(f'\t"{item}" [shape=cylinder, label="{label}"]\n')
    for item in grphs:
        label = item.split('/')[-1]
        out.write(f'\t"{item}" [shape=parallelogram, label="{label}"]\n')
    for item in hrefs:
        label = re.findall(r'((\w+\.)+\w+)', 'https://www.fedstat.ru/indicator/43007')[0][0]
        out.write(f'\t"{item}" [shape=parallelogram, label="{label}"]\n')
    for edge in set(edges):
        out.write(edge)
    out.write('}\n')