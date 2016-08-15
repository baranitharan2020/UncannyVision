import os
from PyQt4 import QtCore, QtGui

class PhotoViewer(QtGui.QGraphicsView):
	globalItem = []
	globalCircleItem = []
	globalConnectItem = []
	globalLoop = []
	
	def __init__(self, parent):
		super(PhotoViewer, self).__init__(parent)
		self.centralWidget = parent
		self.boolSetPath = 0
		self._zoom = 0
		self._scene = QtGui.QGraphicsScene(self)
		self._photo = QtGui.QGraphicsPixmapItem()
		self._scene.addItem(self._photo)
		self.setScene(self._scene)
		self.setTransformationAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setResizeAnchor(QtGui.QGraphicsView.AnchorUnderMouse)
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
		self.setFrameShape(QtGui.QFrame.NoFrame)
		self.loopStart = 1
		self._pos = []
		self._save = []
		self.session_loops = 0		#number of loops in the current session

	def mousePressEvent(self, event):
		super (PhotoViewer, self).mousePressEvent(event)
		if self.boolSetPath:
			self.loopStart = 0
			rad = 7
			pen = QtGui.QPen(QtCore.Qt.red, 4, QtCore.Qt.SolidLine)
			pos = self.mapToScene(event.x(), event.y())
			self._save.append((event.x(), event.y()))
			self.globalCircleItem.append(QtGui.QGraphicsEllipseItem(pos.x(), pos.y(), rad, rad))
			self.globalItem.append(self.globalCircleItem[-1])
			self.globalCircleItem[-1].setPen(pen)
			#self._scene.addEllipse(pos.x(), pos.y(), rad, rad, pen)
			self._scene.addItem(self.globalCircleItem[-1])
			self._pos.append(pos)
			if len(self._pos) > 1:
				start = self._pos[-2]
				end = self._pos[-1]
				self.globalConnectItem.append(QtGui.QGraphicsLineItem(QtCore.QLineF(start, end)))
				self.globalItem.append(self.globalConnectItem[-1])
				self._scene.addItem(self.globalConnectItem[-1])
		else:
			QtGui.QMessageBox.information(self, 'INFO', "Enter the image and annotation paths to mark the joints!", QtGui.QMessageBox.Ok)

	def contextMenuEvent(self, event):
		self.loopStart = 1
		start = self._pos[-1]
		end = self._pos[0]
		self.globalLoop.append(self._save)
		self._save = []
		self.globalConnectItem.append(QtGui.QGraphicsLineItem(QtCore.QLineF(start, end)))
		self.globalItem.append(self.globalConnectItem[-1])
		self._scene.addItem(self.globalConnectItem[-1])
		self.scrollWidget.addPersonDetails()
		self._pos = []
		self.session_loops += 1
		if executableSettings().popupLabelFlag:
			self.centralWidget.dynamicActionLabeler.popup(self.scrollWidget.totalPersonCount-1)

	def fitInView(self):
		rect = QtCore.QRectF(self._photo.pixmap().rect())
		if not rect.isNull():
			viewrect = self.viewport().rect()
			scenerect = self.transform().mapRect(rect)
			factorW = viewrect.width() / scenerect.width()
			factorH = viewrect.height() / scenerect.height()
			self.scale(factorW, factorH)
			self.centerOn(rect.center())
			self._zoom = 0

	def setPhoto(self, pixmap=None):
		self._zoom = 0
		if pixmap and not pixmap.isNull():
			self._photo.setPixmap(pixmap)
			self.fitInView()
		else:
			self._photo.setPixmap(QtGui.QPixmap())

	def zoomFactor(self):
		return self._zoom

	def wheelEvent(self, event):
		if not self._photo.pixmap().isNull():
			if event.delta() > 0:
				factor = 1.25
				self._zoom += 1
			else:
				factor = 0.8
				self._zoom -= 1
			if self._zoom > 0:
				self.scale(factor, factor)
			elif self._zoom == 0:
				self.fitInView()
			else:
				self._zoom = 0

class CentralWidget(QtGui.QWidget):
	imageNames = []
	imgCount = 0
	imagePath = None
	imgActionDict = []
	reading = 0
	def __init__(self, parent):
		super(CentralWidget, self).__init__(parent)
		
		self.viewer = PhotoViewer(self)
		
		self.imageNamePrint = QtGui.QLabel(self)
		
		self.edit = QtGui.QLineEdit(self)
		self.edit.setReadOnly(True)
		self.button = QtGui.QToolButton(self)
		self.button.setText('&Image Path')
		self.button.clicked.connect(self.imageOpen)
		
		self.edit2 = QtGui.QLineEdit(self)
		self.edit2.setReadOnly(True)
		self.button2 = QtGui.QToolButton(self)
		self.button2.setText('&Annotation Path')
		self.button2.clicked.connect(self.annotationOpen) 
		
		self.actionLabel = (QtGui.QLabel(self))
		self.actionLabel.setText("Enter the details of selections : ")
		
		self.dialog = JumpImgDialog(self)
		self.connect(self, QtCore.SIGNAL('mysignal(int)'), self.dialog.jumpToImage) 
				  
		self.readAllImgActionLabels(parent) 
		self.scrollWidget = labelWidget(self)	
		self.scrollWidget.imgActionDict = self.imgActionDict
		
		self.dynamicActionLabeler = popupActionLabeler(self)

		self.viewer.scrollWidget = self.scrollWidget

		# scroll area
		self.scrollArea = QtGui.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.scrollWidget)
		self.scrollArea.setMaximumWidth(250)
		
		# main layout
		self.mainLayout = QtGui.QGridLayout()
		self.mainLayout.addWidget(self.imageNamePrint,0,0,1,1)
		self.mainLayout.addWidget(self.viewer,1,0,2,1)
		self.mainLayout.addWidget(self.scrollArea,1,1)
		self.mainLayout.addWidget(self.actionLabel,0,1)
		self.mainLayout.addWidget(self.edit,3,0)
		self.mainLayout.addWidget(self.button,3,1)
		self.mainLayout.addWidget(self.edit2,4,0)
		self.mainLayout.addWidget(self.button2,4,1)
		
		self.button2.setMaximumWidth(250)
		self.button.setMaximumWidth(250)

		# central widget
		self.setLayout(self.mainLayout)
		
	def readAnnotation(self):
		self.reading = 1
		f = open(self.annotationPath + '/' + self.annotationName)
		temp = f.read()
		if temp:
			dict_ = eval(temp)
			rad = 7
			point_ctr = []
			person_index = -1

			for i in xrange(len(dict_)):
				p = 'Person' + str(i+1)
				person = dict_[p]
				point_ctr.append(0)
				
				#updating the variables
				self.viewer.globalLoop.append([])
				for x, y in person['Loop']:
					pos = self.viewer.mapToScene(x, y)
					self.viewer._pos.append(pos)
					self.viewer.globalCircleItem.append(QtGui.QGraphicsEllipseItem(pos.x(), pos.y(), rad, rad))
					point_ctr[-1] += 1
					self.viewer.globalItem.append(self.viewer.globalCircleItem[-1])
					self.viewer.globalLoop[i].append((x, y))
					if len(self.viewer._pos) > 1:
						start = self.viewer._pos[-2]
						end = self.viewer._pos[-1]
						self.viewer.globalConnectItem.append(QtGui.QGraphicsLineItem(QtCore.QLineF(start, end)))
						self.viewer.globalItem.append(self.viewer.globalConnectItem[-1])
				if self.viewer._pos:
					start = self.viewer._pos[-1]
					end = self.viewer._pos[0]
					self.viewer.globalConnectItem.append(QtGui.QGraphicsLineItem(QtCore.QLineF(start, end)))
					self.viewer.globalItem.append(self.viewer.globalConnectItem[-1])
				self.viewer._pos = []				

				person_index += 1
				action = person['ImageAction']
				
				#drawing circles and lines
				color = [QtCore.Qt.red, QtCore.Qt.black, QtCore.Qt.green, QtCore.Qt.cyan, QtCore.Qt.magenta, QtCore.Qt.blue, QtCore.Qt.yellow]
				actions = [None, 'Standing', 'Sleeping', 'Sitting', 'Walking', 'Crouching']
				
				pen = QtGui.QPen(color[0], 4, QtCore.Qt.SolidLine)
				for point in xrange(point_ctr[person_index]):
					circle = self.viewer.globalCircleItem[sum(point_ctr[:person_index]) + point]
					circle.setPen(pen)
					self.viewer._scene.addItem(circle)
				
				line_color = color[actions.index(action)+1]
				pen = QtGui.QPen(line_color, 5, QtCore.Qt.SolidLine)
				for point in xrange(point_ctr[person_index]):
					line = self.viewer.globalConnectItem[sum(point_ctr[:person_index]) + point]
					line.setPen(pen)
					self.viewer._scene.addItem(line)

				self.scrollWidget.addPersonDetails()
				if action == None:
					actionId = 0
				else:
					actionId = self.imgActionDict.index(action)
				self.scrollWidget.actionSelect(i, actionId)
		self.viewer.loopStart = 1
		self.reading = 0

	def saveAnnotation(self):
		if len(self.viewer.globalLoop) or os.path.isfile(self.annotationPath+self.annotationName):
			f = open(self.annotationPath + self.annotationName, 'w+')
			content = f.read()
			try:
				if not content:
					f.write("{")
				for varJ in xrange(len(self.viewer.globalLoop)):
					p = 'Person' + str(varJ+1)
					p = "'" + p + "'" + ': '
					f.write(p)
					f.write("{")
					
					f.write("'Loop': ")
					f.write("[")
					for varI in self.viewer.globalLoop[varJ]:
						f.write(str((varI[0], varI[1])) + ", ")
					f.write("], ")
					
					f.write("'ImageAction': ")
					if self.scrollWidget.personBox[varJ].actionBox.currentIndex():
						f.write("'%s'"%self.scrollWidget.personBox[varJ].actionBox.itemText(self.scrollWidget.personBox[varJ].actionBox.currentIndex()))
					else:
						f.write('None')
					f.write("}, ")
				f.write("}")
			except Exception as e:
				print 'Error:', e, 'on line {}'.format(sys.exc_info()[-1].tb_lineno)
				f.truncate(0)
			f.close()
		
	def clearAnnotation(self):
		for varI in xrange(len(self.viewer.globalItem)):
			self.viewer._scene.removeItem(self.viewer.globalItem[varI])
		for varI in xrange(len(self.scrollWidget.personBox)):
			self.scrollWidget.removePersonDetails()
		self.viewer.globalLoop = []
		self.viewer.globalItem = []
		self.viewer.globalCircleItem = []
		self.viewer.globalConnectItem = []

	def checkLoopCompletion(self):
		if not self.viewer.loopStart:
			QtGui.QMessageBox.critical(self, 'Close the loop!', 'Press right click to close the loop.', QtGui.QMessageBox.Ok)
			return False
		return True
	
	def helpWindow(self):
		helpMenu = ("KEY\tDESCRIPTION\n"
					" N \tTo go to next image\n"
					" P \tTo go to previous image\n"
					" U \tTo undo the last annotation in the image\n"
					" C \tTo clear all the annotations in the image\n"
					" J \tTo jump to a particular image\n"
					" Q \tTo quit the application\n"
					" H \tTo go to help menu\n")
		QtGui.QMessageBox.information(self, 'Help Menu', helpMenu, QtGui.QMessageBox.Ok)
		
	mysignal = QtCore.pyqtSignal(int, name='mysignal')
	def keyPressEvent(self, event):
		super (CentralWidget, self).keyPressEvent(event)
		
		if self.viewer.boolSetPath:
			if event.key() == QtCore.Qt.Key_U:	# undo last label
				if self.viewer.globalItem:
					if self.viewer.loopStart:
						self.viewer._scene.removeItem(self.viewer.globalItem[-1])
						self.viewer._scene.removeItem(self.viewer.globalItem[-2])
						self.viewer._scene.removeItem(self.viewer.globalItem[-3])
						self.viewer.globalItem = self.viewer.globalItem[:-3]
						self.viewer.globalConnectItem = self.viewer.globalConnectItem[:-2]
						self.viewer.globalCircleItem = self.viewer.globalCircleItem[:-1]
						self.viewer._save = self.viewer.globalLoop[-1][:-1]
						self.viewer.globalLoop = self.viewer.globalLoop[:-1]
						self.viewer._pos = [self.viewer.mapToScene(i[0], i[1]) for i in self.viewer._save]
						self.viewer.loopStart = 0
						self.scrollWidget.removePersonDetails()
					else:
						if str(type(self.viewer.globalItem[-1])) == "<class 'PyQt4.QtGui.QGraphicsLineItem'>":
							self.viewer._scene.removeItem(self.viewer.globalItem[-1])
							self.viewer._scene.removeItem(self.viewer.globalItem[-2])
							self.viewer.globalItem = self.viewer.globalItem[:-2]
							self.viewer.globalConnectItem = self.viewer.globalConnectItem[:-1]
							self.viewer.globalCircleItem = self.viewer.globalCircleItem[:-1]
							self.viewer._save = self.viewer._save[:-1]
							self.viewer._pos = [self.viewer.mapToScene(i[0], i[1]) for i in self.viewer._save]
						else:
							self.viewer._scene.removeItem(self.viewer.globalItem[-1])
							self.viewer.globalItem.pop()
							self.viewer.globalCircleItem.pop()
							self.viewer._pos = []
							self.viewer._save = []
							self.viewer.loopStart = 1

			elif event.key() == QtCore.Qt.Key_C and self.checkLoopCompletion():	#clear all labels in the image
				self.clearAnnotation()
			elif event.key() == QtCore.Qt.Key_N and self.checkLoopCompletion():	#goto next image
				self.saveAnnotation()  
				self.clearAnnotation()
				if self.imgCount == len(self.imageNames):	#fix
					self.hide()
					event.ignore()
					sys.exit()
				else:
					self.imageAnnotation(self.imgCount)
			elif event.key() == QtCore.Qt.Key_P and self.checkLoopCompletion():	# goto previous image
				self.saveAnnotation()
				if self.imgCount-1:
					self.clearAnnotation()
					self.imageAnnotation(self.imgCount-2)
			elif event.key() == QtCore.Qt.Key_J:	# jump to image
				if not self.viewer.boolSetPath:
					QtGui.QMessageBox.information(self, 'INFO', "Enter the image and annotation paths to mark the joints!", QtGui.QMessageBox.Ok)
				else:
					self.mysignal.emit((len(self.imageNames)))
					if self.dialog.edit.text():
						idxVal = int(self.dialog.edit.text())
					else:
						idxVal = 0
					if idxVal and self.checkLoopCompletion():
						self.saveAnnotation()  
						self.clearAnnotation()
						self.imgCount = idxVal - 1
						self.imageAnnotation(self.imgCount)
			elif event.key() == QtCore.Qt.Key_Q and self.checkLoopCompletion():	# quit
				self.saveAnnotation()  
				self.clearAnnotation()
				self.hide()
				event.ignore()
				sys.exit()	#exit(app.exec_())	#anoopkp: fix this 
		else:
			if event.key() == QtCore.Qt.Key_Q:
				sys.exit()	#exit(app.exec_())	#anoopkp: fix this 
		if event.key() == QtCore.Qt.Key_H:	# help
			self.helpWindow()
		if self.imgCount:
			self.imageNamePrint.setText("Viewing image : %s\t\t(%d/%d)"%(self.imageNames[self.imgCount-1], self.imgCount, len(self.imageNames)))
	
	def imageAnnotation(self, callCount):
		self.viewer.setPhoto(QtGui.QPixmap(self.imagePath+self.imageNames[callCount]))
		self.annotationName = os.path.splitext(self.imageNames[callCount])[0]+'.txt'
		if os.path.isfile(self.annotationPath+self.annotationName):
			self.readAnnotation()
		if callCount < self.imgCount:
			self.imgCount -= 1
		else:
			self.imgCount += 1
		self.imageNamePrint.setText("Viewing image : %s\t\t(%d/%d)"%(self.imageNames[callCount], self.imgCount, len(self.imageNames)))

	def imageOpen(self):
		self.imagePath = QtGui.QFileDialog.getExistingDirectory(
			self, 'Choose Image Path', self.edit.text())
		self.imagePath.append("/")
		if self.imagePath:
			self.edit.setText(self.imagePath)
			for file in os.listdir(self.imagePath):
				if file.endswith((".bmp",".jpg",".png")):
					self.imageNames.append(file)
			self.edit.setEnabled(False)
			self.button.setEnabled(False)
			
	def annotationOpen(self):
		if self.imagePath:
			self.annotationPath = QtGui.QFileDialog.getExistingDirectory(
				self, 'Choose Annotation Path', self.edit2.text())
			#self.annotationPath = QtCore.QString("./")
			self.annotationPath.append("/")
			if self.annotationPath:
				self.edit2.setText(self.annotationPath)
				self.imageAnnotation(self.imgCount)
				self.viewer.boolSetPath = 1
				self.statusBar.clearMessage()
			self.edit2.setEnabled(False)
			self.button2.setEnabled(False)
		else:
			QtGui.QMessageBox.information(self, 'INFO', "Enter the image path first!", QtGui.QMessageBox.Ok)
					
	def readAllImgActionLabels(self, parent):
		del self.imgActionDict[:]
		if os.path.isfile(parent.settingsObj.imgActionDictFName):
			f = open(parent.settingsObj.imgActionDictFName,'r')
			for line in f:
				self.imgActionDict.append( line.rstrip() )
			f.close()
		else:
			QtGui.QMessageBox.information(self, 'ERROR', "Action dictionary not found!", QtGui.QMessageBox.Ok)

	def change_color(self):
		if not self.reading:
			self.saveAnnotation()
			self.clearAnnotation()
			self.readAnnotation()

class executableSettings():
	def __init__(self):
		self.popupLabelFlag = 0
		self.imgActionDictFName = "./actionDict.txt"
		self.readSettings()
		
	def readSettings(self):  
		settingsFile = os.getcwd() + '/' + '.loop_marker.settings'
		
		if os.path.isfile(settingsFile):
			f = open(settingsFile,'r')
			for line in f:
				data = line.rstrip().split()
				#print 'data', data
				if len(data):
					if data[0] == 'popupLabeler':
						self.popupLabelFlag = int(data[1])
					if data[0] == 'actionDict':
						self.imgActionDictFName = data[1]
			f.close()
		
	def saveSettings(self):
		settingsFile = os.getcwd() + '/' + '.loop_marker.settings'
		f = open(settingsFile,'w')
		f.write('popupLabeler %d\n' % self.popupLabelFlag)
		f.write('actionDict %s\n' % self.imgActionDictFName)
		
		f.close()

class Window(QtGui.QMainWindow):
	def __init__(self):
		super(Window, self).__init__()
		
		self.settingsObj = executableSettings()
		
		self.statusBar()
		self.statusBar().showMessage("Enter the image path and annotation path")
		
		quitMenu = QtGui.QAction('&Quit', self)
		quitMenu.setShortcut("Ctrl+Q")
		quitMenu.setStatusTip('Leave the App')
		quitMenu.triggered.connect(self.close)
		
		settingsMenu = QtGui.QAction('&Settings', self)
		settingsMenu.setShortcut("Ctrl+S")
		settingsMenu.setStatusTip('Change basic settings')
		settingsMenu.triggered.connect(lambda: SettingsDialog(self))
		
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		fileMenu.addAction(quitMenu)
		fileMenu = mainMenu.addMenu('&Tools')
		fileMenu.addAction(settingsMenu)
		
		centralWidget = CentralWidget(self)
		centralWidget.statusBar = self.statusBar()
		self.setCentralWidget(centralWidget)

class JumpImgDialog(QtGui.QDialog):
	def __init__(self, parent):
		super(JumpImgDialog, self).__init__()
		self.setWindowTitle("Jump to :")
		self.setWindowModality(QtCore.Qt.ApplicationModal)
		self.label1 = QtGui.QLabel(self)
		self.label2 = QtGui.QLabel(self)
		self.edit = QtGui.QLineEdit(self)
		
		self.button = QtGui.QToolButton(self)
		self.button.setText('OK')

		layout = QtGui.QGridLayout(self)
		layout.addWidget(self.label1, 0, 0)
		layout.addWidget(self.label2, 1, 0)
		layout.addWidget(self.edit, 2, 0)
		layout.addWidget(self.button, 2, 1)
		self.button.clicked.connect(self.close)
		self.edit.returnPressed.connect(self.button.click)

	def jumpToImage(self, param):
		self.imgCount = param
		self.label1.setText('  Total number of images is : %d' % self.imgCount)
		self.label2.setText('  Skip to (0 - %d) :' % self.imgCount)
		self.edit.setValidator(QtGui.QIntValidator(0,self.imgCount))	#limit is working. now use this!!
		self.exec_()

class labelWidget(QtGui.QWidget):
	personBox = []
	imgActionDict = None
	def __init__(self, parent):
		super(labelWidget, self).__init__(parent)
		self.parent = parent
		# scroll area widget contents - layout
		self.scrollLayout = QtGui.QFormLayout()

		# scroll area widget contents
		self.setLayout(self.scrollLayout)

		self.totalPersonCount = 0

	def actionSelect(self, personIdx, selectIdx):
		self.personBox[personIdx].actionBox.setCurrentIndex(selectIdx)

	def removePersonDetails(self):
		self.personBox[-1].deleteLater()
		del self.personBox[-1]
		self.totalPersonCount -= 1
		self.update()
		self.layout().update()

	def addPersonDetails(self):
		varI = self.totalPersonCount 
		self.personBox.append(QtGui.QGroupBox("Loop %d : " % (varI+1)))

		actionDropdown.imgActionDict = self.imgActionDict
		self.personBox[varI].actionBox = actionDropdown(self)
		self.personBox[varI].actionBox.idx = varI

		personLayout = QtGui.QVBoxLayout()
		personLayout.addWidget(self.personBox[varI].actionBox)  

		self.personBox[varI].actionBox.currentIndexChanged['int'].connect(lambda:self.updateLoop(varI))

		self.personBox[varI].setMinimumHeight(100)
		self.personBox[varI].setMaximumHeight(100)
		self.personBox[varI].setLayout(personLayout)

		self.layout().addWidget(self.personBox[varI])

		self.totalPersonCount += 1
		
	def updateLoop(self, personIdx):
		self.parent.change_color()

class actionDropdown(QtGui.QComboBox):
	def __init__(self, parent):
		super(actionDropdown, self).__init__(parent)
		self.parent = parent
		for varJ in self.imgActionDict:
			self.addItem(varJ)
		self.currentIndexChanged['int'].connect(lambda:parent.setFocus())
		self.setFocusPolicy(QtCore.Qt.NoFocus)

	def wheelEvent(self, event):
		pass

class SettingsDialog(QtGui.QDialog):
	def __init__(self, parent):
		super(SettingsDialog, self).__init__(parent)
		self.setWindowTitle("Settings")
		
		self.imgActionDictLabel = QtGui.QLabel('Path to Image Action Dictionary : ')
		self.imgActionDictEdit = QtGui.QLineEdit(self)
		self.imgActionDictEdit.setText(parent.settingsObj.imgActionDictFName)
		
		self.imgActionDictButton = QtGui.QToolButton(self)
		self.imgActionDictButton.setText("...")
		self.imgActionDictButton.clicked.connect( lambda:self.getImgActionFile(parent) )
		
		noteLabel = QtGui.QLabel('\n\nNote : Restart the executable if you change the action dictionary path')
		self.popupLabelerCheckBox = QtGui.QCheckBox("Enable popup labeler after every boundingbox creation")
		
		if parent.settingsObj.popupLabelFlag:
			self.popupLabelerCheckBox.setChecked(1)

		self.label2 = QtGui.QLabel(self)
		self.OKbutton = QtGui.QToolButton(self)
		self.OKbutton.setText('Save')

		layout = QtGui.QGridLayout(self)
		layout.addWidget(self.imgActionDictLabel, 0, 0)
		layout.addWidget(self.imgActionDictEdit, 0, 1)
		layout.addWidget(self.imgActionDictButton, 0, 2)
		layout.addWidget(self.popupLabelerCheckBox, 1, 0, 1, 3)
		layout.addWidget(self.OKbutton, 2, 1, 1, 2)
		layout.addWidget(noteLabel, 4, 0, 1, 3)
		self.OKbutton.clicked.connect(lambda:self.clickSave(parent))
		self.exec_()
		
	def clickSave(self, parent):
		if int(self.popupLabelerCheckBox.isChecked()):
			parent.settingsObj.popupLabelFlag = 1
		else:
			parent.settingsObj.popupLabelFlag = 0
		
		parent.settingsObj.imgActionDictFName = self.imgActionDictEdit.text()
		parent.settingsObj.saveSettings()
		parent.centralWidget().readAllImgActionLabels(parent)
		self.close()
		
	def getImgActionFile(self,parent):
		parent.settingsObj.imgActionDictFName = QtGui.QFileDialog.getOpenFileName(
				self, 'Choose Image Action Dictionary Path', self.imgActionDictEdit.text())
		self.imgActionDictEdit.setText(parent.settingsObj.imgActionDictFName)

class popupActionLabeler(QtGui.QDialog):
	def __init__(self, parent):
		super (popupActionLabeler, self).__init__(parent)
		self.parent = parent
		self.setWindowTitle("Popup Labeler")
		Menu = ("Available classes : \n\n"
				"Key\t\tAction Labels\n"
				"===\t\t============\n"
				)
		countAction = 0
		for (varI,action) in enumerate(parent.imgActionDict):
			countAction += 1
			Menu += ("  %d\t\t%s\n")%(varI, action)
		Menu += ("\nEnter any key from the above list ( 0 - %d ):\n"%(countAction-1))
		
		label1 = QtGui.QLabel(Menu)
		self.keyIpEdit = QtGui.QLineEdit(self)
		self.keyIpEdit.setValidator(QtGui.QIntValidator(0,countAction-1))
		self.keyIpEdit.returnPressed.connect(self.close)
				
		layout = QtGui.QGridLayout(self)
		layout.addWidget(label1, 0, 0)
		layout.addWidget(self.keyIpEdit, 1, 0)
		
	def keyPressEvent(self,event):
		super (popupActionLabeler, self).keyPressEvent(event)
		if event.key() == QtCore.Qt.Key_Escape:
			self.close()
		
	def close(self):
		super (popupActionLabeler, self).close()
		
		if self.keyIpEdit.text() == "":
			self.keyIpEdit.setText("0")
		self.parent.scrollWidget.actionSelect(self.personIdx, int(self.keyIpEdit.text()))
		
	def popup(self, personIdx):
		self.personIdx = personIdx
		self.keyIpEdit.setText("0")
		self.keyIpEdit.selectAll()
		self.exec_()

if __name__ == '__main__':

	import sys
	app = QtGui.QApplication(sys.argv)
	screenWidth =  app.desktop().screenGeometry().width()
	screenHeight =  app.desktop().screenGeometry().height()
	window = Window()
	window.setGeometry(200, 200, screenWidth*0.7, screenHeight*0.7)
	window.show()
	
	sys.exit(app.exec_())