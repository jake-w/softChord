# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'softchord_pdf_dialog.ui'
#
# Created: Tue Jul 03 00:15:21 2012
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):  
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(500, 379)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.print_song_num_box = QtWidgets.QCheckBox(Dialog)
        self.print_song_num_box.setObjectName("print_song_num_box")
        self.verticalLayout.addWidget(self.print_song_num_box)
        self.print_song_title_box = QtWidgets.QCheckBox(Dialog)
        self.print_song_title_box.setObjectName("print_song_title_box")
        self.verticalLayout.addWidget(self.print_song_title_box)
        self.print_song_key_box = QtWidgets.QCheckBox(Dialog)
        self.print_song_key_box.setObjectName("print_song_key_box")
        self.verticalLayout.addWidget(self.print_song_key_box)
        self.print_song_comment_box = QtWidgets.QCheckBox(Dialog)
        self.print_song_comment_box.setObjectName("print_song_comment_box")
        self.verticalLayout.addWidget(self.print_song_comment_box)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_7 = QtWidgets.QLabel(Dialog)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 0, 0, 1, 1)
        self.top_margin_ef = QtWidgets.QLineEdit(Dialog)
        self.top_margin_ef.setMaximumSize(QtCore.QSize(80, 16777215))
        self.top_margin_ef.setObjectName("top_margin_ef")
        self.gridLayout.addWidget(self.top_margin_ef, 0, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 0, 2, 1, 1)
        self.label_8 = QtWidgets.QLabel(Dialog)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 1, 0, 1, 1)
        self.bottom_margin_ef = QtWidgets.QLineEdit(Dialog)
        self.bottom_margin_ef.setMaximumSize(QtCore.QSize(80, 16777215))
        self.bottom_margin_ef.setObjectName("bottom_margin_ef")
        self.gridLayout.addWidget(self.bottom_margin_ef, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 1, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.left_margin_ef = QtWidgets.QLineEdit(Dialog)
        self.left_margin_ef.setMaximumSize(QtCore.QSize(80, 16777215))
        self.left_margin_ef.setObjectName("left_margin_ef")
        self.gridLayout.addWidget(self.left_margin_ef, 2, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 3, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.right_margin_ef = QtWidgets.QLineEdit(Dialog)
        self.right_margin_ef.setMaximumSize(QtCore.QSize(80, 16777215))
        self.right_margin_ef.setObjectName("right_margin_ef")
        self.gridLayout.addWidget(self.right_margin_ef, 3, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 3, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_9 = QtWidgets.QLabel(Dialog)
        self.label_9.setObjectName("label_9")
        self.horizontalLayout.addWidget(self.label_9)
        self.page_width_ef = QtWidgets.QLineEdit(Dialog)
        self.page_width_ef.setMaximumSize(QtCore.QSize(80, 16777215))
        self.page_width_ef.setObjectName("page_width_ef")
        self.horizontalLayout.addWidget(self.page_width_ef)
        self.label_11 = QtWidgets.QLabel(Dialog)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout.addWidget(self.label_11)
        self.page_height_ef = QtWidgets.QLineEdit(Dialog)
        self.page_height_ef.setMaximumSize(QtCore.QSize(80, 16777215))
        self.page_height_ef.setObjectName("page_height_ef")
        self.horizontalLayout.addWidget(self.page_height_ef)
        self.label_10 = QtWidgets.QLabel(Dialog)
        self.label_10.setObjectName("label_10")
        self.horizontalLayout.addWidget(self.label_10)
        spacerItem1 = QtWidgets.QSpacerItem(2, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.alternate_margins_box = QtWidgets.QCheckBox(Dialog)
        self.alternate_margins_box.setObjectName("alternate_margins_box")
        self.verticalLayout.addWidget(self.alternate_margins_box)
        self.print_4_per_page_box = QtWidgets.QCheckBox(Dialog)
        self.print_4_per_page_box.setObjectName("print_4_per_page_box")
        self.verticalLayout.addWidget(self.print_4_per_page_box)
        self.generate_table_of_contents_box = QtWidgets.QCheckBox(Dialog)
        self.generate_table_of_contents_box.setObjectName("generate_table_of_contents_box")
        self.verticalLayout.addWidget(self.generate_table_of_contents_box)
        spacerItem2 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtWidgets.QApplication.translate("Dialog", "Pdf Export Settings", None))
        self.print_song_num_box.setText(QtWidgets.QApplication.translate("Dialog", "Print song number", None))
        self.print_song_title_box.setText(QtWidgets.QApplication.translate("Dialog", "Print song title", None))
        self.print_song_key_box.setText(QtWidgets.QApplication.translate("Dialog", "Print song key & alternative key", None))
        self.print_song_comment_box.setText(QtWidgets.QApplication.translate("Dialog", "Print song comment (note)", None))
        self.label_7.setText(QtWidgets.QApplication.translate("Dialog", "Top margin:", None))
        self.top_margin_ef.setText(QtWidgets.QApplication.translate("Dialog", "0.5", None))
        self.label_6.setText(QtWidgets.QApplication.translate("Dialog", "inches", None))
        self.label_8.setText(QtWidgets.QApplication.translate("Dialog", "Bottom margin:", None))
        self.bottom_margin_ef.setText(QtWidgets.QApplication.translate("Dialog", "0.5", None))
        self.label_5.setText(QtWidgets.QApplication.translate("Dialog", "inches", None))
        self.label_2.setText(QtWidgets.QApplication.translate("Dialog", "Left margin:", None))
        self.left_margin_ef.setText(QtWidgets.QApplication.translate("Dialog", "0.5", None))
        self.label_3.setText(QtWidgets.QApplication.translate("Dialog", "inches", None))
        self.label.setText(QtWidgets.QApplication.translate("Dialog", "Right margin", None))
        self.right_margin_ef.setText(QtWidgets.QApplication.translate("Dialog", "0.5", None))
        self.label_4.setText(QtWidgets.QApplication.translate("Dialog", "inches", None))
        self.label_9.setText(QtWidgets.QApplication.translate("Dialog", "Page size width:", None))
        self.page_width_ef.setText(QtWidgets.QApplication.translate("Dialog", "8.5", None))
        self.label_11.setText(QtWidgets.QApplication.translate("Dialog", "height:", None))
        self.page_height_ef.setText(QtWidgets.QApplication.translate("Dialog", "11", None))
        self.label_10.setText(QtWidgets.QApplication.translate("Dialog", "inches", None))
        self.alternate_margins_box.setText(QtWidgets.QApplication.translate("Dialog", "Reverse left and right margins for even pages", None))
        self.print_4_per_page_box.setText(QtWidgets.QApplication.translate("Dialog", "Print 4 copies of same song per page", None))
        self.generate_table_of_contents_box.setText(QtWidgets.QApplication.translate("Dialog", "Generate table of contents page(s)", None))

