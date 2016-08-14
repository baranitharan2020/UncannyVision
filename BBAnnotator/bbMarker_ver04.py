from PyQt4 import QtCore, QtGui
import os

class labelWidget(QtGui.QWidget):
	personBox = []
	imgActionDict = None
	def __init__(self, parent):
		super(labelWidget, self).__init__(parent)
		self.parent = parent
		self.scrollLayout = QtGui.QFormLayout()
		self.setLayout(self.scrollLayout)
		self.totalPersonCount = 0
		self.lastAction = 0

	def actionSelect(self, personIdx, selectIdx):
		self.personBox[personIdx].actionBox.setCurrentIndex(selectIdx)

	def removePersonDetails(self):
		self.personBox[-1].setParent(None)
		del self.personBox[-1]
		self.totalPersonCount -= 1
		self.update()
		self.layout().update()

	def addPersonDetails(self):
		varI = self.totalPersonCount 
		self.personBox.append( QtGui.QGroupBox("BB %d : " % (varI+1)) )
		actionDropdown.imgActionDict = self.imgActionDict
		self.personBox[varI].actionBox = actionDropdown(self)
		self.personBox[varI].actionBox.idx = varI
		personLayout = QtGui.QVBoxLayout()
		personLayout.addWidget(self.personBox[varI].actionBox)
		self.personBox[varI].actionBox.currentIndexChanged['int'].connect(lambda:self.updateBB(varI))
		self.personBox[varI].setMinimumHeight(100)
		self.personBox[varI].setMaximumHeight(100)
		self.personBox[varI].setLayout(personLayout)
		self.layout().addWidget(self.personBox[varI])
		self.totalPersonCount += 1

	def updateBB(self, personIdx): 
		action = ' '
		if self.personBox[personIdx].actionBox.currentIndex():
			self.parent.viewer.globalItem[personIdx].setPen (QtGui.QPen(QtCore.Qt.green, 1))
			action = self.personBox[personIdx].actionBox.itemText(self.personBox[personIdx].actionBox.currentIndex())
		else:
			self.parent.viewer.globalItem[personIdx].setPen (QtGui.QPen(QtCore.Qt.red, 1))

		newfont = QtGui.QFont()
		fm = QtGui.QFontMetrics(newfont)
		factor = self.parent.viewer.globalItem[personIdx].rect().width() / fm.width(action)
		newfont.setPointSizeF(newfont.pointSizeF()*factor)

		self.parent.viewer._scene.removeItem(self.parent.viewer.bbActionLabel[personIdx])
		self.parent.viewer.bbActionLabel[personIdx] = self.parent.viewer._scene.addSimpleText('%s'%action)
		self.parent.viewer.bbActionLabel[personIdx].setPen(QtCore.Qt.white)
		self.parent.viewer.bbActionLabel[personIdx].setBrush(QtCore.Qt.blue)

		self.parent.viewer.bbActionLabel[personIdx].setFont(newfont)
		self.parent.viewer.bbActionLabel[personIdx].setPos(QtCore.QPointF(self.parent.viewer.globalItem[personIdx].rect().x(), self.parent.viewer.globalItem[personIdx].rect().y()+(self.parent.viewer.globalItem[personIdx].rect().height()/2)))
		'''
		if self.lastAction and self.personBox[personIdx].actionBox.currentIndex() == self.lastAction:
			self.parent.undo()
			QtGui.QMessageBox.information(self, 'INFO', "End not marked!", QtGui.QMessageBox.Ok)
		else:
			self.lastAction = self.personBox[personIdx].actionBox.currentIndex()
		'''

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

	def mousePressEvent(self, event):
		super(actionDropdown, self).mousePressEvent(event)
		self.parent.parent.viewer.globalItem[self.idx].setPen(QtGui.QPen(QtCore.Qt.yellow, 2))

class PhotoViewer(QtGui.QGraphicsView):
	globalItem = []
	globalBoundingBox = []
	lineItem = []
	bbLabel = []
	bbActionLabel = []

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
		self.bbStart=0

	def mousePressEvent(self, event):
		super (PhotoViewer, self).mousePressEvent(event)
		if self.boolSetPath:
			self.bbStart += 1
			self.bbStart %= 2
			position = self.mapToScene(event.pos())	#QtCore.QPointF(event.pos()) - item.rectF.center()
			if self.bbStart:
				item2 = QtGui.QGraphicsRectItem()
				item2.setRect(position.x() , position.y(), 1,1)
				item2.setPen (QtGui.QPen(QtCore.Qt.yellow, 2));
				self._scene.addItem(item2)
				self.globalItem.append(item2)
			else:
				wh = position - QtCore.QPointF(self.globalItem[-1].rect().x() , self.globalItem[-1].rect().y())
				self.globalItem[-1].setRect(self.globalItem[-1].rect().x(), self.globalItem[-1].rect().y(), wh.x(), wh.y())
				if self.globalItem[-1].rect().width()<0:
					self.globalItem[-1].setRect(self.globalItem[-1].rect().x()+self.globalItem[-1].rect().width() , self.globalItem[-1].rect().y(), -self.globalItem[-1].rect().width(), self.globalItem[-1].rect().height())
				if self.globalItem[-1].rect().height()<0:
					self.globalItem[-1].setRect(self.globalItem[-1].rect().x(), self.globalItem[-1].rect().y()+self.globalItem[-1].rect().height(), self.globalItem[-1].rect().width(), -self.globalItem[-1].rect().height())
				self.globalBoundingBox.append([self.globalItem[-1].rect().x(), self.globalItem[-1].rect().y(), self.globalItem[-1].rect().width(), self.globalItem[-1].rect().height()])
				self.bbLabel.append(self._scene.addSimpleText('BB %d' % len(self.globalItem)))
				self.bbLabel[-1].setBrush(QtCore.Qt.red)
				self.bbLabel[-1].setPen(QtCore.Qt.white)
				self.bbLabel[-1].setPos(self.globalItem[-1].rect().x(), self.globalItem[-1].rect().y())
				self.scrollWidget.addPersonDetails()

				self.bbActionLabel.append(self._scene.addSimpleText(' '))
				if executableSettings().popupLabelFlag:
					self.centralWidget.dynamicActionLabeler.popup(self.scrollWidget.totalPersonCount-1)
				else:
					self.globalItem[-1].setPen (QtGui.QPen(QtCore.Qt.red, 1))
		else:
			QtGui.QMessageBox.information(self, 'INFO', "Enter the image and annotation paths to mark the joints!", QtGui.QMessageBox.Ok)

	def mouseMoveEvent(self,event):
		super (PhotoViewer, self).mouseMoveEvent(event)
		for varI in range( len(self.lineItem) ):
			self._scene.removeItem(self.lineItem[0])
			del self.lineItem[0]
		if self.boolSetPath:
			position = self.mapToScene(event.pos()) #QtCore.QPointF(event.pos()) - item.rectF.center()
			if self.bbStart: 
				wh = position - QtCore.QPointF(self.globalItem[-1].rect().x() , self.globalItem[-1].rect().y())
				self.globalItem[-1].setRect(self.globalItem[-1].rect().x() , self.globalItem[-1].rect().y(), wh.x(), wh.y())
			else:
				self.lineItem.append( QtGui.QGraphicsLineItem( QtCore.QLineF( QtCore.QPointF(position.x(),0), QtCore.QPointF(position.x(),self._photo.pixmap().rect().height()) )))
				self.lineItem[0].setPen(QtGui.QPen(QtCore.Qt.cyan, 0.5, QtCore.Qt.DashLine))
				self._scene.addItem(self.lineItem[0])
				self.lineItem.append( QtGui.QGraphicsLineItem( QtCore.QLineF( QtCore.QPointF(0,position.y()), QtCore.QPointF(self._photo.pixmap().rect().width(),position.y()) )))
				self.lineItem[-1].setPen(QtGui.QPen(QtCore.Qt.cyan, 0.5, QtCore.Qt.DashLine))
				self._scene.addItem(self.lineItem[-1])
			self._scene.update()

	def fitInView(self):
		rect = QtCore.QRectF(self._photo.pixmap().rect())
		if not rect.isNull():
			viewrect = self.viewport().rect()
			scenerect = self.transform().mapRect(rect)
						 #viewrect.height() / scenerect.height())
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
	def __init__(self, parent):
		super(CentralWidget, self).__init__(parent)
		self.start = 1
		self.viewer = PhotoViewer(self)
		self.imageNamePrint = QtGui.QLabel(self)

		self.edit = QtGui.QLineEdit(self)
		self.edit.setReadOnly(True)
		self.button = QtGui.QToolButton(self)
		self.button.setText('&Image path')
		self.button.clicked.connect(self.imageOpen)

		self.edit2 = QtGui.QLineEdit(self)
		self.edit2.setReadOnly(True)
		self.button2 = QtGui.QToolButton(self)
		self.button2.setText('&Annotation path')
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

		self.scrollArea = QtGui.QScrollArea()
		self.scrollArea.setWidgetResizable(True)
		self.scrollArea.setWidget(self.scrollWidget)
		self.scrollArea.setMaximumWidth(250)

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

		self.setLayout(self.mainLayout)

	def readAnnotation(self):
		f = open(self.annotationPath+self.annotationName,'r')
		personCount = 0
		for line in f:
			if line == 'Person:\n':
				for person in f:
					if person == '{\n':
						pass
					elif person == '}\n':
						break
					else:
						if person == '\tBoundingBox:\n':
							for bbs in f:
								if bbs == '\t{\n':
									pass
								elif bbs == '\t}\n':
									break
								else:
									splits = bbs.split(',')
									self.viewer.globalBoundingBox.append([float(splits[0]), float(splits[1]), float(splits[2]), float(splits[3])])

									if self.viewer.globalBoundingBox[-1][2]<0:
										self.viewer.globalBoundingBox[-1][0] += self.viewer.globalBoundingBox[-1][2]
										self.viewer.globalBoundingBox[-1][2] = -self.viewer.globalBoundingBox[-1][2]

									if self.viewer.globalBoundingBox[-1][3]<0:
										self.viewer.globalBoundingBox[-1][1] += self.viewer.globalBoundingBox[-1][3]
										self.viewer.globalBoundingBox[-1][3] = -self.viewer.globalBoundingBox[-1][3]
									item2 = QtGui.QGraphicsRectItem()
									item2.setRect(self.viewer.globalBoundingBox[-1][0], self.viewer.globalBoundingBox[-1][1], self.viewer.globalBoundingBox[-1][2], self.viewer.globalBoundingBox[-1][3])
									item2.setPen (QtGui.QPen(QtCore.Qt.red, 1))
									self.viewer.globalItem.append(item2)
									self.viewer.bbLabel.append(self.viewer._scene.addSimpleText('BB %d' % len(self.viewer.globalItem)))
									self.viewer.bbLabel[-1].setBrush(QtCore.Qt.red)
									self.viewer.bbLabel[-1].setPen(QtCore.Qt.white)
									self.viewer.bbLabel[-1].setPos(QtCore.QPointF(item2.rect().x(), item2.rect().y()))

									self.viewer.bbActionLabel.append(self.viewer._scene.addSimpleText(''))
									self.viewer.bbActionLabel[-1].setPos(QtCore.QPointF(item2.rect().x(), item2.rect().y()))

									self.scrollWidget.addPersonDetails()
									self.viewer._scene.addItem(item2)
									personCount += 1
						if person == '\tVideoAction:\n':
							for bbs in f:
								if bbs == '\t{\n':
									pass
								elif bbs == '\t}\n':
									break
								else:
									action = bbs.lstrip().rstrip()
									action = action.split(', ')[-1]
									if action not in self.imgActionDict:
										print 'Exiting as action not present in the dictionary'
										QtGui.QMessageBox.information(self, 'ERROR', "Exiting as action \"%s\"not present in the dictionary!"%action, QtGui.QMessageBox.Ok)
										sys.exit()
									actionId = self.imgActionDict.index(action)
									self.scrollWidget.actionSelect(personCount-1, actionId)
									self.viewer.globalItem[-1].setPen (QtGui.QPen(QtCore.Qt.green, 1));

									newfont = QtGui.QFont()
									fm = QtGui.QFontMetrics(newfont)
									factor = item2.rect().width() / fm.width(action);
									newfont.setPointSizeF(newfont.pointSizeF()*factor);

									self.viewer._scene.removeItem(self.viewer.bbActionLabel[-1])
									self.viewer.bbActionLabel[-1] = self.viewer._scene.addSimpleText('%s'%action)
									self.viewer.bbActionLabel[-1].setPen(QtCore.Qt.white)
									self.viewer.bbActionLabel[-1].setBrush(QtCore.Qt.blue)

									self.viewer.bbActionLabel[-1].setFont(newfont)
									self.viewer.bbActionLabel[-1].setPos(QtCore.QPointF(item2.rect().x(), item2.rect().y()+(item2.rect().height()/2)))
		f.close()

	def saveAnnotation(self):
		if len(self.viewer.globalBoundingBox) or os.path.isfile(self.annotationPath+self.annotationName):
			f = open(self.annotationPath+self.annotationName,'w')
			for varJ in range(len(self.viewer.globalBoundingBox)):
				
				f.write("Person:\n")
				f.write("{\n")

				f.write("\tBoundingBox:\n")
				f.write("\t{\n")
				f.write("\t\t%f,%f,%f,%f\n"%(self.viewer.globalBoundingBox[varJ][0], self.viewer.globalBoundingBox[varJ][1], self.viewer.globalBoundingBox[varJ][2], self.viewer.globalBoundingBox[varJ][3]))
				f.write("\t}\n")

				f.write("\tVideoAction:\n")
				f.write("\t{\n")
				if self.scrollWidget.personBox[varJ].actionBox.currentIndex():
					f.write('\t\t' + self.imageNames[self.imgCount-1] + ', ' + str(varJ+1) + ', ' + "%s\n"%self.scrollWidget.personBox[varJ].actionBox.itemText(self.scrollWidget.personBox[varJ].actionBox.currentIndex()))
					#f.write("\t\t%s\n"%self.scrollWidget.personBox[varJ].actionBox.itemText(self.scrollWidget.personBox[varJ].actionBox.currentIndex()))
				f.write("\t}\n")

				f.write("}\n")
			f.close() 

	def clearAnnotation(self):
		for varI in xrange(len(self.viewer.globalItem),0,-1):
			self.viewer._scene.removeItem(self.viewer.globalItem[varI-1])
			self.viewer._scene.removeItem(self.viewer.bbLabel[-1])
			self.viewer._scene.removeItem(self.viewer.bbActionLabel[-1])
			self.scrollWidget.removePersonDetails()
			del self.viewer.globalItem[varI-1]
			del self.viewer.globalBoundingBox[varI-1]
			del self.viewer.bbLabel[varI-1]
			del self.viewer.bbActionLabel[varI-1]

	def checkBBCompletion(self):
		if self.viewer.bbStart:
			QtGui.QMessageBox.critical(self, 'Set the width and height too!', "The bounding box is not correctly selected!", QtGui.QMessageBox.Ok)
			return 0
		return 1

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

	def undo(self):
		if len(self.viewer.globalItem) > 0:
			self.viewer._scene.removeItem(self.viewer.globalItem[-1])
			del self.viewer.globalItem[-1]
			if self.viewer.bbStart:
				self.viewer.bbStart = 0
			else:
				self.viewer._scene.removeItem(self.viewer.bbLabel[-1])
				self.viewer._scene.removeItem(self.viewer.bbActionLabel[-1])
				del self.viewer.globalBoundingBox[-1]
				del self.viewer.bbLabel[-1]
				del self.viewer.bbActionLabel[-1]
				self.scrollWidget.removePersonDetails()

	mysignal = QtCore.pyqtSignal(int, name='mysignal')
	def keyPressEvent(self, event):
		super (CentralWidget, self).keyPressEvent(event)
		if self.viewer.boolSetPath:
			if event.key() == QtCore.Qt.Key_U:	# undo last label
				self.undo()

			elif event.key() == QtCore.Qt.Key_C and self.checkBBCompletion():	# clear all labels in the image
				self.clearAnnotation()			   
			elif event.key() == QtCore.Qt.Key_N and self.checkBBCompletion():	# goto next image
				self.saveAnnotation()  
				self.clearAnnotation()
				if self.imgCount == len(self.imageNames):
					self.hide()
					event.ignore()
					sys.exit()
				else:
					self.imageAnnotation(self.imgCount)		  
			elif event.key() == QtCore.Qt.Key_P and self.checkBBCompletion():	# goto previous image
				self.saveAnnotation()  
				if self.imgCount-1:
					self.clearAnnotation()
					self.imageAnnotation(self.imgCount-2)
			elif event.key() == QtCore.Qt.Key_J:
				if not self.viewer.boolSetPath:
					QtGui.QMessageBox.information(self, 'INFO', "Enter the image and annotation paths to mark the joints!", QtGui.QMessageBox.Ok)
				else:
					self.mysignal.emit((len(self.imageNames)))
					if self.dialog.edit.text():
						idxVal = int(self.dialog.edit.text())
					else:
						idxVal = 0
					if idxVal and self.checkBBCompletion():
						self.saveAnnotation()  
						self.clearAnnotation()
						self.imgCount = idxVal - 1
						self.imageAnnotation(self.imgCount)  
			elif event.key() == QtCore.Qt.Key_Q and self.checkBBCompletion():	  # quit
				self.saveAnnotation()  
				self.clearAnnotation()
				self.hide()
				event.ignore()
				sys.exit()	#exit(app.exec_())	#anoopkp: fix this 
		else:
			if event.key() == QtCore.Qt.Key_Q:
				sys.exit()	#exit(app.exec_())	#anoopkp: fix this 
		if event.key() == QtCore.Qt.Key_H:
			self.helpWindow()
		if self.imgCount:
			self.imageNamePrint.setText("Viewing image : %s\t\t(%d/%d)"%(self.imageNames[self.imgCount-1], self.imgCount, len(self.imageNames)))

	def imageAnnotation(self,callCount):
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
			f.close() # you can omit in most cases as the destructor will call it
		else:
			QtGui.QMessageBox.information(self, 'ERROR', "Action dictionary not found!", QtGui.QMessageBox.Ok)

class Window(QtGui.QMainWindow):
	def __init__(self):
		super(Window, self).__init__()

		self.settingsObj = executableSettings()

		self.statusBar()
		self.statusBar().showMessage("Enter the image path and annotation path")

		quitMenu = QtGui.QAction('&QUIT', self)
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

class executableSettings():
	def __init__(self):
		self.popupLabelFlag = 0
		self.imgActionDictFName = "./actionDict_v04.txt"
		self.readSettings()

	def readSettings(self):  
		settingsFile = os.getcwd()+'/'+'.bbMarker_ver02.settings'

		if os.path.isfile(settingsFile):
			f = open(settingsFile,'r')
			for line in f:
				data = line.rstrip().split()
				if len(data):
					if data[0] == 'popupLabeler':
						self.popupLabelFlag = int(data[1])
					if data[0] == 'actionDict':
						self.imgActionDictFName = data[1]
			f.close()

	def saveSettings(self):
		settingsFile = os.getcwd()+'/'+'.bbMarker_ver02.settings'
		f = open(settingsFile,'w')
		f.write('popupLabeler %d\n' % self.popupLabelFlag)
		f.write('actionDict %s\n' % self.imgActionDictFName)

		f.close()

class popupActionLabeler(QtGui.QDialog):
	def __init__(self, parent):
		super (popupActionLabeler, self).__init__(parent)
							  #QtCore.Qt.WindowSystemMenuHint |
							  #~QtCore.Qt.WindowMaximizeButtonHint)
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

		if int(self.keyIpEdit.text()):
			self.parent.viewer.globalItem[-1].setPen (QtGui.QPen(QtCore.Qt.green, 1))
		else:
			self.parent.viewer.globalItem[-1].setPen (QtGui.QPen(QtCore.Qt.red, 1))

	def popup(self, personIdx):
		self.personIdx = personIdx
		self.keyIpEdit.setText("0")
		self.keyIpEdit.selectAll()
		self.exec_()

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
		self.edit.setValidator(QtGui.QIntValidator(0,self.imgCount))
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