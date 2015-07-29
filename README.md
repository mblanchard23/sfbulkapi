# sfbulkapi
Introduces 2 Python classes sfJob and sfSession to help use the Salesforce Bulk API.
Full documentation for Salesforce Bulk API can be found here: https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/

You should pay particular attention to the section about "When to use Bulk API" and How to Structure your Batches.

<header><b>WORKFLOW</b></header>

1) Create a Job. A job must relate to a specific operation/verb (QUERY,INSERT,UPSERT,UPDATE,DELETE) and an Object in your Salesforce instance

2) Add batches to your job. Batches must be relevant to the verb/object specified in one

3) CLose the job (starts processing)

4) Retrieve results (when querying)

<b>CLASSES</b><br>
<b>sfSession()</b> - <i>Creates an object storing the users credentials used to authenticate with each API call. Upon initiation uses the username, password and security token stored in the settings_file <br>
<b>METHODS</b><br>
.login(username,password) - password needs to be concatenated with the token<br>
.refreshToken() - refreshes the sessionId<br>
.getheaders(content_type) - Creates headers dictionary used with every API request. Content type defaults application/xml<br>
.isExpired() - returns a T/F value based on current time vs expiry time<br>
</i>

<b>EXAMPLES</b> <br>
1) <i>Run SOQL Query on the User object </i>

```python
sf = sfSession()
job = sfJob('query','user',sf)
job.addbatch('select id,name from user') # Returns SF ID and Fullname for all users

#Polling the status of the batches
while processing == True:
	# All batches must have finished to progress
	attemptnumber += 1
	time.sleep(10)
	processing = False
	print 'Refresh number %d' % attemptnumber
	job.updatebatch()
	print job.batches #Informtion for each batch is stored in the dictionary job.batches with batch ID as key
	for key in job.batches:
		if job.batches[key]['state'] in ('Queued','InProgress'):
			processing = True

#Returns a list of the result IDs and adds them to the
for key in job.batches:
	job.getresultlists(key)

for key in job.batches:
	for resultid in job.batches[key]['results']:
		job.getresults(key,resultid)

#Call job.batches[batchid]['output'] to get the csv response


```

2) <i>Update Opportunity records </i>

