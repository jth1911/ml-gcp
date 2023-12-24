import yaml

d = {'a':1, 'b':2}
for key,val in d.items():
        exec(key + '=val')