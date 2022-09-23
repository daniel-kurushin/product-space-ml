# ignore
import re
from glob import glob

def find_functions(file_name, file_text):
    function_defs = re.findall(r'(def .*)', file_text) + ['END']
    rez = {}
    if function_defs:
        for i in range(len(function_defs) - 1):
            a = re.escape(function_defs[i])
            b = re.escape(function_defs[i+1])
            rez.update({(file_name, a): "".join(re.findall(a + r'(.*?)' + b, file_text, flags=re.M+re.S))})
    return rez

progs = []
funcs = []

for py in glob('*py'):
    lines = open(py).read() 
    if '# ignore' not in lines:
        progs += [py]
        funcs += [find_functions(py, lines)]
        
        
        