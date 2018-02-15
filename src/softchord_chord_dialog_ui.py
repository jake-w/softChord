# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'softchord_chord_dialog.ui'
#
# Created: Tue Jul 03 00:18:17 2012
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(470, 149)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.marker_ef = QtWidgets.QLineEdit(Dialog)
        self.marker_ef.setMinimumSize(QtCore.QSize(30, 0))
        self.marker_ef.setMaximumSize(QtCore.QSize(80, 16777215))
        self.marker_ef.setObjectName("marker_ef")
        self.horizontalLayout.addWidget(self.marker_ef)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.note_menu = QtWidgets.QComboBox(Dialog)
        self.note_menu.setMinimumSize(QtCore.QSize(90, 0))
        self.note_menu.setObjectName("note_menu")
        self.horizontalLayout.addWidget(self.note_menu)
        self.chord_type_menu = QtWidgets.QComboBox(Dialog)
        self.chord_type_menu.setObjectName("chord_type_menu")
        self.horizontalLayout.addWidget(self.chord_type_menu)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.bass_menu = QtWidgets.QComboBox(Dialog)
        self.bass_menu.setMinimumSize(QtCore.QSize(90, 0))
        self.bass_menu.setObjectName("bass_menu")
        self.horizontalLayout.addWidget(self.bass_menu)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.in_parentheses_box = QtWidgets.QCheckBox(Dialog)
        self.in_parentheses_box.setObjectName("in_parentheses_box")
        self.verticalLayout.addWidget(self.in_parentheses_box)
        spacerItem1 = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
             
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject) 
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        
        Dialog.setTabOrder(self.note_menu, self.chord_type_menu)
        Dialog.setTabOrder(self.chord_type_menu, self.bass_menu)
        Dialog.setTabOrder(self.bass_menu, self.in_parentheses_box)
        Dialog.setTabOrder(self.in_parentheses_box, self.marker_ef)
        Dialog.setTabOrder(self.marker_ef, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Chord Selector", None))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Chord for selected letter:", None))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", ":", None))
        self.label_3.setText(QtWidgets.QApplication.translate("Dialog", "/", None))
        self.in_parentheses_box.setText(QtWidgets.QApplication.translate("Dialog", "In parentheses", None))

