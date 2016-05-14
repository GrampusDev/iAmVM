# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'monitor_GUI.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_iAmVM(object):
    def setupUi(self, iAmVM):
        iAmVM.setObjectName(_fromUtf8("iAmVM"))
        iAmVM.resize(463, 296)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("icons/Virtualbox_logo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iAmVM.setWindowIcon(icon)
        iAmVM.setStyleSheet(_fromUtf8("background-color: rgb(226, 233, 255);"))
        self.centralwidget = QtGui.QWidget(iAmVM)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.block = QtGui.QPushButton(self.centralwidget)
        self.block.setGeometry(QtCore.QRect(300, 240, 101, 31))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8("icons/Remove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.block.setIcon(icon1)
        self.block.setObjectName(_fromUtf8("block"))
        self.allow_once = QtGui.QPushButton(self.centralwidget)
        self.allow_once.setGeometry(QtCore.QRect(180, 240, 101, 31))
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8("icons/accept.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.allow_once.setIcon(icon2)
        self.allow_once.setObjectName(_fromUtf8("allow_once"))
        self.allow = QtGui.QPushButton(self.centralwidget)
        self.allow.setGeometry(QtCore.QRect(60, 240, 101, 31))
        self.allow.setIcon(icon2)
        self.allow.setObjectName(_fromUtf8("allow"))
        self.textBox = QtGui.QTextEdit(self.centralwidget)
        self.textBox.setGeometry(QtCore.QRect(30, 70, 401, 151))
        self.textBox.setAutoFillBackground(False)
        self.textBox.setObjectName(_fromUtf8("textBox"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(180, 0, 91, 61))
        self.label.setText(_fromUtf8(""))
        self.label.setPixmap(QtGui.QPixmap(_fromUtf8("icons/malware-detection-website-icon-large.png")))
        self.label.setScaledContents(True)
        self.label.setObjectName(_fromUtf8("label"))
        iAmVM.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(iAmVM)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        iAmVM.setStatusBar(self.statusbar)

        self.retranslateUi(iAmVM)
        QtCore.QMetaObject.connectSlotsByName(iAmVM)

    def retranslateUi(self, iAmVM):
        iAmVM.setWindowTitle(_translate("iAmVM", "iAmVM", None))
        self.block.setText(_translate("iAmVM", "Block", None))
        self.allow_once.setText(_translate("iAmVM", "Allow Once", None))
        self.allow.setText(_translate("iAmVM", "Allow", None))

