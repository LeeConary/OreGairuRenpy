import os
import re
import struct

def search_table():
    tables = {}
    for f in os.listdir('../scx/'):
        if f.endswith('.bin.txt'):
            with open(os.path.join('../scx/', f), 'r') as fp:
                content = fp.read()
                matches = re.findall(r'DataAccess\(\S+, (\d+)\)', content)
                for m in matches:
                    m = int(m)
                    if m:
                        tables[f] = tables.get(f, set())
                        tables[f].add(m)
    return tables

def read_table(tables):
    result = {}
    for key in tables:
        with open(os.path.join('../scx/', key[:-4]), 'rb') as fp:
            label_start = 12
            fp.seek(label_start)
            label_end = struct.unpack('i', fp.read(4))[0]
            label_len = label_end - label_start
            fp.seek(label_start)
            # 读取所有标签偏移
            labels = list(struct.unpack('i'*int(label_len/4), fp.read(label_len)))
            tables[key] = list(tables[key])
            result[int(key[:-8])] = {}
            for i in range(len(tables[key])):
                label_id = tables[key][i]
                # 读取表格数据并赋值取代原来的表格标签id
                fp.seek(labels[label_id])
                block_len = labels[label_id+1] - labels[label_id]
                result[int(key[:-8])][label_id] = list(struct.unpack('i'*int(block_len/4), fp.read(block_len)))
    return result
with open('../OreGairu/game/tables.rpy', 'w', encoding='utf8') as fp:
    fp.write('define LabelTable = ' + str(read_table(search_table())))
    pass
