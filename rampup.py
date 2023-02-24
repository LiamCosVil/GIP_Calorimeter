from mcculw import ul
import time
import matplotlib.pyplot as plt
from ALR32XX.ALR32XX import *

ps = ALR32XX("ALR3206D")
ps.MODE("NORMAL")

ps.OUT(1,1)

for i in range(15):
    print(5+i/2)
    ps.Ecrire_tension(5+i/2,1)
    time.sleep(30)

ps.OUT(0,1)

