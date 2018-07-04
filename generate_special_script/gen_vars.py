with open('../OreGairu/game/flag.rpy', 'w', encoding='utf8') as fp:
    for i in range(5000):
        fp.write(f'default flag_{i} = False\n')

with open('../OreGairu/game/globalvar.rpy', 'w', encoding='utf8') as fp:
    fp.write(f'define GlobalVars = [0]*10000\n')

with open('../OreGairu/game/threadvar.rpy', 'w', encoding='utf8') as fp:
    fp.write(f'define ThreadVars = [0]*1000\n')