# The script of the game goes in this file.

# Declare characters used by this game. The color argument colorizes the
# name of the character.

define e = Character("Eileen")
image bg 1 = "bg/1.png"

define interval = 0.1

define charas_say = [False]*3
define charas = [0]*3
define charas_body = [1]*3
define charas_face = [1]*3
define charas_mouth = [[]]*3
define charas_x = [480]*3
define charas_y = [544]*3

define m = [0.0]*3
define ma = [0]*3


init python:
    def draw_chara(st, at, id):
        global m, ma, charas_x, charas_y
        print(id)
        print(charas[id])
        if charas_say[id] and len(charas_mouth[id]):
            m[id] += 0.6
            m[id] %= len(charas_mouth[id])
        ma[id] = int(m[id])

        composites = []
        if charas_body[id] != None:
            composites.append((0, 0))
            composites.append("chara/%d/%d_body.png"%(charas[id], charas_body[id]))
        if charas_face[id] != None:
            composites.append((0, 0))
            composites.append("chara/%d/%d_face.png"%(charas[id], charas_face[id]))
        if len(charas_mouth[id]) > 0:
            composites.append((0, 0))
            composites.append("chara/%d/%d_mouth_%d.png"%(charas[id], charas_face[id], charas_mouth[id][ma[id]]))

        return LiveComposite((charas_x[id], charas_y[id]), *composites), interval

image c0 = DynamicDisplayable(draw_chara, 0)
image c1 = DynamicDisplayable(draw_chara, 1)
image c2 = DynamicDisplayable(draw_chara, 2)
# The game starts here.

label start:
    $ charas[0] = 18
    show c0
    pause



    jump global_7

    return
