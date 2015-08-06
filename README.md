# sfbulkapi

Introduces 2 Python classes sfJob and sfSession to help use the Salesforce Bulk API.

Full documentation for Salesforce Bulk API can be found here: https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/

You should pay particular attention to the section about "When to use Bulk API" and How to Structure your Batches.

## Workflow

1) Create a Job. A job must relate to a specific operation/verb (QUERY,INSERT,UPSERT,UPDATE,DELETE) and an Object in your Salesforce instance

2) Add batches to your job. Batches must be relevant to the verb/object specified in one

3) CLose the job (starts processing)

4) Retrieve results (when querying)

## Classes

### sfSession()

Creates an object storing the users credentials used to authenticate with each API call. Upon initiation uses the username, password and security token stored in the settings_file <br>

#### Methods

.login(username,password) - password needs to be concatenated with the token

.refreshToken() - refreshes the sessionId

.getheaders(content_type) - Creates headers dictionary used with every API request. Defaults to application/xml

.isExpired() - returns a T/F value based on current time vs expiry time

### sfJob (operation,object,session,jobid)

Creates a Job class to handle the Bulk Api Job process. A new job is created if jobid is left blank. Entering an old job id loads a previous job into the class instance

#### Methods & Properties

.addbatch(postdata) - Creates batch and send the data to Salesforce via POST 

.batches - A dictionary containing all batches in the current job with metadata with Batch ID used as the key 

.updatebatch() - Refreshes the status of the batches running in the current job

.getresultlists(batchid) - Attempts to retrieve the list of result IDs for the batch, appends to the .batches dictionary

.getresults(batchid,resultid) - (When querying) Retrieves results for the batch and appends to .batches dictionary 

.closeJob() - Closes the job, no more batches can be added after this method has run

Note, most of the metadata for the job is saved as an attribute on the job, for a full list see Bulk API Docs

## Examples

1) *Run SOQL Query on the User object*

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
	#Batch info added to the dictionary job.batches with batch ID as the key
	print job.batches 
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

2) *Update Opportunity records*

