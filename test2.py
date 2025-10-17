


old = [['lund',1],['bhund',2],['bhoot',3],['choot',4]]
new = [['lund',1],['bhund',2],['bhoot',3],['choot',4],['gaand',5]]

for n in new:
    if n in old:
        pass
    else:
        print(f'{n} is opened')
for o in old:
    if o in new:
        pass
    else:
        print(f'{o} is closed')
