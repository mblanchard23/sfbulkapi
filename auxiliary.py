import time
import requests
import settings_file
import soaprequests
import json
import datetime
import sqlite3

my_settings = json.loads(settings_file.settingsdict)
instance = my_settings['instance']
conn = sqlite3.connect(my_settings["sqlitedirectory"] + '/jobtracker.sqlite')
lc = conn.cursor()

username = my_settings['username']
if my_settings['password']: # Looks for a password by default
  password = my_settings['password'] + my_settings['token'] 
elif my_settings['b64_password'] :
  password = my_settings['b64_password'].decode('base64') + my_settings['token'] 
else:
  print "Password required!"


def getXMLData(xmlstring,tagName):
  #XML Parser
  q = xmlstring.split('<'+tagName+'>')

  if len(q)> 1:
    return q[1].split('</'+tagName+'>')[0]
  else:
    return None 

class sfSession:
  #Grabs the SessionId and ensure it's kept valid
  def __init__(self,username=username,password=password):
    self.username = username
    self.password = password
    self.instance = "na10" # Need to get this to populate from sessiondetails

    self.sessiondetails = self.login(self.username,self.password)
    self.sessionId = self.sessiondetails['sessionId']
    self.expirytime = datetime.datetime.now() + datetime.timedelta(seconds=int(self.sessiondetails['sessionSecondsValid']) - 60) 
    # Take off 60 seconds to acount for computer time lag



  def login(self,username, password):
    #Returns a dictionary of metadata retrieved from authenticating with Salesforce
    request = soaprequests.createloginSOAP(username,password)
    session_details = {} 
    encoded_request = request.encode('utf-8')
    url = "https://login.salesforce.com/services/Soap/u/30.0"
    
    headers = {"Content-Type": "text/xml; charset=UTF-8",
               "SOAPAction": "login"}
                               
    response = requests.post(url=url,
                             headers = headers,
                             data = encoded_request,
                             verify=True)

    session_details['sessionId'] = getXMLData(response.text,'sessionId')
    session_details['passwordExpired'] = getXMLData(response.text,'passwordExpired')
    session_details['sessionSecondsValid'] = getXMLData(response.text,'sessionSecondsValid')

    return session_details

  def isExpired(self):
    if self.expirytime > datetime.datetime.now():
      return False
    else:
      return True

  def refreshToken(self):
    self.sessiondetails = self.login(self.username,self.password)
    self.sessionId = self.sessiondetails['sessionID']
    self.expirytime = datetime.datetime.now() + datetime.timedelta(seconds=self.sessiondetails['sessionSecondsValid'] - 60)

  def getheaders(self,content_type="application/xml; charset=UTF-8"):

    if self.isExpired():
      self.refreshToken()
  
    headers = {"X-SFDC-Session": self.sessionId, 
                 "Content-Type": content_type}
    return headers


  def __repr__(self):
    return str(self.sessionId)



class sfJob:
  def __init__(self,operation='',object='',session='',jobid=""):

    #Create new job
    if not jobid:

      postdata = soaprequests.createjobstring(operation=operation
                                                ,object=object
                                                ,concurrency="Parallel"
                                                ,contenttype="CSV")
      postdata = postdata.encode('utf-8')
      url = "https://" + session.instance + ".salesforce.com/services/async/30.0/job"
      self.session = session
      self.operation = operation
      self.object = object
      self.batches = {}       
      headers = self.session.getheaders()
                                 
      response = requests.post(url=url,headers=headers,data=postdata,verify=True)
      self.updateSelf(response.text)
      insertstr = "insert into jobs values('%s','%s','%s','%s','%s')" % (self.jobid,self.state,self.createdDT,self.operation,self.object)
      lc.execute(insertstr)
      conn.commit()

    #Retrieve old job. Once Job ID is passed, all the regular Job attributes of the old job are updated
    else:
      self.jobid = jobid
      self.session = session
      self.updateSelf(self.getJobUpdate())
      self.operation= 'Unknown'
      self.object = 'Unknown'

  def updateSelf(self,xml_response_text):

    self.jobid = getXMLData(xml_response_text,'id')
    self.createdby = getXMLData(xml_response_text,'createdById')
    self.createdDT = getXMLData(xml_response_text,'createdDate')
    self.numberBatchesQueued = getXMLData(xml_response_text,'numberBatchesQueued')
    self.numberBatchesInProgress = getXMLData(xml_response_text,'numberBatchesInProgress')
    self.numberBatchesCompleted = getXMLData(xml_response_text,'numberBatchesCompleted')
    self.numberBatchesFailed = getXMLData(xml_response_text,'numberBatchesFailed')
    self.numberBatchesTotal = getXMLData(xml_response_text,'numberBatchesTotal')
    self.state = getXMLData(xml_response_text,'state')
    self.numberRecordsProcessed = getXMLData(xml_response_text,'numberRecordsProcessed')
    self.numberRetries = getXMLData(xml_response_text,'numberRetries')
    self.operation = getXMLData(xml_response_text,'operation')
    self.apiVersion = getXMLData(xml_response_text,'apiVersion')
    self.numberRecordsFailed = getXMLData(xml_response_text,'numberRecordsFailed')
    self.totalProcessingTime = getXMLData(xml_response_text,'totalProcessingTime')
    self.apiActiveProcessingTime = getXMLData(xml_response_text,'apiActiveProcessingTime')
    self.apexProcessingTime = getXMLData(xml_response_text,'apexProcessingTime')
    self.jobInfo = getXMLData(xml_response_text,'jobInfo')
    self.operation = getXMLData(xml_response_text,'operation')
    self.object = getXMLData(xml_response_text,'object')
    return None


  def addbatch(self,postdata):
    session = self.session
    url = "https://" + session.instance + ".salesforce.com/services/async/30.0/job/{jobid}/batch".format(jobid=self.jobid)
    # headers = {"X-SFDC-Session": session.sessionId, 
    #            "Content-Type": "text/csv; charset=UTF-8"}
    headers = self.session.getheaders('text/csv; charset=UTF-8')
    response = requests.post(url=url,
                             headers = headers,
                             data = postdata,
                             )
    batchId = getXMLData(response.text,'id')
    self.unfinished_business = True
    self.batches[batchId] = {}
    self.batches[batchId]['jobID'] = getXMLData(response.text,'jobId')
    self.batches[batchId]['state'] = getXMLData(response.text,'state')
    self.batches[batchId]['numberRecordsProcessed'] = getXMLData(response.text,'numberRecordsProcessed')
    self.batches[batchId]['numberRecordsFailed'] = getXMLData(response.text,'numberRecordsFailed')

    return response.text

  def getJobUpdate(self):
    session = self.session
    url = "https://{instance}.salesforce.com/services/async/30.0/job/{jobid}".format(instance=session.instance,jobid=self.jobid)

    headers = self.session.getheaders()

    response = requests.get(url=url,headers=headers)
    return response.text

  def getbatchinfo(self,batchid):
    session = self.session
    url = "https://{instance}.salesforce.com/services/async/30.0/job/{jobid}/batch/{batchid}"

    headers = self.session.getheaders()

    url = url.format(instance=session.instance,jobid=self.jobid,batchid=batchid)
    response = requests.get(url=url,headers=headers)

    return response.text

  def updatebatch(self):
    if self.batches:
      for key in self.batches:
        newdata = self.getbatchinfo(key)
        self.batches[key]['state'] = getXMLData(newdata,'state')
        self.batches[key]['numberRecordsProcessed'] = getXMLData(newdata,'numberRecordsProcessed')
        self.batches[key]['numberRecordsFailed'] = getXMLData(newdata,'numberRecordsFailed')

        if getXMLData(newdata,'stateMessage'):
          self.batches[key]['stateMessage'] = getXMLData(newdata,'stateMessage')

    return None

  def getresultlists(self,batchid):
    session = self.session
    url = "https://{instance}.salesforce.com/services/async/30.0/job/{jobid}/batch/{batchid}/result"
    url = url.format(instance=session.instance,jobid=self.jobid,batchid=batchid)
    headers = self.session.getheaders()

    response = requests.get(url=url,headers=headers) # returns results list xml
    
    response_expl = response.text.split('<result>')
    result_list = []
    for i in range(1, len(response_expl)):
      result_elem = response_expl[i]
      result_list.append(result_elem.split('</result>')[0])

    self.batches[batchid]['results'] = result_list 
    

  def getresults(self,batchid,resultid):
    if 'output' not in self.batches[batchid]:
      self.batches[batchid]['output'] = []

    session = self.session
    url = "https://{instance}.salesforce.com/services/async/30.0/job/{jobid}/batch/{batchid}/result/{resultid}"
    url = url.format(instance=session.instance,jobid=self.jobid,batchid=batchid,resultid=resultid)
    print url

    headers = self.session.getheaders()

    response = requests.get(url=url,headers=headers)
    self.batches[batchid]['output'].append(response.text)
    return response.text



  def closeJob(self):
    session = self.session
    postdata = soaprequests.closeJobString
    url = "https://" + session.instance + ".salesforce.com/services/async/30.0/job/" + self.jobid

    headers = self.session.getheaders()

    response = requests.post(url=url,headers=headers,data=postdata)

    if getXMLData(response.text,'state') == 'Closed':
      self.state = 'Closed'
      updatedb= "update jobs set state = '%s' where jobid = '%s'" % (self.state,self.jobid)
      lc.execute(updatedb)
      conn.commit()
    return response.text

    def describe(self):
       description = "ID: {jobid}\nOperation: {operation}\nSalesforce Object: {sfobject}"
       return description.format(jobid=self.jobid,operation=self.operation,sfobject=self.object)


def cleanup(auto=False):
  lc.execute("select jobid,operation,object,created_at from jobs where state = 'Open'")
  results = lc.fetchall()
  print results


  if results:
    
    if auto:    
      sf = sfSession()
      for row in results:
        jobid = row[0]
        job = sfJob(jobid=jobid,session=sf)
        job.closeJob()
      return None
    else:
      return None

    user_input = raw_input("Would you like to close these jobs? (Y/N): ")

    if user_input.upper() == 'Y':
      sf = sfSession()
      for row in results:
        jobid = row[0]
        job = sfJob(jobid=jobid,session=sf)
        job.closeJob()
      return None
    else:
      return None
