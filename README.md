# sfbulkapi
Introduces 2 Python classes sfJob and sfSession to help use the Salesforce Bulk API.
Full documentation for Salesforce Bulk API can be found here: https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/

You should pay particular attention to the section about "When to use Bulk API" and How to Structure your Batches.

WORKFLOW

1) Create a Job. A job must relate to a specific operation/verb (QUERY,INSERT,UPSERT,UPDATE,DELETE) and an Object in your Salesforce instance

2) Add batches to your job. Batches must be relevant to the verb/object specified in one

3) CLose the job (starts processing)

4) Retrieve results (when querying)

EXAMPLES:
Example 1) Run SOQL Query

Example 2) Update Opportunity records

