
loginString = """<?xml version="1.0" encoding="utf-8" ?>
  <env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">
    <env:Body>
      <n1:login xmlns:n1="urn:partner.soap.sforce.com">
        <n1:username>{username}</n1:username>
        <n1:password>{password}</n1:password>
      </n1:login>
    </env:Body>
  </env:Envelope>"""

jobstring = """
<?xml version="1.0" encoding="UTF-8"?>
<jobInfo
    xmlns="http://www.force.com/2009/06/asyncapi/dataload">
  <operation>{operation}</operation>
  <object>{object}</object>
  <concurrencyMode>{concurrency}</concurrencyMode>
  <contentType>{contenttype}</contentType>
</jobInfo>"""


closeJobString = """
<?xml version="1.0" encoding="UTF-8"?>
<jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload">
  <state>Closed</state>
</jobInfo>"""

queryResultsString = """
<result-list xmlns="http://www.force.com/2009/06/asyncapi/dataload">
<result>{resultid}</result>
</result-list>
"""

def createloginSOAP(username,password):
	return loginString.format(username=username,password=password)

def createjobstring(operation,object,concurrency="Parallel",contenttype="CSV"):
  return jobstring.format(operation=operation,object=object,concurrency=concurrency,contenttype=contenttype)

def createresultstring(resultid):
  return queryResultsString.format(resultid=resultid)
