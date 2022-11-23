import sys
from crossword import *
from generate import *


from PySide6.QtWidgets import (
    QMainWindow, QApplication,
    QLabel, QComboBox, QLineEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QGridLayout, QProgressDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

class FinalWindow(QWidget):
    def __init__(self, structure, words):
        super(FinalWindow, self).__init__()
        self.setFixedWidth(600)
        self.setFixedHeight(400)
        
        self.structure = structure
        self.words = words
        
        crossword = Crossword(self.structure, self.words)
        creator = CrosswordCreator(crossword)
        assignment = creator.solve()
        
        layout = QVBoxLayout()
        
        if assignment is None:
            #print("No solution.")
            photo_label = QLabel(self)
            pixmap = QPixmap('assets/images/error.png')
            photo_label.setPixmap(pixmap)
            photo_label.setScaledContents(True)
            self.resize(pixmap.width(), pixmap.height())
            
            thelabel = QLabel('No Solution, please try different words or structre')
            font = thelabel.font()
            font.setPointSize(10)
            thelabel.setFont(font)
            thelabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

                             
        else:
            photo_label = QLabel(self)
            creator.create_image(assignment, 'result.png')
            pixmap = QPixmap('result.png')
            photo_label.setPixmap(pixmap)
            photo_label.setScaledContents(True)
            self.resize(pixmap.width(), pixmap.height())
            
            thelabel = QLabel('successfully generated')
            font = thelabel.font()
            font.setPointSize(10)
            thelabel.setFont(font)
            thelabel.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)                  
        
        layout.addWidget(photo_label)
        layout.addWidget(thelabel)
        self.setLayout(layout)

class AnotherWindow(QWidget):
    
    

    def __init__(self):
        super(AnotherWindow, self).__init__()
        self.setFixedWidth(300)
        self.setFixedHeight(300)
     
        
        
        layout = QVBoxLayout()
        instructions = QLabel("""Upload your strucutre, 
and the words, then press on generate""")
        font = instructions.font()
        font.setPointSize(10)
        instructions.setFont(font)
        instructions.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        upload_st = QPushButton("upload structure")
        upload_words = QPushButton("upload words")
        generate = QPushButton("generate")
        
        upload_st.clicked.connect(self.upload_structure)
        
        upload_words.clicked.connect(self.upload_words)
        
        generate.clicked.connect(self.generate)

        
       
        
        layout.addWidget(instructions)
        layout.addWidget(upload_st)
        layout.addWidget(upload_words)
        layout.addWidget(generate)
       
        
        self.setLayout(layout)
     
    
    def upload_structure(self, checked):
        self.upload_1 = QFileDialog.getOpenFileName(self)
        
        self.structure = (self.upload_1[0])
    
    
    def upload_words(self):
        self.upload_2 = QFileDialog.getOpenFileName(self)
        
        self.words = (self.upload_2[0])
        
        
        
    def generate(self):
        self.window2 = FinalWindow(self.structure, self.words)
        if self.window2.isVisible():
            self.window2.hide()

        else:
            self.window2.show()  
        
        
    
        
        
    
    



class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.window1 = AnotherWindow()
        

        self.setWindowTitle("Fadel's CNN program")
        self.setFixedWidth(500)
        self.setFixedHeight(500)
        
        layout1 = QVBoxLayout()

        
        widget = QLabel("""Simple program that able to create
crossword puzzle
coded using python, and pyside6""")
        font = widget.font()
        font.setPointSize(15)
        widget.setFont(font)
        widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        
        start_btn = QPushButton("Start Now!")
        start_btn.clicked.connect(self.toggle_window1)
        start_btn.setAutoDefault(True)
        
        layout1.addWidget(widget)
        layout1.addWidget(start_btn)

        
        widget = QWidget()
        widget.setLayout(layout1)
        self.setCentralWidget(widget)
        
    def toggle_window1(self, checked):
        if self.window1.isVisible():
            self.window1.hide()

        else:
            self.window1.show()

    


    
    

  
        

app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()