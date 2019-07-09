"""
Created July 2019

@author Danny Sallurday

Script to generate plots for overhead stats averaged over a given range of dates.

"""

import os
import sys, time, datetime, string
import struct
import numpy as np
import sdb_mysql as mysql
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
plt.switch_backend('agg')

import run_blockvisitstats
from nightstats import getnightstats

if __name__=='__main__':
   elshost='db2.suth.saao.ac.za'
   elsname='els'
  # elsuser=os.environ['ELSUSER']
  # elspassword=os.environ['SDBPASS']
   sdbhost='sdb.salt'
   sdbname='sdb'
  # user=os.environ['SDBUSER']
  # password=os.environ['SDBPASS']

   sdb=mysql.mysql('sdbsandbox.cape.saao.ac.za', 'sdb_v7', 'danny', 'lemmein!', port=3306)

   sdate = sys.argv[1]
   edate = sys.argv[2]
   startdate = datetime.datetime(int(sdate[0:4]), int(sdate[4:6]), int(sdate[6:8]))
   enddate = datetime.datetime(int(edate[0:4]), int(edate[4:6]), int(edate[6:8]))
   date = startdate
   slewtotal=0
   trslewtotal=0
   targetacqtotal=0
   instracqtotal=0
   scitracktotal=0
   count=0
   while date <= enddate:
       obsdate = '%4i-%2s-%2s' % (date.year, str(date.month).zfill(2), str(date.day).zfill(2))
       #nightstats=getnightstats(sdb, obsdate)
       nightstats, numberofblocks = getnightstats(sdb, obsdate)
       date += datetime.timedelta(days=1)
       if len(nightstats) == 0 or numberofblocks == 0: continue
       else:
          count+=numberofblocks
          slewtotal+=nightstats[0]
          trslewtotal+=nightstats[1]
          targetacqtotal+=nightstats[2]
          instracqtotal+=nightstats[3]
          scitracktotal+=nightstats[4]
   if count == 0:
       print("No observation nights within this range")
       rangestats=[0]
   else:
       rangestats = {}
       #rangestats.update({'SlewTime' : slewtotal/count, 'TrackerSlewTime' : trslewtotal/count})
       #rangestats.update({'TargetAcquisitionTime':targetacqtotal/count})
       rangestats.update({'SlewTime' : slewtotal.median(), 'TrackerSlewTime' : trslewtotal.median()})
       rangestats.update({'TargetAcquisitionTime':targetacqtotal.median()})
       #rangestats.update({'InstrumentAcquisitionTime':instracqtotal/count, 'ScienceTrackTime': scitracktotal/count})

   #Produce a pdf with the relevant stats
   with PdfPages('blockoverheadstats-%s-%s.pdf' % (sdate, edate)) as pdf:
       df = pd.DataFrame([rangestats])
       ax = df.plot(kind="bar", stacked=True, figsize=(8.27,11.69))
       heights = []
       for patch in ax.patches:
           heights.insert(0, patch.get_height())
       i = 0
       while i < len(heights):
           if i+1 < len(heights):
               a = heights[i+1:]
               rest = sum(a)
           else:
               rest = 0
           ax.text(0, heights[i]+rest-25, \
                    str(round(heights[i],1)), fontsize=14, horizontalalignment='center',
                        color='white', fontweight='bold')
           i+=1
       ax.text(0, sum(heights)+5, \
                   str(round(sum(heights),1))+' (total)', fontsize=14, horizontalalignment='center',
                        color='black', fontweight='bold')
       ax.set_ylabel("Time (s)", fontweight='bold')
       ax.set_yticks(np.arange(0,1550,50))
       ax.set_xticklabels(['Average Overhead Time per Block'], rotation='horizontal', fontweight='bold')
       ax.set_title('Overhead Statistics for %s to %s' % (sdate,edate),fontweight='bold')
       pdf.savefig() # saves the current figure into a pdf page
       plt.show()
       plt.close()
