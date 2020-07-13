#!/usr/bin/env python
# coding: utf-8

# In[14]:


import boto3
import botocore
import os
from datetime import datetime, timezone
from configparser import ConfigParser
import keyring

def version():
    return '2.2'

def readConfig(section,key,default = '',config_file = 'config.ini'):
    # Read Configuration settings saved on local drive (E.g. LastRun_utc)
    # returns value
    value = default
    if os.path.exists(config_file) == False:
        writeConfig(section,key,value)  
        
    try:
        
        config = ConfigParser()
        config.read(config_file)
        value = config.get(section, key)
    except:
        writeConfig(section,key,value)  
        value = default
        
        
    return value

def writeConfig(section,key,value,config_file = 'config.ini'):
    # Write Configuration settings - saved to local drive (E.g. LastRun_utc)
    config = ConfigParser()
    config.read(config_file)
    if config.has_section(section) == False:
        config.add_section(section)
    config.set(section, key, value)
    with open(config_file, 'w') as f:
        config.write(f)
        
def make_dir(dirname):
    # Check and create directories if necessary
    # Default ShareBox Directory
    # Folders needed on download to keep directory structure (Sync)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        
def getEssentials(boxpath =''):
    
    # returns required values to be used with AWS
    # and the local ShareBox path
    keysdatafile = 'awskeys.txt'
    bucketname = 'uab-dropbox'
    
    if boxpath =='':
        # Go to ShareBox folder in user Documents Directory
        documentspath = os.path.join(os.path.expanduser('~'),"Documents\\")    
        boxpath = os.path.join(documentspath,"ShareBox\\")  
        
    # Create one if it does not exist
    make_dir(boxpath)
    
    return keysdatafile,bucketname,boxpath

def ReadCredentials(datafile):
    # read AWS credentials
    keyID=secretID=sessionToken=''
    
    with open(datafile) as f:
        i = 0
        for line in f:
            line = line.split("=") 
            if line:
                if i == 0: # aws_access_key_id
                    keyID = line[1].rstrip('\n')
                if i == 1: # aws_secret_access_key 
                    secretID= line[1].rstrip('\n')      
                if i == 2: # aws_session_token
                    sessionToken = line[1].rstrip('\n')    
                i += 1

    return keyID,secretID,sessionToken

def Add2Dictionary(subdir,org):
    if len(subdir)==0:
        isValid = False
    elif subdir.startswith(org)==False:
        isValid = False
    else:
        isValid = True  
    return isValid

def listLocalDir(dirPath,boxPath,my_lst,org):
    # returns list of files and folders in local ShareBox directory
    entities = os.listdir(dirPath) # File or Folder
    for entity in entities:
        fullpath = os.path.abspath(os.path.join(dirPath,entity))
        isFile = os.path.isfile(fullpath)
        if isFile == False:
            listLocalDir(fullpath,boxpath,my_lst,org)
        else:
            EntityPath = fullpath.replace(boxpath,'').replace(entity,'')
            if len(EntityPath) !=0:
                if EntityPath[-1] =='\\':
                    EntityPath = EntityPath[:-1]
            EntityPath = EntityPath.replace('\\','/')       
            my_dict = {'File':entity,'SubDir':EntityPath}
            if Add2Dictionary(EntityPath,org) == True:
                my_lst.append(my_dict)
    return my_lst

def listS3Files(keysdatafile,bucketname,org):
    # returns list of files in S3 for the specified bucket
    filelist =[]
    
    keyID,secretID,sessionToken = ReadCredentials(keysdatafile)
    resource = boto3.resource('s3',
                              aws_access_key_id = keyID,
                              aws_secret_access_key = secretID)

    bucket_of_interest = resource.Bucket(bucketname)
   
    for item in bucket_of_interest.objects.filter():
        d,add = parseKey(item.key,item.last_modified,org)
        if add == True:
            filelist.append(d)
        #print((datetime.strptime(str(item.last_modified), '%Y-%m-%d %H:%M:%S+00:00')))
    return filelist   

def parseKey(keyitem,lastmodified,org):
    # returns dictionary of pertinent items after parsing the given key item and the last modifed date
    tmp = keyitem.split('/')
    file = tmp[len(tmp) - 1]
    filename = file.split('\\')[len(file.split('\\'))-1]
    subdir = '/'.join(tmp)
    subdir = subdir.replace('/' + file,'')
    
    isValid = Add2Dictionary(subdir,org)
    file_subDir_dict = {'File':file,'Filename':filename,'SubDir':subdir,'Key':keyitem,'Lastmodified':lastmodified}
    return file_subDir_dict,isValid

def deleteFileinS3(client,filebucket,file,dirname):
    # Delete individual file in s3 bucket
    try:
        delete_file_bucket = str(filebucket)
        delete_file_key = str(dirname) + '/' + str(file)
        response = client.delete_object(Bucket = delete_file_bucket,Key = delete_file_key)
        return response
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

def deleteAllFiles(keysdatafile,bucketname,delete_lst):
    
    # Delete all files in s3 bucket
    keyID,secretID,sessionToken = ReadCredentials(keysdatafile)
    client = boto3.client('s3', aws_access_key_id = keyID, aws_secret_access_key = secretID)
    for item in delete_lst:
        #print('File:',item['File'],'SubDir:',item['SubDir'])
        response = deleteFileinS3(client,bucketname,item['File'],item['SubDir'])
        
def uploadtoS3(client,filebucket,file,dirname):
    try:
        upload_file_bucket = filebucket
        upload_file_key = str(dirname) + '/' + str(file)
        client.upload_file(file,upload_file_bucket,upload_file_key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise
            
def uploadAllFiles(keysdatafile,bucketname,upload_lst,boxpath):
    keyID,secretID,sessionToken = ReadCredentials(keysdatafile)
    client = boto3.client('s3', aws_access_key_id = keyID, aws_secret_access_key = secretID)
    for item in upload_lst:
        filepath = os.path.abspath(os.path.join(boxpath,item['SubDir']))
        file = os.path.abspath(os.path.join(filepath,item['File']))
        uploadtoS3(client,bucketname,file,item['SubDir'])
        

        
def downloadAllFiles(keysdatafile,bucketname,download_lst,boxpath):
    #boxpath = 'C:\\Users\\sumanth.bail\\Documents\\Test\\' # ---> Test for downloading to different location i.e different machine
    keyID,secretID,sessionToken = ReadCredentials(keysdatafile)
    client = boto3.client('s3', aws_access_key_id = keyID, aws_secret_access_key = secretID)
    for item in download_lst:
        download_file_key = item['Key'] 
        download_file_name = os.path.abspath(os.path.join(boxpath,item['SubDir']))
        make_dir(download_file_name)
        download_file_name = os.path.abspath(os.path.join(download_file_name,item['Filename']))
        client.download_file(bucketname,download_file_key,download_file_name)
        print('Successful File Download: ',download_file_name)
        

def downloadModifiedFilesSinceLastRun(keysdatafile,bucketname,download_lst,boxpath,LastRun_utc):
    keyID,secretID,sessionToken = ReadCredentials(keysdatafile)
    client = boto3.client('s3', aws_access_key_id = keyID, aws_secret_access_key = secretID)
    for item in download_lst:
        download_file_key = item['Key'] 
        download_file_name = os.path.abspath(os.path.join(boxpath,item['SubDir']))
        make_dir(download_file_name)
        download_file_name = os.path.abspath(os.path.join(download_file_name,item['Filename']))
        # Will download only if 
        # 1) Any file modified on s3 since last run
        # 2) If file in s3 but not in local drive
        if (datetime.strptime(str(item['Lastmodified']), '%Y-%m-%d %H:%M:%S+00:00') > datetime.strptime(str(LastRun_utc), '%Y-%m-%d %H:%M:%S')) or os.path.exists(download_file_name) == False:
            print('Successful File Download: ',download_file_name)
            client.download_file(bucketname,download_file_key,download_file_name)
        else:
            print(download_file_name,' No file change in S3. File exists locally. Download skipped!')
            
def setLastRun():
    writeConfig('Main','LastRun_utc',str(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))
    
def getLastRun():
    return readConfig('Main','LastRun_utc','1900-01-01 00:00:00')

def setuser(username):
    writeConfig('Main','username',username)
    
def getuser():
    return readConfig('Main','username','')

def setapikey(apikey):
    writeConfig('Main','apikey',apikey)
    
def getapikey():
    return readConfig('Main','apikey','')

def setrole(role):
    writeConfig('Main','role',role)
    
def getrole():
    return readConfig('Main','role','')

def setorg(org):
    writeConfig('Main','org',org)
    
def getorg():
    return readConfig('Main','org','')

def setpassword():
    keyring.set_password(Application_Name, username, password)
    
def getpassword():
    return keyring.get_password(Application_Name, username)

def login(Application_Name,username,password):
    ret = False
    if Application_Name == '':
        Application_Name = 'Sharebox'
    if username != '' and password !='':
        # Do API login call
        
        # Get User Record. Parse api_key, org and role
        # Return api_key, org and role
        api_key = '2b0e6a26-4b4a-4461-96b7-9085de4cc344'
        org_id = 6 # Get Org based on org_id
        org = 'test-organization'
        role = 'RW'    
        setorg(org)
        setapikey(api_key)
        setrole(role)
        ret = True
    return ret
    


# In[ ]:




