import sys
import time

 = None
try:
     = open(".txt")
    #     
    while True:
         = .readline()
        if len() == :
            break
        print(, end='')
        sys.stdout.flush()
        print(" +c  ")
        #     
        time.sleep(5)
except IOError:
    print(".txt   ")
except KeyboardInterrupt:
    print("!!    .")
finally:
    if :
        .close()
    print("( :  )")
