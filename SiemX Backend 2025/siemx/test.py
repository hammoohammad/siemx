l = False
msg = 'Hello i am reating siemx'
if any(word in msg for word in ['ERROR', 'try', 'batch']):
    l = True
print(l)