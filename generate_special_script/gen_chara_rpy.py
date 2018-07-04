#
# image chara 0 1 face = "chara/0/1_face.png"
# image chara 0 body = "chara/0/1_body.png"
# image chara 0 1 mouth = "chara/0/1_mouth_0.png"

import os

DIR = 'chara/'

charas = [None]*242

chara_list = os.listdir(DIR)

for chara in chara_list:
    f_list = os.listdir(os.path.join(DIR, chara))
    body = None
    emotions = [[] for i in range(16)]
    for f in f_list:
        if f.find('body') > -1:
            body = int(f.split('_')[0])
        elif f.find('mouth') > -1:
            emotions[int(f.split('_')[0])].append(int(f.split('_')[2][:-4]))
    charas[int(chara)] = (body, emotions)

with open('./charas.rpy', 'w', encoding='utf8') as fp:
    fp.write('define chara_infos = [\n')
    for c in charas:
        fp.write('(')
        if c[0] != None:
            fp.write(str(c[0]))
        else:
            fp.write('None')
        fp.write(',')
        fp.write(str(c[1]))
        fp.write('),\n')
    fp.write(']\n')
