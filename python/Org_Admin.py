#!/usr/bin/env python
# coding: utf-8

'''''
ShareBox (Admin)

Cloud Computing Final Project

Team: Open Group

Team Members: Abdullateef A, Sumanth B, Brendan T, Ryna B, Freddie Z

# Requires to be with the following files in the same directory

1. AWS credentials: Awskeys.txt (Communication with S3)
2. s3.py (Communication with S3)
3. Client.py (End User)

'''''

# Working copy
import os
import sys
import json
import pymysql
import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QListWidgetItem,
        QListWidget, QPushButton, QRadioButton, QVBoxLayout, QWidget, QMessageBox)

Title = 'ShareBox'
url_prefix = 'https://l0er6wogrg.execute-api.us-east-1.amazonaws.com/prod'
UIVersion = '2.0.08012020'

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow,self).__init__()

        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint, False)
        self.setGeometry(100,100,300,400)
        self.setWindowTitle(Title)
        self.setWindowIcon(QtGui.QIcon('ShareBox.png'))
        self.setFixedSize(500, 500)

        self.listView = QtWidgets.QListWidget(self)
        self.listView.setGeometry(QtCore.QRect(10, 70, 310, 220))
        self.listView.setObjectName("listView")
        self.listView.clicked.connect(self.listSelection)

        self.btnList = QtWidgets.QPushButton(self)
        self.btnList.setGeometry(330, 70, 150, 40)
        self.btnList.setText("List Users")
        self.btnList.clicked.connect(self.listUsers)
        
        self.btnAdd = QtWidgets.QPushButton(self)
        self.btnAdd.setGeometry(330, 115, 150, 40)
        self.btnAdd.setText("Add User")
        self.btnAdd.clicked.connect(self.ADD)
        self.btnAdd.setEnabled(False)
        
        self.btnChangeRole = QtWidgets.QPushButton(self)
        self.btnChangeRole.setGeometry(330, 160, 150, 40)
        self.btnChangeRole.setText("Change Role")
        self.btnChangeRole.clicked.connect(self.roleGroup)

        self.btnDelete = QtWidgets.QPushButton(self)
        self.btnDelete.setGeometry(330, 205, 150, 40)
        self.btnDelete.setText("Delete User")
        self.btnDelete.clicked.connect(self.delete_user)        
        
        self.btnAbout = QtWidgets.QPushButton(self)
        self.btnAbout.setGeometry(330, 250, 150, 40)
        self.btnAbout.setText("About")
        self.btnAbout.clicked.connect(self.about)
        
        self.btnList.setEnabled(False)
        self.btnDelete.setEnabled(False)
        self.btnChangeRole.setEnabled(False)
        
        # Set user Credentials and Login
        self.txtuser = QtWidgets.QLineEdit(self)
        self.txtuser.setGeometry(10, 5, 150, 40)
        self.txtuser.setPlaceholderText("  Enter Username") 
        
        self.txtpwd = QtWidgets.QLineEdit(self)
        self.txtpwd.setGeometry(170, 5, 150, 40)
        self.txtpwd.setEchoMode(QtWidgets.QLineEdit.Password)
        self.txtpwd.setPlaceholderText("  Enter Password") 
        
        self.btnLogin = QtWidgets.QPushButton(self)
        self.btnLogin.setGeometry(330,5, 150, 40)
        self.btnLogin.setText("Login")
        self.btnLogin.clicked.connect(self.DBConnection)

        boldFont = QtGui.QFont()
        boldFont.setBold(True)

        self.groupBox = QtWidgets.QGroupBox("Select Role", self)
        self.groupBox.setGeometry(20, 300, 200, 190)
        self.btnUpdate = QtWidgets.QPushButton(self)
        self.btnUpdate.setText("Update")
        self.btnUpdate.setMinimumHeight(30)
        self.btnUpdate.clicked.connect(self.updateRole)
        self.btnCancel = QtWidgets.QPushButton(self)
        self.btnCancel.setText("Cancel")
        self.btnCancel.setMinimumHeight(30)
        self.btnCancel.clicked.connect(self.cancel)
        self.radioOrgAdmin = QRadioButton("org_admin")
        self.readOnly = QRadioButton("  ReadOnly")
        self.radioReadWrite = QRadioButton("  ReadWrite")
        self.radioOrgAdmin.setChecked(True)
        self.gridLayout = QGridLayout()
        self.gridLayout.addWidget(self.radioOrgAdmin, 0,0)
        self.gridLayout.addWidget(self.readOnly, 1,0)
        self.gridLayout.addWidget(self.radioReadWrite, 2,0)
        self.gridLayout.addWidget(self.btnUpdate, 4,0)
        self.gridLayout.addWidget(self.btnCancel, 4,1)
        self.groupBox.setLayout(self.gridLayout)
        self.groupBox.setHidden(True)

        self.groupBox2 = QtWidgets.QGroupBox("Enter Information", self)
        self.groupBox2.setGeometry(20, 300, 300, 190)
        self.txtUsername = QtWidgets.QLineEdit(self)
        self.txtUsername.setPlaceholderText("  Enter Username") 
        self.txtUsername.setMinimumHeight(30)
        self.txtPass = QtWidgets.QLineEdit(self)
        self.txtPass.setPlaceholderText("  Enter Password")
        self.txtPass.setMinimumHeight(30) 
        self.txtEmail = QtWidgets.QLineEdit(self)
        self.txtEmail.setPlaceholderText("  Enter Email") 
        self.txtEmail.setMinimumHeight(30)
        self.labelRole = QtWidgets.QLabel(self)
        self.labelRole.setText("* Choose a Role *")
        self.labelRole.setFont(boldFont)
        self.readOnly1 = QRadioButton("  ReadOnly")
        self.radioReadWrite1 = QRadioButton("  ReadWrite")
        self.readOnly1.setChecked(True)
        self.btnSave = QtWidgets.QPushButton(self)
        self.btnSave.setText("Save")
        self.btnSave.setMinimumHeight(30)
        self.btnSave.clicked.connect(self.addUser)
        self.btnReset = QtWidgets.QPushButton(self)
        self.btnReset.setText("Reset")
        self.btnReset.setMinimumHeight(30)
        self.btnReset.clicked.connect(self.clearText)
        self.gridLayout2 = QGridLayout()
        self.gridLayout2.addWidget(self.txtUsername, 0,0)
        self.gridLayout2.addWidget(self.txtPass, 1,0)
        self.gridLayout2.addWidget(self.txtEmail, 2,0)
        self.gridLayout2.addWidget(self.labelRole, 0,1)
        self.gridLayout2.addWidget(self.readOnly1, 1,1)
        self.gridLayout2.addWidget(self.radioReadWrite1, 2,1)
        self.gridLayout2.addWidget(self.btnSave, 4,0)
        self.gridLayout2.addWidget(self.btnReset, 4,1)
        self.groupBox2.setLayout(self.gridLayout2)
        self.groupBox2.setHidden(True)
        
        
    def DBConnection(self):
        if self.txtuser.text().strip() != '' and self.txtpwd.text().strip() != '':
            
            try:
                credin = {}
                credin["username"] = self.txtuser.text().strip()
                credin["password"] = self.txtpwd.text().strip()
        
                lambdaAPI = url_prefix + '/login'
                response = requests.post(url=lambdaAPI, json = credin )
                obj = json.dumps(response.json())
                login = json.loads(obj)
                
                result = login["status"]
                if result == 400:
                    QMessageBox.critical(self, 'Error', '  Incorrect username and/or password!   ')
                
                else:
                    user = json.loads(login["body"])
                    role = user['role']
                    global orgAdmin_apiKey
                    orgAdmin_apiKey = user['api_key']
                    global orgAdmin_orgId
                    orgAdmin_orgId = user['org_id']                    

                    if role == 'org_admin':
                    
                        self.btnAdd.setEnabled(True)
                        self.btnList.setEnabled(True)
                        self.btnDelete.setEnabled(True)
                        self.btnChangeRole.setEnabled(True)

                    else:
                        QMessageBox.critical(self, 'Error', '  Not Organization Admin!   ')
        

            except pymysql.Error as e:
                QMessageBox.critical(self, 'Connection', 'Failed To Connect Database')
                sys.exit(1)
    

    def userID(self, username):
        req = {}
        req["api_key"] = orgAdmin_apiKey
        req["username"] = username  

        lambdaAPI = url_prefix + '/get_user'
        response = requests.post(url=lambdaAPI, json = req)
        obj = json.dumps(response.json())
        userInfo = json.loads(obj)['body']
        userId = json.loads(userInfo)['id']
        return userId

            
    def roleGroup(self):
        self.groupBox2.setHidden(True)
        self.groupBox.show()
    

    def ADD(self):
        self.groupBox.setHidden(True)
        self.groupBox2.show()        
    

    def listUsers(self):
        self.listView.clear()

        lambdaAPI = url_prefix + '/get_organization_users'
        response = requests.post(url=lambdaAPI, json = {"org_id":orgAdmin_orgId} )
        obj = json.dumps(response.json())
        res = json.loads(obj)
        result = json.loads(res["body"])

        for row in range(len(result)):
            self.listView.addItem(QListWidgetItem(str(result[row]["username"]), self.listView))


    def clearText(self):
        self.txtUsername.setText('')
        self.txtPass.setText('')
        self.txtEmail.setText('')


    def addUser(self):
    
        if self.readOnly1.isChecked():  
            role = "readonly"
        elif self.radioReadWrite1.isChecked():  
            role = "readwrite"
        else:
            QMessageBox.critical(self, 'Error', 'Select Role')

        event = {}
        event["api_key"] = orgAdmin_apiKey
        event["email"] = self.txtEmail.text().strip()
        event["username"] = self.txtUsername.text().strip()
        event["password"] = self.txtPass.text().strip()
        event["role"] = role
        event["org_id"] = int(orgAdmin_orgId)

        lambdaAPI = url_prefix + '/register_user'
        response = requests.post(url=lambdaAPI, json = event)
        obj = json.dumps(response.json())
        res = json.loads(obj)

        if res["status"] == 200:
            user = json.loads(res["body"])
            userId = user['id']
            self.listView.addItem(QListWidgetItem(self.txtUsername.text().strip(),self.listView))
            self.groupBox2.setHidden(True)
            QMessageBox.about(self, 'Successfull', self.txtUsername.text() + ' was added successfully')


        else:
            QMessageBox.critical(self, 'Error', res["body"])
            

    def listSelection(self):
        item = self.listView.currentItem()
        selectedUser = item.text()
        return selectedUser


    def delete_user(self):
        req = {}
        req["api_key"] = orgAdmin_apiKey
        req["user_id"] = self.userID(self.listSelection())
        confirm = QMessageBox.question(self, Title, "Continue with deletion?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirm == QMessageBox.Yes:
            lambdaAPI = url_prefix + '/delete_user'
            response = requests.post(url=lambdaAPI, json = req)
            obj = json.dumps(response.json())
            res = json.loads(obj)

            if res["status"] == 200:
                self.listView.takeItem(self.listView.currentRow())
                QMessageBox.about(self, 'Successfull', res["body"])
            else:
                QMessageBox.critical(self, 'Error', res["body"])  


    def updateRole(self):
        if self.radioOrgAdmin.isChecked():
            role = self.radioOrgAdmin.text()
        elif self.readOnly.isChecked():  
            role = "readonly"
        elif self.radioReadWrite.isChecked():  
            role = "readwrite"
        else:
            QMessageBox.critical(self, 'Error', 'Select Role')

        req = {}
        req["role"] = role
        req["api_key"] = orgAdmin_apiKey
        req["user_id"] = self.userID(self.listSelection())

        lambdaAPI = url_prefix + '/edit_user_role'
        response = requests.post(url=lambdaAPI, json = req)
        obj = json.dumps(response.json())
        res = json.loads(obj)

        if res["status"] == 200:
            QMessageBox.about(self, 'Successfull', res["body"])

        else:
            QMessageBox.critical(self, 'Error', res["body"])


    def cancel(self):
        self.groupBox.setHidden(True)
        self.groupBox.setHidden(True)


    def about(self):
        QMessageBox.about(self, Title, "ShareBox:\n~A Dropbox inspired application\n\nVersion " + UIVersion + "\n\nFinal Project for Cloud Computing\n\nDeveloped by 'Open Group'\nTeam - Brendan T, Sumanth B, Abdullateef A, Freddie Z, and Ryan B") 

        

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    form = MyWindow()
    form.show()
    app.exec_()
    
if __name__ == '__main__':
    main()
