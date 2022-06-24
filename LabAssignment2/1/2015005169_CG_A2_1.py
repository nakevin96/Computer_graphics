import numpy as np
#2015005169_최윤석
#ComputerGraphics
#Labassginment_2



#1-A
m=np.arange(2,27)
print(m)
print()

#1-B
m=m.reshape(5,5)
print(m)
print()

#1-C
m[1:4, 1:4]=0
print(m)
print()

#1-D
m=m@m
print(m)
print()

#1-E
v=m[0,:]
v*=v
vnum=np.sum(v)
vnum=np.sqrt(vnum)
print(vnum)