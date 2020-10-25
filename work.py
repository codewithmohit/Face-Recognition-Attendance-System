from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import re
from PyQt5.uic import loadUiType
import mysql.connector as con
import datetime
from xlrd import *
from xlsxwriter import *
ui_home,_=loadUiType('home.ui')
ui_manage,_=loadUiType('manage.ui')
ui_attendance,_=loadUiType('attendance_report.ui')
import fr
class Mess():
    def message_warning(self,message):
        msg = QMessageBox()      
        msg.setWindowTitle("Info")
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        x = msg.exec_()
    def message_critical(self,message):
        msg = QMessageBox()
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        x = msg.exec_()
    def message_information(self,message):
        msg = QMessageBox()
        msg.setWindowTitle("Information")
        msg.setText(message)
        msg.setIcon(QMessageBox.Information)
        x = msg.exec_()  
class Home(QMainWindow,ui_home):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handel_Buttons()
    def Handel_Buttons(self):
        self.pushButton.clicked.connect(self.manage)
        self.pushButton_2.clicked.connect(self.attendance)
        self.pushButton_4.clicked.connect(self.recognize)

    def manage(self):
        self.window1=Manage()
        self.close()
        self.window1.show()
    def attendance(self):
        self.window2=Attendance()
        self.close()
        self.window2.show()
    def recognize(self):
        c=fr.main()

class Manage(QMainWindow,ui_manage):
    c=Mess()
    def __init__(self):
        self.db = con.connect(host='localhost', user='root', password='root', db='attendance')
        self.cur = self.db.cursor()
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.Handel_Buttons()
        self.Handel_UI_Changes() 
        self.Show_Handle_Operation()
    
    def check(self,email): 
        # Make a regular expression 
        regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        # for custom mails use: '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'  
        if(re.search(regex,email)):  
            return True  
        else:  
            return False
    def Handel_UI_Changes(self):
        #To hide The tab bar
        self.tabWidget.tabBar().setVisible(False)

    def browse(self):
        fname=QFileDialog.getOpenFileName(self,'Open File','c\\','Image files(*.jpg *.gif)')
        self.lineEdit_8.setText(fname[0])

    def Handel_Buttons(self):
        self.pushButton_5.clicked.connect(self.add_student)
        self.pushButton_6.clicked.connect(self.update_detail)
        self.pushButton_1.clicked.connect(self.submit)
        self.pushButton_2.clicked.connect(self.search)
        self.pushButton.clicked.connect(self.browse)
        self.pushButton_3.clicked.connect(self.edit_detail)
        self.pushButton_4.clicked.connect(self.delete_detail)
        self.pushButton_7.clicked.connect(self.log_out)
    
    def log_out(self):
        self.window=Home()
        self.close()
        self.window.show()
    ################################# Opening tab #################################################
    def add_student(self):
        self.tabWidget.setCurrentIndex(0)
        self.Show_Handle_Operation()
    def update_detail(self):
        self.tabWidget.setCurrentIndex(1)
    ################################### Add detail #################################################
    def submit(self):
        department=self.comboBox.currentText()
        roll_no=self.lineEdit.text()
        name=self.lineEdit_2.text()
        father_name=self.lineEdit_3.text()
        mother_name=self.lineEdit_4.text()
        semester=self.comboBox_2.currentText()
        email=self.lineEdit_5.text()
        gender=self.comboBox_3.currentText()
        date=self.lineEdit_6.text()
        mobile_no=self.lineEdit_7.text()
        address=self.textEdit.toPlainText()
        picture=self.lineEdit_8.text()
        if department!='' and roll_no!='' and name!='' and father_name!='' and mother_name!=''and semester!='' and \
        email!='' and gender!='' and date!=''and mobile_no!='' and address!='' and picture!= '':
            if department!='Select Department' and semester!='Select Semester' and gender!='Select Gender':
                val=self.check(email)
                if val==True:
                    if re.search(r'([6789]\d{9}?)',mobile_no) and len(mobile_no) == 10:
                        self.cur.execute('''INSERT into student_record(department,roll_no,name,father_name,mother_name,semester,email,gender,date,mobile_no,address,picture)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',(department,roll_no,name,father_name,mother_name,semester,email,gender,date,mobile_no,address,picture))
                        self.db.commit()
                        self.Show_Handle_Operation()
                        self.c.message_information("Add Successfully!")
                        self.comboBox.setCurrentIndex(0)
                        self.comboBox_2.setCurrentIndex(0)
                        self.comboBox_3.setCurrentIndex(0)
                        self.lineEdit.setText('')
                        self.lineEdit_2.setText('')
                        self.lineEdit_3.setText('')
                        self.lineEdit_4.setText('')
                        self.lineEdit_5.setText('')
                        self.lineEdit_6.setText('')
                        self.lineEdit_7.setText('')
                        self.lineEdit_8.setText('')
                        self.textEdit.setText('')
                        
                    else:
                        self.c.message_warning("Please insert Valid Mobile No.")
                else:
                    self.c.message_warning("Please insert Valid Email-id")
            else:
                self.c.message_warning("Please Check that you have select right option")
        else:
            self.c.message_warning("Please Insert Entry")
    ################################################ Show Student Record ##############################
    def Show_Handle_Operation(self):
        self.cur.execute('''SELECT roll_no,name,father_name,mother_name,department,semester,email,gender,date,mobile_no,address FROM student_record''')
        data=self.cur.fetchall()
        if data:
            self.tableWidget.setRowCount(0)
            self.tableWidget.insertRow(0)
            for row,form in enumerate(data):
                for column,item in enumerate(form):
                    self.tableWidget.setItem(row,column,QTableWidgetItem(str(item)))
                    column+=1
                row_position=self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_position)
        else:
            self.tableWidget.clearContents()
                
    ######################################### Search Details ###########################################
    def setText(self):
        self.groupBox_3.setEnabled(False)
        self.lineEdit_9.setText('')
        self.lineEdit_10.setText('')
        self.lineEdit_11.setText('')
        self.lineEdit_12.setText('')
        self.lineEdit_13.setText('')
        self.lineEdit_14.setText('')
        self.lineEdit_15.setText('')
        self.lineEdit_16.setText('')
        self.textEdit_2.setText('')
        self.label.clear()
        self.comboBox_4.setCurrentIndex(0)
        self.comboBox_5.setCurrentIndex(0)
        self.comboBox_6.setCurrentIndex(0)
        self.lineEdit_10.setFocus()
    def search(self):
        roll_no=self.lineEdit_9.text()
        if roll_no!='':
            self.cur.execute('''SELECT name,father_name,mother_name,semester,department,email,gender,date,mobile_no,address,picture FROM student_record
                                                                                        where roll_no=%s''',[(roll_no)])
            data=self.cur.fetchone()
            if data!=None:
                self.groupBox_3.setEnabled(True)
                self.lineEdit_10.setText(roll_no)
                self.lineEdit_11.setText(data[0])
                self.lineEdit_12.setText(data[1])
                self.lineEdit_13.setText(data[2])
                self.comboBox_5.setCurrentText(str(data[3]))
                self.comboBox_4.setCurrentText(data[4])
                self.lineEdit_14.setText(data[5])
                self.comboBox_6.setCurrentText(data[6])
                self.lineEdit_15.setText(data[7])
                self.lineEdit_16.setText(str(data[8]))
                self.textEdit_2.setText(data[9])
                self.label.setPixmap(QPixmap(data[10]))
                self.label.setScaledContents(True)
            else:
                QMessageBox.warning(self,"Error","Student Record does not Exist.",QMessageBox.Ok)
                self.setText()
        else:
            QMessageBox.warning(self,"Error","Please Insert Entry",QMessageBox.Ok)
            self.lineEdit_9.setFocus()
    ###################################################### Update Details #################################################
    def edit_detail(self):
        roll_no=self.lineEdit_10.text()
        name=self.lineEdit_11.text()
        father_name=self.lineEdit_12.text()
        mother_name=self.lineEdit_13.text()
        department=self.comboBox_4.currentText()
        semester=self.comboBox_5.currentText()
        email=self.lineEdit_14.text()
        gender=self.comboBox_6.currentText()
        date=self.lineEdit_15.text()
        mobile_no=self.lineEdit_16.text()
        address=self.textEdit_2.toPlainText()

        if department!='' and roll_no!='' and name!='' and father_name!='' and mother_name!=''and semester!='' and \
        email!='' and gender!='' and date!=''and mobile_no!='' and address!='':
            if department!='Select Department' and semester!='Select Semester' and gender!='Select Gender':
                val=self.check(email)
                if val==True:
                    if re.search(r'([6789]\d{9}?)',mobile_no) and len(mobile_no) == 10:
                        self.cur.execute('''UPDATE student_record set name=%s,father_name=%s,mother_name=%s,department=%s,semester=%s,email=%s,gender=%s,
                        date=%s,mobile_no=%s,address=%s where roll_no=%s''',(name,father_name,mother_name,department,semester,email,gender,date,mobile_no,address,roll_no))
                        self.db.commit()
                        self.setText()
                        self.c.message_information("Update Successfully!")
                    else:
                        self.c.message_warning("Please insert Valid Mobile No.")
                else:
                    self.c.message_warning("Please insert Valid Email-id")
            else:
                self.c.message_warning("Please Check that you have select right option")
        else:
            self.c.message_warning("Please Insert Entry")
    
    def delete_detail(self):
        roll_no=self.lineEdit_9.text()
        response=QMessageBox.warning(self,"Delete Book","Are you want to delete this Record",QMessageBox.Yes|QMessageBox.No)
        if response ==QMessageBox.Yes:
            self.cur.execute('''DELETE FROM student_record WHERE roll_no=%s''',[(roll_no)])
            self.db.commit()
            self.setText()
            self.c.message_information("Delete Successfully!")
        else:
            self.lineEdit_11.setFocus()
    
class Attendance(QMainWindow,ui_attendance):
    c=Mess()
    def __init__(self):
        self.db = con.connect(host='localhost', user='root', password='root', db='attendance')
        self.cur = self.db.cursor()
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.show_attendance_record()
        self.Handel_Buttons()
    
    def Handel_Buttons(self):
        #self.pushButton.clicked.connect()
        self.pushButton_6.clicked.connect(self.log_out)
        self.pushButton.clicked.connect(self.update_attendance)
        self.pushButton_2.clicked.connect(self.clear)
        self.pushButton_3.clicked.connect(self.excel_report)
        self.pushButton_4.clicked.connect(self.delete_attendance)
    
    def log_out(self):
        self.window=Home()
        self.close()
        self.window.show()
    ####################################### Show Attendance ########################################################
    def show_attendance_record(self):
        self.cur.execute('''SELECT * FROM attendance_record''')
        show_detail=self.cur.fetchall()
        if show_detail:
            self.tableWidget.setRowCount(0)
            self.tableWidget.insertRow(0)
            for row,form in enumerate(show_detail):
                for column,item in enumerate(form):
                    self.tableWidget.setItem(row,column,QTableWidgetItem(str(item)))
                    column+=1
                row_position=self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_position)
        else:
            self.tableWidget.clearContents()
    ################################################# Update Attendance ##############################################
    def update_attendance(self):
        roll_no=self.lineEdit.text()
        name=self.lineEdit_2.text()
        date=self.lineEdit_3.text()
        attendance_status=self.comboBox.currentText()
        try:
            if roll_no!='' and name!='' and date!='':
                if attendance_status!='Select Status':
                    self.cur.execute('''UPDATE attendance_record SET status=%s WHERE roll_no=%s AND name=%s AND date=%s''',(attendance_status,roll_no,name,date))
                    self.db.commit()
                    self.clear()
                    self.show_attendance_record()
                    self.c.message_information("Update Successfully!")
                    self.lineEdit.setFocus()
                else:
                    self.c.message_warning("Please Check that you have select right option")
            else:
                self.c.message_warning("Please Insert Entry")
                self.lineEdit.setFocus()
        except Exception as e:
            print("Unknown error=",e)
            self.c.message_warning("Something Went Wrong")
    
    ################################################## Clear Button ####################################################
    def clear(self):
        self.lineEdit.setText("")
        self.lineEdit_2.setText("")
        self.lineEdit_3.setText("")
        self.comboBox.setCurrentIndex(0)
    ############################ Export Section ############################################
    def excel_report(self):
        date=self.lineEdit_4.text()
        self.cur.execute('''SELECT roll_no,name,semester,department,status,time FROM attendance_record WHERE date=%s''',([date]))
        data = self.cur.fetchall()

        wb=Workbook('report.xlsx')
        sheet1=wb.add_worksheet()
        sheet1.write(0,0,'Roll No.')
        sheet1.write(0,1,'Name')
        sheet1.write(0,2,'Semester')
        sheet1.write(0,3,'Department')
        sheet1.write(0,4,'Status')
        sheet1.write(0,5,'Time')

        row_number = 1
        for row in data:
            column = 0
            for item in row:
                sheet1.write(row_number, column, str(item))
                column += 1
            row_number += 1
        wb.close()
        self.lineEdit_4.setText('')
        self.c.message_information("Export Successfully!")
    ###################### Delete Attendance by date ######################################
    def delete_attendance(self):
        date=self.lineEdit_5.text()
        response = QMessageBox.warning(self, "Delete Attendance", "Are you want to delete Attendance",QMessageBox.Yes | QMessageBox.No)
        if response == QMessageBox.Yes:
            self.cur.execute('''DELETE FROM attendance_record WHERE date=%s''', [(date)])
            self.db.commit()
            self.lineEdit_5.setText("")
            self.c.message_information("Delete Successfully!")
            self.show_attendance_record()
            self.lineEdit_5.setFocus()
        else:
            self.lineEdit_5.setFocus()


def main():
    app=QApplication(sys.argv)
    window=Home()
    window.show()
    app.exec_()

if __name__=='__main__':
    main()
