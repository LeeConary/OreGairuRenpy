# 用来放替换信息的

import math

# 为了方便写所以搞了个这个，加一个替换就复制粘贴2333
def sub_plate(matchobj):
    pass

def sub_callfar(matchobj):
    global_label = int(matchobj.group(1))-1
    local_label = int(matchobj.group(2))
    return f'call global_{global_label}.label_{local_label}'

#TODO:增加说话者
def sub_mes(matchobj):
    chara_id_sign = int(matchobj.group(1))
    chara_id = -1
    if chara_id_sign == 4:
        chara_id = 0
    elif chara_id_sign == 10:
        chara_id = 1
    elif chara_id_sign == 3:
        chara_id = 2

    str_id = matchobj.group(2)

    if chara_id == -1:
        return f'"StringRef({str_id})"'

    return f'''$ charas_say[{chara_id}] = True
    "StringRef({str_id})"
    $ charas_say[{chara_id}] = False
    '''

def sub_voice_mes(matchobj):
    voice_id = matchobj.group(1)
    anim_id = matchobj.group(2)
    chara_id_sign = int(matchobj.group(3))
    chara_id = -1
    if chara_id_sign == 4:
        chara_id = 0
    elif chara_id_sign == 10:
        chara_id = 1
    elif chara_id_sign == 3:
        chara_id = 2

    str_id = matchobj.group(4)

    if chara_id == -1:
        return f'play sound "voice/{voice_id}.ogg"\n\t"StringRef({str_id})"'

    return f'''play sound "voice/{voice_id}.ogg"
    $ charas_say[{chara_id}] = True
    "StringRef({str_id})"
    $ charas_say[{chara_id}] = False
    '''
# 全局变量都有各自的含义，目前已知的重要全局变量有：
# 37：bg图片id
# 5260,5300,5340：人物立绘的x坐标
# 5261,5301,5341：人物立绘的y坐标
#TODO:优化+美化，现在写的都不知道是些什么鬼东西
def sub_assign(matchobj):
    v_type = matchobj.group(1)
    if v_type == '37':
        if matchobj.group(2).find('GlobalVars') > -1:
            return '#copy bg'
        bgid = int(matchobj.group(2))
        if bgid > 0:
            return f'scene expression "bg/{bgid}.png"'
        elif bgid == -16777216 or bgid == -1:
            return f'scene expression "#000"'
        else:
            return f'#scene bg {bgid}'
    elif v_type == '5260' or v_type == '5340' or v_type == '5300':
        if matchobj.group(2).find('GlobalVars') > -1:
            return '#"copy pos"'
        buffer_id = int((int(v_type) - 5260) / 40)
        xoffset = int(matchobj.group(2))
        return f'show c{buffer_id}:\n\t\txpos {xoffset}'
    elif v_type == '5261' or v_type == '5341' or v_type == '5301':
        if matchobj.group(2).find('GlobalVars') > -1:
            return '#"copy pos"'
        buffer_id = int((int(v_type) - 5261) / 40)
        yoffset = int(matchobj.group(2)) + 544/2
        return f'show c{buffer_id}:\n\t\typos {yoffset}'
    else:
        return f'#GlobalVars[{v_type}] = {matchobj.group(2)}'

# 替换显示人物指令，需要和人物显示脚本相配合，由于人物需要更改，所以这里还需要改动
def sub_loadcha(matchobj):
    buffer_id = int(math.log(int(matchobj.group(2)), 2)) - 4
    chara_id = int((int(matchobj.group(3)) % 65536) / 2)
    emotion_id = int((int(matchobj.group(3)) - chara_id) / 65536)
    return f'''$ charas[{buffer_id}] = {chara_id}
    $ charas_body[{buffer_id}] = chara_infos[{chara_id}][0]
    $ charas_face[{buffer_id}] = {emotion_id}
    $ charas_mouth[{buffer_id}] = chara_infos[{chara_id}][1][{emotion_id}]
    show c{buffer_id}#loadcha'''

def sub_if(matchobj):
    s = 'if'
    s += ' ' if matchobj.group(1) == '1' else ' not '
    s += matchobj.group(2) + ':\n\t\t'
    s += f'jump .label_{int(matchobj.group(3))}'
    return s

# 需要替换的指令
# TODO:重新排序，这样看着有一些乱
# TODO:似乎光用正则已经不能满足需求了
reg_dict = {
    '!CallFar': (r'CallFar\(target: FarLabelRef\((\d+), (\d+)\), returnAddress: ReturnAddressRef\((\d+)\)\)',
                sub_callfar),
    'SetFlag': (r'SetFlag\(flag: FlagRef\((\d+)\)\)',
                r'$ flag_\1 = True'),
    'ResetFlag': (r'ResetFlag\(flag: FlagRef\((\d+)\)\)',
                  r'$ flag_\1 = False'),
    'BGMplay': (r'BGMplay\(loop: (\d+), track: (\d+)\)',
                r'play music "bgm/\2.ogg"'),
    'BGMstop': (r'BGMstop\(zero: 0\)',
                r'stop music'),
    'FlagOnWait': (r'FlagOnWait\(condition: (\d+), flag: FlagRef\((\d+)\)\)',
                   r'if flag_\2:\n\t\tpause'),
    'FlagOnJump': (r'FlagOnJump\(condition: (\d+), flag: FlagRef\((\d+)\), target: LocalLabelRef\((\d+)\)\)',
                   r'if flag_\2:\n\t\tjump .label_\3'),
    'Jump': (r'Jump\(target: LocalLabelRef\((\d+)\)\)',
             r'jump .label_\1'),
    'SEplay': (r'SEplay\(channel: (\d+), type: (\d+), effect: (\S+), loop: (\d+)\)',
               r'play sound "se/\3.ogg"'),
    'SetEVflag': (r'SetEVflag\(EVflag: (\d+)\)',
                  r'$ ev = \1'),
    'Mwait': (r'Mwait\(delay: (\d+), unused: 0\)',
              r'pause'),
    'Mes_LoadVoicedDialogue': (r'Mes_LoadVoicedDialogue\(audioId: (\d+), animationId: (\S+), characterId: (\S+), line: StringRef\((\d+)\)\)',
                               sub_voice_mes),
    'Mes_LoadDialogue': (r'Mes_LoadDialogue\(characterId: (\S+), line: StringRef\((\d+)\)\)',
                        sub_mes),
    'CHAload': (r'CHAload\(type: (\d+), bufferId: (\d+), spriteId: (\d+), unused: 2832\)',
               sub_loadcha),
    'Return': (r'Return',
               r'return'),
    'End': (r'End',
            r'return'),
    'ScriptLoad': (r'ScriptLoad\(scriptBuffer: (\d+), scriptFile: (\d+)\)',
                   r'call global_\2'),
    'GlobalVars': (r'GlobalVars\[(\d+)\] = (\S+)',
                   sub_assign),
    'If': (r'If\(conditionExpectedTrue: (\d+), condition: ([^,]+), target: LocalLabelRef\((\d+)\)\)',
                   sub_if),
}

# 这些指令由于没什么卵用，所以直接删掉
useless_inss = [
    'MesVoiceWait',
    'MessWindow_AwaitShowCurrent',
    'MessWindow_ShowCurrent',
    'MesSetID_SetSavePoint',
    'MesMain_DisplayDialogue',
    'MessWindow_Hide',
    'MessWindow_AwaitHideCurrent',
    'AutoSave_05',
    'AutoSave_SaveState'
]