import auxiliary
from auxiliary import sfSession, sfJob
import time



def runsoqltest():
  sf = sfSession()
  job = sfJob('query','user',sf)
  job.addbatch('select id,name from user limit 50')
  job.closeJob()
  job.updatebatch()
  attemptnumber = 0
  print job.batches

  for key in job.batches:
    if job.batches[key]['state'] not in ('Queued','InProgress'):
      processing = False
      break
    else:
      processing = True
      break


  while processing == True:
    # All batches must finish to progress
    attemptnumber += 1
    time.sleep(10)
    processing = False
    print 'Refresh number %d' % attemptnumber
    job.updatebatch()
    print job.batches
    for key in job.batches:
      if job.batches[key]['state'] in ('Queued','InProgress'):
        processing = True


  for batchid in job.batches:
    job.getresultlists(batchid)


  # getresults() saves the result output to a dictionary - should get rid of this to save memory
  for batchid in job.batches:
    for resultid in job.batches[batchid]['results']:
      job.getresults(batchid,resultid)

  query_result = ''
  headers = ''
  for batchid in job.batches:
    for result_out in job.batches[batchid]['output']:
      # TODO: Grab table headers (row 1) and append to beginning
      if not headers:
        headers = result_out[:result_out.find('"\n"')] # Gives everything up to the end of the first line (header row)

      query_result += result_out[result_out.find('"\n"')+2:] #Appends the data without headers
      

  query_result = query_result.replace('","','\t') # Convert to tab separated
  query_result = query_result.replace('"\n"','\n')[1:] # Trims the first quote

  if query_result[-1] == '\n' and query_result[-2] == '"': # trims the final carriage return and quote
    return query_result[0:len(query_result)-2]
  else:
    return query_result
