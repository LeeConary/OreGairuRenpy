import os
import struct
import math
from PIL import Image
import imageio
import copy

# 该类为春物原游戏的lay文件， 用于切割组合人物图片
class Lay():
    def __init__(self, name, path, oldimg_path):
        self.name = name
        self.fp = open(path, 'rb')
        self.oldimg = self.init_old_image(oldimg_path)
        self.pics = []
        self.parts = []
        self.read_head()
        self.read_body()

    def read_head(self):
        fp = self.fp
        self.pic_count = struct.unpack('i', fp.read(4))[0]
        self.part_total_count = struct.unpack('i', fp.read(4))[0]

    def read_body(self):
        fp = self.fp
        for i in range(self.part_total_count):
            fp.seek(8 + self.pic_count * 12 + i * 16)
            self.parts.append(Part(fp.read(16)))

        for i in range(self.pic_count):
            fp.seek(8 + i * 12)
            pic = Pic(fp.read(12))
            pic.init_part(self.parts[pic.partid_start:pic.partid_start+pic.part_count])
            self.pics.append(pic)

    def init_old_image(self, path):
        fp = open(path, 'rb')
        img = Image.open(fp)
        return img

    # 写着玩的， 生成gif的玩意，毫无卵用
    # def save_gif(self, base):
    #     base_dir = f'lay_test/{base}/'
    #     if not os.path.exists(base_dir):
    #         os.mkdir(base_dir)
    #     body = None
    #     emotions = {}
    #     for p in self.pics:
    #         img = p.get_img(self.oldimg)
    #         if p.type == 'body':
    #             body = img
    #         elif p.type == 'face':
    #             emotions[p.id] = (img, [])
    #         elif p.type == 'mouth':
    #             emotions[p.id2][1].append(img)
    #
    #     for e in emotions:
    #         if not len(emotions[e][1]):
    #             return
    #
    #         for m in emotions[e][1]:
    #             i = body.copy()
    #             i.paste(emotions[e][0], (0, 0), emotions[e][0])
    #             i.paste(m, (0, 0), m)
    #             dir_path = f'{base_dir}{e}/'
    #             if not os.path.exists(dir_path):
    #                 os.mkdir(dir_path)
    #             i.save(f'{dir_path}/{emotions[e][1].index(m)}.png', )
    #
    #             frames = []
    #             pngFiles = os.listdir(dir_path)
    #             image_list = [os.path.join(dir_path, f) for f in pngFiles]
    #             for image_name in image_list:
    #                 # 读取 png 图像文件
    #                 frames.append(imageio.imread(image_name))
    #
    #             for i in frames[1:-1:-1]:
    #                 frames.append(copy.deepcopy(i))
    #             # 保存为 gif
    #             imageio.mimsave(dir_path+'g.gif', frames, 'GIF', duration=0.1)

class Pic():
    def __init__(self, raw):
        self.type = raw[3]
        if self.type == 0x00:
            self.type = 'body'
        elif self.type == 0x20:
            self.type = 'face'
        elif self.type == 0x40:
            self.type = 'mouth'

        if self.type == 'mouth':
            self.id2 = int(raw[1])

        self.id = int(raw[0])

        self.partid_start = struct.unpack('i', raw[4:8])[0]
        self.part_count = struct.unpack('i', raw[8:12])[0]

    def init_part(self, parts):
        self.parts = list(parts)
        self.left = int(min(p.new_x for p in self.parts))
        self.bottom = int(min(p.new_y for p in self.parts))
        self.right = int(max(p.new_x for p in self.parts))+32
        self.top = int(max(p.new_y for p in self.parts))+32
        self.width = self.right - self.left
        self.height = self.top - self.bottom

    def get_img(self, oldimg):
        img = Image.new('RGBA', (544, 544), '#00000000')
        for p in self.parts:
            w = round(p.old_x*oldimg.size[0])-1
            h = round(p.old_y*oldimg.size[1])-1
            piece = oldimg.crop((w, h, w+32, h+32))
            #piece.show()
            img.paste(piece, (int(p.new_x+544/2), int(p.new_y+544/2)))
        return img

    def save_img(self, oldimg, base_path):
        img = self.get_img(oldimg)
        id2 = ''
        if self.type == 'mouth':
            id2 = '_'+str(self.id)
            self.id = self.id2
        img.save(os.path.join(f'{base_path}/', f'{self.id}_{self.type}{id2}.png'),
                 format='png')

class Part():
    def __init__(self, raw):
        self.new_x = round(struct.unpack('f', raw[0:4])[0])
        self.new_y = round(struct.unpack('f', raw[4:8])[0])
        self.old_x = math.fabs(struct.unpack('f', raw[8:12])[0])
        self.old_y = math.fabs(struct.unpack('f', raw[12:16])[0])