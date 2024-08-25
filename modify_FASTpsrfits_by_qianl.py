import types
import numpy as np 
import pyfits
import os
import datetime
import time
import sys
from array import array
import matplotlib as mpl
import matplotlib.pyplot as plt
from pylab import *


#------------------------------------------------------------------
# Written by Lei QIAN
# created long ago, commented on 20190930
# version 20190930
# modify the header of FAST psrfits file
# Usage: 
#       python modify_FASTpsrfits.py FAST.fits keyfile
# Usage: 
#       python modify_FASTpsrfits.py FAST.fits key.txt
#------------------------------------------------------------------

#mpl.rcParams['image.interpolation']='none'
if (len(sys.argv)<3):
  print 'too few inputs!'
  print 'example:'
  print 'python modify_FASTpsrfits.py FAST.fits keyfile'
  sys.exit()

starttime=datetime.datetime.now()

filename=sys.argv[1]
keyfile=sys.argv[2]



#u19700101=62135683200.0

hdulist = pyfits.open(filename)

hdu0 = hdulist[0]
data0 = hdu0.data
header0 = hdu0.header
#print len(hdulist[0].header)
#help(hdulist[0].header)
#for i in range(len(hdulist[0].header)):
#    print hdulist[0].header[i]

hdu1 = hdulist[1]
data1 = hdu1.data
header1 = hdu1.header
#print hdu1.header['CHAN_BW']
#hdu1.header['CHAN_BW']=0.25
#print hdu1.header['CHAN_BW']

#help(hdulist[1].header.keys)
#help(hdulist[1].header.values)
#help(hdulist[1].header.comments)
#print hdulist[1].header.comments[0]

print hdulist[1].header.keys()[0]

#print hdulist[1].header.values
#for i in range(len(hdulist[1].header)):
#    print hdulist[1].header[i]

flag0=0
flag1=0

for line in open(keyfile):
    #key=line.replace('\n','').split(",")[0].strip()
    #tempvalue=line.replace('\n','').split(",")[1].strip()
    line1=" ".join(line.split())
    key=line1.replace('\n','').split(" ")[0].strip()
    tempvalue=line1.replace('\n','').split(" ")[1].strip()
    for i in range(len(hdulist[0].header)):
        if (hdulist[0].header.keys()[i]==key):
           flag0=1
    for i in range(len(hdulist[1].header)):
        if (hdulist[1].header.keys()[i]==key):
           flag1=1
#    if (key in hdulist[0].header.keys()):
#        flag0=1
#    if (key in hdulist[1].header.keys()):
#        flag1=1

    #print type(hdu0.header[key])
    if(flag0==1):
        if isinstance(hdu0.header[key],int):
           hdu0.header[key]=int(tempvalue)
           print key,tempvalue,hdu0.header[key]
           flag0=0
        else:
           if isinstance(hdu0.header[key],float):
              hdu0.header[key]=float(tempvalue)
              print key,tempvalue,hdu0.header[key]
              flag0=0
           else:
              if isinstance(hdu0.header[key],str):
                 hdu0.header[key]=tempvalue
                 print key,tempvalue,hdu0.header[key]
                 flag0=0

    if(flag1==1):
        if isinstance(hdu1.header[key],int):
           hdu1.header[key]=int(tempvalue)
           print key,tempvalue,hdu1.header[key]
           flag1=0
        else:
           if isinstance(hdu1.header[key],float):
              hdu1.header[key]=float(tempvalue)
              print key,tempvalue,hdu1.header[key]
              flag1=0
           else:
              if isinstance(hdu1.header[key],str):
                 hdu1.header[key]=tempvalue
                 print key,tempvalue,hdu1.header[key]
                 flag1=0


key='OBSFREQ'
hdu0.header[key]=1.0
print hdu0.header[key]




hdulist2 = pyfits.HDUList([hdu0,hdu1])
os.system('rm -f FASTpsrfits_out.fits')
hdulist2.writeto('FASTpsrfits_out.fits')



print '--------------------------------------------'
print '             Finished!                      '


endtime=datetime.datetime.now()
print 'START:',starttime
print 'END:',endtime
duration=endtime-starttime
print 'DURATION:',duration.seconds,' sec'

