import auxiliary
from auxiliary import sfSession, sfJob
import time


def runtest():
  sf = sfSession()


  mj = sfJob('query','user',sf)
  mj.addbatch("select id from user")
  mj.closeJob()
  mj.updatebatch()
  print "BATCH RUNDOWN:\n\n" + str(mj.batches)
  incomplete = True
  counter = 0

  while incomplete:
    counter += 1
    print "Attempt no. %d" % counter
    time.sleep(10)
    mj.updatebatch()
    print mj.batches
    incomplete = False
    for batch in mj.batches:
      if mj.batches[batch]['state'] in ('Queued','InProgress'):
        incomplete = True

  for batch in mj.batches:
    if mj.batches[batch]['state'] == 'Completed':
      mj.batches[batch]['results'] = mj.getqueryresultlist(batch)

  for batch in mj.batches:
    for result in mj.batches[batch]['results']:
      print mj.getresults(batch,result)

  return mj
