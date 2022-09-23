import re
from random import choice

voc = {
    'cylinder'  : 'файл',
    'invtrapezium': 'ручная операция',
    'parallelogram': 'источник данных',
    'rect': 'действие',
}
used_resources = [
    "Ресурс %s используется программой %s. ",
    "Данные из %s используются программой %s. ",
    "Данные из %s используются скриптом %s. ",
    "Ресурс %s обрабатываются скриптом %s. ",
]

program_create_files = [
    "Программа %s создает файлы: ",
    "Скрипт %s создает файлы: ",
    "Скрипт %s генерирует файлы: ",
    "Программа %s генерирует файлы: ",
    "%s представляет результат своей работы в виде файлов: ",
]

file_used_by_prog = [
    "Файл %s используется программами:",
    "Такой файл как %s используется следующими программами:",
    "%s считывается скриптами:",
    "Данные из файла %s используются в скриптах:",
]

edges = [ x.strip().replace('"','').split(' -> ') for x in open('/tmp/out.dot').readlines() if '->' in x ]
nodes = [ (re.findall(r'\"(.*?)\"', x)[0], re.findall(r'\"(.*?)\"', x)[-1], voc[re.findall(r'shape=(\w+)', x)[-1]]) for x in open('/tmp/out.dot').readlines() if '[' in x ]

used_files = []
used_progs = []

edge_dict = {}
for a, b in edges:
    try:
        edge_dict[a] += [b]
    except KeyError:
        edge_dict.update({a:[b]})

print('Источниками данных для комплекса программ являются web-ресурсы: ', ', '.join([ x[1] for x in nodes if x[2] == 'источник данных' and '.dot' not in x[0] ]))
print('Также комплекс программ использует ряд файлов, подготовленных вручную:', ', '.join([ x[1] for x in nodes if x[2] == 'файл' and '.xls' in x[0] ]))

progs = []
for web, text in [ (x[0], x[1]) for x in nodes if x[2] == 'источник данных' and '.dot' not in x[0] ]:
    a_progs = edge_dict[web]
    for prog in a_progs:
        print(choice(used_resources) % (text, prog))
        progs += [prog]

for x in range(100):
    files = []    
    for prog in set(progs) - set(used_progs):
        try:
            a_files = edge_dict[prog]
            print(choice(program_create_files) % prog, ', '.join(a_files))
            for file in a_files:
                files += [file]
        except KeyError:
            pass
            # print(111111, prog)
        used_progs += [prog]

    progs = []
    for file in set(files) - set(used_files):
        try:
            a_progs = edge_dict[file]
            print(choice(file_used_by_prog) % file, ', '.join(a_progs))
            for prog in a_progs:
                progs += [prog]
        except KeyError:
            pass
#            print(11111, file)
        used_files += [file]
    

