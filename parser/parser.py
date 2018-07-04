import os
import re
import json
from instruction_regex import *

TEXTS_DIR = './texts/'
PATCHES_DIR = '../OreGairu/game/patches/'
scrnames = open('../assets/scrname.txt').readlines()

class Script():
    def __init__(self, path, outputpath=None, id=None):
        self.fp = open(path, 'r')
        self.path = path
        self.outputpath = outputpath
        self.blocks = []
        self.content = ''
        self.read_blocks()
        if id != None:
            self.id = id
            self.load_texts()

    # 按照label将脚本分块读取
    def read_blocks(self):
        lines = self.fp.readlines()
        label_index_list = []
        for i in range(len(lines)):
            if lines[i].startswith('#label'):
                label_index_list.append(i)

        # 从标签行开始读取，直到遇到空行结束，作为一个块
        for i in range(len(label_index_list)):
            block = lines[label_index_list[i]:
                          (label_index_list[i+1] if i+1 < len(label_index_list) else None)]
            self.blocks.append(block)

    # 加载脚本对应的文本
    def load_texts(self):
        path = os.path.join(TEXTS_DIR, scrnames[self.id][:-5]+'.json')
        if not os.path.exists(path):
            return

        with open(path, encoding='utf8') as json_file:
            texts = json.load(json_file)
            self.texts = texts

    def parse(self):
        self.process_blocks()
        self.content += f'label global_{self.id}:\n\n\tpass\n\n'
        for b in self.blocks:
            for l in b:
              self.content += l

        self.content = self.post_process(self.content)

    # 写出文件
    def output(self):
        path = self.path + '.rpy'
        if self.outputpath != None:
            path = self.outputpath

        with open(path, 'w', encoding='utf8') as fp:
            fp.write(self.content)

    # 处理代码块
    def process_blocks(self):
        for b in self.blocks:
            b[0] = re.sub(r'#label_(\d+)', r'label .label_\1', b[0])
            for i in range(1, len(b)):
                b[i] = self.convert_instruction(b[i], self.blocks.index(b), i)

    # 转换原脚本指令为renpy指令
    def convert_instruction(self, ins, block_id, line_num):
        # 遍历正则表，一旦匹配上就执行替换
        for opcode in reg_dict:
            if ins[:len(opcode)+1] == f'\t{opcode}':
                pat, repl = reg_dict[opcode]
                ins = re.sub(pat, repl, ins)
                return self.process_line(ins, block_id, line_num)

        # 删掉无用的指令
        for useless_ins in useless_inss:
            if ins.startswith(f'\t{useless_ins}'):
                return ''

        return self.comment_line(ins)

    # 对行进行额外的处理，主要是为了防止语法错误
    def process_line(self, line, block_id, line_num):
        # 替换文本引用为文本
        #TODO: 添加说话者
        matches = re.search(r'StringRef\((\d+)\)', line)
        if matches:
            strid = int(matches.group(1))
            #return re.sub(r'StringRef\((\d+)\)', r'"{}"'.format(self.texts[strid]['Chinese Translation']), line)

        # if line.count('DataAccess'):
        #     line = line.replace('DataAccess(LabelTable')
        # if line.count('LabelTable'):
        #     line = line.replace('LabelTable', f'LabelTable[{self.id}]')
        return f'#BlockLocalSymbol({block_id}, {line_num})\n' + line

    # 替换之后的处理
    def post_process(self, s):
        s = s.replace('#loadcha\n\t#"cha_pos"', ':\n\t')

        # renpy和py一样不支持自增自减，替换成+=1，-=1
        s = s.replace('++', '+=1').replace('--', '-=1')
        # 因为有些指令的第一个单词和某指令相同，会导致匹配不到，所以把他们注释掉
        for op in reg_dict:
            s = s.replace(op, '#'+op)
        # renpy的变量引用需要在语句前面加$，所以需要一些处理，虽然这样写很sb就是了
        #TODO: 美化优化这一步
        s = re.sub(r'[#]*GlobalVars', r'$ GlobalVars', s)
        s = re.sub(r'[#]*ThreadVars', r'$ ThreadVars', s)
        s = s.replace('= $ G', '= G')
        s = s.replace('= $ T', '= T')

        new_s = ''
        for l in s.split('\n'):
            if l.count('$') > 1 and l.count('#') == 0:
                l = l.replace('$ ', '').replace('$', '').lstrip('\t')
                l = '    $ ' + l
            new_s += l +'\n'

        s = new_s.replace('\t', '    ').replace('$ if ', 'if ').replace('if $', 'if ')

        return s

    def patch(self):
        if not os.path.exists(PATCHES_DIR+str(self.id)):
            return

        for block_dir in os.listdir(PATCHES_DIR+str(self.id)):
            for p in os.listdir(PATCHES_DIR+str(self.id)+'/'+block_dir+'/'):
                with open(os.path.join(PATCHES_DIR+str(self.id)+'/'+block_dir, p), encoding='utf8') as fp:
                    patch = fp.read()
                    self.content = self.content.replace(f'#BlockLocalSymbol({block_dir}, {p[:-4]})', patch)

    # 注释掉该行
    def comment_line(self, line):
        return line.replace('\t', '\t#')

if __name__ == '__main__':
    SCX_DIR = '../scx/'
    OUTPUT_DIR = '../OreGairu/game/'

    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    files = os.listdir(SCX_DIR)

    for f in files:
        if f.endswith('.bin.txt'):
            s = Script(os.path.join(SCX_DIR, f),
                       # 前面加zscr是为了防止脚本比重要的初始化脚本先执行导致一些错误
                       os.path.join(OUTPUT_DIR, 'zscr' + f.replace('.bin.txt', '.rpy')),
                       int(f.split('.')[0]))

            s.parse()

            s.patch()

            s.output()