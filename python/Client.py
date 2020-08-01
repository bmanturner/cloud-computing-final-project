#!/usr/bin/env python
# coding: utf-8

# In[3]:


'''''
ShareBox

Cloud Computing Final Project

Team: Open Group

Team Members: Sumanth B, Abdullateef A, Brendan T, Ryna B, Freddie Z

# Requires the following files in the same directory

1. AWS credentials: Awskeys.txt (Communication with S3)
2. s3.py (Communication with S3)
3. Org_Admin.py (Administration)

'''''


# In[4]:


# Working copy
import shutil, os
import sys
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QMenuBar,QStatusBar
from PyQt5.QtWidgets import QFileDialog,QInputDialog

'''
import of backend code for List, upload, 
download and delete from s3 

'''
# import of backend code for List, upload, download and delete from s3
import s3

# import of Admin code to Add, Delete Users, Modify Roles
from Org_Admin import MyWindow

Title = 'ShareBox'
currentparentpath = ''
previousparentpath = ''
boxpath = ''
orgpath = ''
org = ''
orgname = ''
keysdatafile = ''
bucketname = ''
role = ''
droppedFiles = []
logcount = 0
UIVersion = '2.0.08012020'



class DropArea(QtWidgets.QPushButton):
    '''
    Pushbutton used both as an area to drop file and also 
    to browse files that need to be uploaded
    Allow files 
    '''
    signal = QtCore.pyqtSignal()
    def __init__(self, parent):
        super(DropArea, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super(DropArea, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        super(DropArea, self).dragMoveEvent(event)

    def dropEvent(self, event):
        global droppedFiles
        
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
            droppedFiles = []
            for url in event.mimeData().urls():
                file = str(url.toLocalFile())
                isFile = os.path.isfile(file)
                if isFile == True:
                    droppedFiles.append(file)
            self.signal.emit()
        else:
            super(DropArea,self).dropEvent(event)

class ShareboxClient(QtWidgets.QWidget):
    '''
    Main End-user Window
    
    '''
    def __init__(self):
        super(ShareboxClient,self).__init__()

        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setGeometry(100,100,300,400)

        self.setWindowTitle(Title)
        self.setWindowIcon(QtGui.QIcon('ShareBox.png')) 
        self.setFixedSize(800, 640)

        self.btnDA = DropArea(self)
        self.btnDA.setGeometry(0, 550, 600, 90)
        self.btnDA.setText("To Upload: Drop files here or click to browse to file")
        self.btnDA.clicked.connect(self.addDocument)
        self.btnDA.signal.connect(self.drop_event)

        self.listView = QtWidgets.QListWidget(self)
        self.listView.setGeometry(QtCore.QRect(0, 50, 600, 450))
        self.listView.setObjectName("listView")
        self.listView.doubleClicked.connect(self.listSelection)
        self.listView.HideSelection = False

        self.btnBack = QtWidgets.QPushButton(self)
        self.btnBack.setGeometry(610, 50, 175, 40)
        self.btnBack.setText("Back")
        self.btnBack.clicked.connect(self.goBack)

        self.btnSync = QtWidgets.QPushButton(self)
        self.btnSync.setGeometry(610, 100, 175, 40)
        self.btnSync.setText("Sync")
        self.btnSync.clicked.connect(self.sync)
        
        self.btnForceSync = QtWidgets.QPushButton(self)
        self.btnForceSync.setGeometry(610, 150, 175, 40)
        self.btnForceSync.setText("Sync (Get All)")
        self.btnForceSync.clicked.connect(self.syncforce)

        self.btnList = QtWidgets.QPushButton(self)
        self.btnList.setGeometry(610, 200, 175, 40)
        self.btnList.setText("Refresh")
        self.btnList.clicked.connect(self.load)

        self.btnDelete = QtWidgets.QPushButton(self)
        self.btnDelete.setGeometry(610, 250, 175, 40)
        self.btnDelete.setText("Delete")
        self.btnDelete.clicked.connect(self.deleteFile)

        self.btnAdd = QtWidgets.QPushButton(self)
        self.btnAdd.setGeometry(610, 300, 175, 40)
        self.btnAdd.setText("Add Folder")
        self.btnAdd.clicked.connect(self.addFolder)
        
        self.btnReUpload = QtWidgets.QPushButton(self)
        self.btnReUpload.setGeometry(610, 350, 175, 40)
        self.btnReUpload.setText("Re-Upload")
        self.btnReUpload.clicked.connect(self.ReUpload)
        
        self.btnAbout = QtWidgets.QPushButton(self)
        self.btnAbout.setGeometry(610, 400, 175, 40)
        self.btnAbout.setText("About")
        self.btnAbout.clicked.connect(self.about)
        
        self.btnAdmin = QtWidgets.QPushButton(self)
        self.btnAdmin.setGeometry(610, 540, 175, 40)
        self.btnAdmin.setText("Admin")
        self.btnAdmin.clicked.connect(self.Admin)

        self.btnExit = QtWidgets.QPushButton(self)
        self.btnExit.setGeometry(610, 590, 175, 40)
        self.btnExit.setText("Exit")
        self.btnExit.clicked.connect(self.exit)

        self.lblDir = QtWidgets.QLabel(self)
        self.lblDir.setGeometry(10, 480, 600, 90)
        self.lblDir.setText("")
        
        # Set user Credentials and Login
        self.txtuser = QtWidgets.QLineEdit(self)
        self.txtuser.setGeometry(10, 5, 175, 40)
        self.txtuser.setPlaceholderText("  Enter Username") 
        
        self.txtpwd = QtWidgets.QLineEdit(self)
        self.txtpwd.setGeometry(195, 5, 175, 40)
        self.txtpwd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txtpwd.setPlaceholderText("  Enter Password") 
        
        self.btnLogin = QtWidgets.QPushButton(self)
        self.btnLogin.setGeometry(380,5, 150, 40)
        self.btnLogin.setText("Login")
        self.btnLogin.clicked.connect(self.login)
        
        # set user local Sharebox directory
        self.chkSB = QtWidgets.QCheckBox(self)
        self.chkSB.setGeometry(600,5, 200, 40)
        self.chkSB.setText("Set Local Path")
        self.chkSB.toggled.connect(lambda:self.btnstate(self.chkSB))
        self.chkSB.hide()
        
        self.listdebug = QtWidgets.QListWidget(self)
        self.listdebug.setGeometry(QtCore.QRect(0, 640, 800, 400))
        self.listdebug.setObjectName("listdebug")
        self.listdebug.HideSelection = False
        
        self.chklog = QtWidgets.QCheckBox(self)
        self.chklog.setGeometry(610, 490, 175, 40)
        self.chklog.setText("View Log")
        self.chklog.toggled.connect(lambda:self.btnstate(self.chklog))


        
        # Disable buttons on load
        self.btnEnable(False)
        
        '''
        # Get config values and set to text boxes for login
    
        '''
        
        username = s3.getuser()
        if username.strip() !='':

            self.txtuser.setText(username)
            self.txtpwd.setText(s3.getpassword(username))
        
        boxpath = s3.getboxpath()
        '''
        # Start logging with version information
    
        '''
        self.addLog('Start Session')
        self.addLog('Sharebox UI Version: ' + UIVersion)
        self.addLog('s3 Library Version: ' + s3.version())
        
      
    def drop_event(self):
        # gets executed on drop via signal
        self.add_files()
        
    '''
    ReUpload: 
    Requires a selection in the list box
    Will overwrite the file in S3 with local file
    Requires Role: "ReadWrite" or "Org_Admin"
    Communicates with s3
    
    '''        
        
    def ReUpload(self):
        global droppedFiles
        item = self.listView.currentItem()
        if item == None:
            # no item seleted, skip
            return 
        if '+' in item.text():
            # is a folder, skip
            return
                
        fileparent = orgpath + self.lblDir.text()
        file = os.path.abspath(os.path.join(fileparent,item.text().replace('-','')))

        droppedFiles = []
        droppedFiles.append(file)
        self.add_files()
        
    '''
    add_files: 
    Called by 1) Drag and drop on Browse button  or 2) Click event of Browse button.
    File will be uploaded to S3
    Requires Role: "ReadWrite" or "Org_Admin"
    Communicates with s3
    
    '''     
    def add_files(self): 
        if role == 'readonly':
            self.addLog('No upload rights')
            QMessageBox.critical(self, Title, "You do not have create rights.") 
            return
        upload_lst =[]
        for file in droppedFiles:
            fileexistsinlocal = False
            try:
                shutil.copy(file, currentparentpath)
            except:
                fileexistsinlocal = True
                self.addLog('Copy Skipped!')
                
            entity = os.path.basename(file)
             
            fullpath = os.path.abspath(os.path.join(currentparentpath,entity))
            EntityPath = fullpath.replace(boxpath,'').replace(entity,'')
            if len(EntityPath) !=0:
                if EntityPath[-1] =='\\':
                    EntityPath = EntityPath[:-1]
            EntityPath = EntityPath.replace('\\','/').replace(boxpath + '/','')       
            my_dict = {'File':entity,'SubDir':EntityPath}
           
            if s3.Add2Dictionary(EntityPath,org) == True:
                upload_lst.append(my_dict)
                self.addLog('Upload file: ' + entity)
                if fileexistsinlocal == False:
                    self.listView.addItem('-' + entity)
            else:
                self.addLog('Cannot Upload file. Dictionary Check Failed: ' + entity)

        if len(upload_lst) > 0:
            try:
                s3.uploadAllFiles(keysdatafile,bucketname,upload_lst,boxpath)
                self.addLog('(S3 Object Upload) Upload Successful ')
            except:
                self.addLog('Upload failed!')
                QMessageBox.critical(self, Title, "Upload failed!")

    def sync(self):   
        self.download(False)
            
    def syncforce(self):   
        self.download(True)
        
    '''
    download: 
    Called by 
    1) Sync: Will check last run time and get files modified or created since then 
    2) Sync (Get All): Will get all
    
    File(s) will be downloaded from S3
    Requires Role: No Role restriction
    Communicates with s3
    '''

    def download(self,forceDownload):   
        try:
            s3_file_dir_lst = s3.listS3Files(keysdatafile,bucketname,org)
            self.addLog('(S3 Object Listing)')

            if forceDownload == True:
                self.addLog('Download complete. All files obtained.')
                s3.downloadAllFiles(keysdatafile,bucketname,s3_file_dir_lst,boxpath)
            else:
                LastRun_utc = s3.getLastRun()
                self.addLog('last sync @' + str(LastRun_utc))
                s3.downloadModifiedFilesSinceLastRun(keysdatafile,bucketname,s3_file_dir_lst,boxpath,LastRun_utc)
                self.addLog('(S3 Object Download) Download complete!')
                s3.setLastRun()
        except:
            QMessageBox.critical(self, Title, "Upload failed!") 

    '''
    deleteFile: 
    Requires a selection in the list box
    Will delete the file in S3 and the local file
    Requires Role: "ReadWrite" or "Org_Admin"
    Communicates with s3
    '''            
    def deleteFile(self):
        if role == 'readonly':
            self.addLog('No delete rights')
            QMessageBox.critical(self, Title, "You do not have delete rights.") 
            return
        item = self.listView.currentItem()
        if item == None:
            return
        delete_lst = []
        # Get list of file in s3
        s3_file_dir_lst = s3.listS3Files(keysdatafile,bucketname,org)
        s3_files = [{'Key':item['Key'],'File':item['File'],'SubDir':item['SubDir']} for item in s3_file_dir_lst]

        fileparent = orgpath + self.lblDir.text()
        file = os.path.abspath(os.path.join(fileparent,item.text().replace('-','')))
        searchfilekey = org + self.lblDir.text()+ '\\' + item.text().replace('-','')
        isFile = os.path.isfile(file)
        if isFile == True:
            found = next((l for l in s3_files if searchfilekey in l['File']), None)
            if found != None:
                delete_lst.append(found)
            if len(delete_lst) > 0:
                confirm = QMessageBox.question(self, Title, "Continue with deletion?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    try:
                        s3.deleteAllFiles(keysdatafile,bucketname,delete_lst)
                        self.addLog('(S3 Object Delete) File deleted. ' + file)
                        os.remove(file)
                        self.listView.takeItem(self.listView.currentRow())
                    except:
                        QMessageBox.critical(self, Title, "Delete failed!") 
                        
    '''
    addFolder: 
    Creates local folder (Folder and sub-folders are set as prefix to the documents uploaded)
    Requires Role: "ReadWrite" or "Org_Admin"
    '''                            
    def addFolder(self):
        if role == 'readonly':
            self.addLog('No upload rights')
            QMessageBox.critical(self, Title, "You do not have create rights.") 
            return
        global currentparentpath
        
        folder,result = QInputDialog.getText(self, Title, 'Enter new folder name:') 
        if result == True:
            currentparentpath = os.path.join(currentparentpath,str(folder)) 
            #print('currentparentpath',currentparentpath)
            s3.make_dir(currentparentpath)
            self.addLog('New folder created: ' + str(folder))
            flist = os.listdir(currentparentpath)
            self.loadlist(flist,currentparentpath)
            self.lblDir.setText(currentparentpath.replace(orgpath,''))
            
    def addDocument(self):
        global droppedFiles
        fname,result = QFileDialog.getOpenFileName(self, 'Open file','c:\\',"All files (*.*)")   
        droppedFiles = []
        droppedFiles.append(fname)
        self.add_files()

    def btnstate(self,b):
        global boxpath
        if b.text() == "Set Local Path":
            if b.isChecked() == True:
                boxpath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
                s3.setboxpath(boxpath)
                s3.resetLastRun()
                b.setChecked(False)
        if b.text() == "View Log":
            if b.isChecked() == True:
                self.setFixedSize(800, 1040)
            else:
                self.setFixedSize(800, 640)

                
    def goBack(self):
        global currentparentpath
        if self.lblDir.text().strip() != '':
            destination = self.lblDir.text().split('\\')
            if len(destination) >= 2:
                currentparentpath = currentparentpath.replace('\\' + str(destination[len(destination) - 1]),'')
                flist = os.listdir(currentparentpath)
                self.loadlist(flist,currentparentpath)
                self.lblDir.setText(currentparentpath.replace(orgpath,''))
                                                   
    def listSelection(self):
        self.selectionAction()
            
    def selectionAction(self):
        global currentparentpath,previousparentpath
        item = self.listView.currentItem()
        fullpath = os.path.join(currentparentpath,item.text().replace('-','').replace('+',''))
        isFile = os.path.isfile(fullpath)
        self.addLog('Open: ' + item.text().replace('-','').replace('+',''))
        if isFile == False:
            
            previousparentpath = currentparentpath
            currentparentpath = os.path.join(currentparentpath,item.text().replace('+',''))
            flist = os.listdir(currentparentpath)
            self.loadlist(flist,currentparentpath)
            self.lblDir.setText(currentparentpath.replace(orgpath,''))
        else:
            
            self.openFile(fullpath)

    '''
    addLog: 
    Add entries to log list
    Valid for the current session
    Requires Role: No Role restriction
    '''     
    def addLog(self,val):
        global logcount
        logcount += 1
        x = str(logcount).zfill(5)
        self.listdebug.addItem(str(x) + ' ' + val) 
        self.listdebug.sortItems(1)
        
    def loadlist(self,flist,fullpath):
        self.listView.clear()
        for item in flist:
            fol = '+'
            if len(item.split('.')) > 1:
                fol = '-'
            self.listView.addItem(fol + item) 
            if item == org:
                self.listView.setCurrentRow(0)
                self.selectionAction()
                break
            self.listView.sortItems()
    '''
    load: 
    Called at login
    Get Organization Name and ID
    Get Role
    If first use, set local ShareBox Directory
    If Windows, set default to Documents
    Set Window title with User and Org info
    Requires Role: No Role restriction
    '''             
    def load(self):
        global currentparentpath,keysdatafile,bucketname,boxpath,orgpath,org,orgname,role
        try:
            orgname = s3.getorgname()
            self.addLog('Org name: ' + orgname)
            org = s3.getorg()
            self.addLog('Org s3 prefix: ' + org)
            role = s3.getrole()
            self.addLog('Role: ' + role)
            boxpath = s3.getboxpath()
            
            if boxpath.strip() == '':
                confirm = QMessageBox.question(self, Title, "Do you wish to use the default ShareBox path for Windows?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if confirm == QMessageBox.No:
                    try:
                        boxpath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
                        print('Set boxpath to',boxpath)
                        s3.setboxpath(boxpath)
                        s3.resetLastRun()
                    except:
                        QMessageBox.critical(self, Title, "boxpath setting failed!") 
            
            self.setWindowTitle(Title + ' | ' + org + ' | ' + self.txtuser.text().strip())
            keysdatafile,bucketname,boxpath = s3.getEssentials(boxpath)
            orgpath = os.path.join(boxpath,org) 
            self.addLog('Local Path: ' + boxpath)
            s3.make_dir(orgpath)
            s3.setboxpath(boxpath)
            self.btnEnable(True) 
            self.addLog('Download files modified since last sync.')
            self.download(False)
            currentparentpath = orgpath
            flist = os.listdir(orgpath)
            self.loadlist(flist,orgpath) 
        except:
            QMessageBox.critical(self, Title, "Load failed!") 

    def exit(self):
        self.close()  
    '''
    login: 
    Call communicates with API-Gateway
    '''          
    def login(self):
        username = self.txtuser.text().strip()
        userpassword = self.txtpwd.text().strip()
        if username == '' or userpassword == '':
            QMessageBox.critical(self, Title, "Username and password are required!")  
        else:
            if s3.login(username,userpassword == '') == True:
                self.addLog('(API Gateway Call) Login Successful for user: ' + username)
                self.load()
            else:
                QMessageBox.critical(self, Title, "Login failed!") 
    '''
    btnEnable: 
    Enable button on login and based on user rights
    '''               
    def btnEnable(self,value):
        self.btnSync.setEnabled(value)
        self.btnList.setEnabled(value)
        self.btnForceSync.setEnabled(value)
        self.btnBack.setEnabled(value)
        self.chkSB.setEnabled(not value)
        
        if role == 'readonly':
            self.addLog('User with Read Only Rights (Add, Delete and Drop Buttons Disabled)')
            self.btnAdd.setEnabled(False)
            self.btnDelete.setEnabled(False)
            self.btnDA.setEnabled(False)
            self.btnReUpload.setEnabled(False)
        else:
            self.btnAdd.setEnabled(value)
            self.btnDA.setEnabled(value)
            self.btnDelete.setEnabled(value)
            self.btnReUpload.setEnabled(value)
    '''
    openFile: 
    Open file selection from list box
    '''   
    def openFile(self,fileName):
        webbrowser.open(fileName)
    '''
    Admin: 
    Open Admin console
    ''' 
    def Admin(self):
        self.addLog('Admin Event')
        self.child_win = MyWindow()
        self.child_win.show()
    '''
    about: 
    Application Version
    Group Information
    '''           
    def about(self):
        self.addLog('About Event')
        QMessageBox.about(self, Title, "ShareBox:\n~A Dropbox inspired application\n\nVersion " + UIVersion + "\n\nFinal Project for Cloud Computing\n\nDeveloped by 'Open Group'\nTeam - Brendan T, Sumanth B, Abdullateef A, Freddie Z, and Ryan B") 
    
def main():
    app = QtWidgets.QApplication(sys.argv)
    form = ShareboxClient()
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    main()


# In[ ]:




