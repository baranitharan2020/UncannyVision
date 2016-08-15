import os
from PyQt4 import QtCore, QtGui

class PhotoViewer(QtGui.QGraphicsView):
	globalItem = []
	globalCircleItem = []
	globalConnectItem = []
	globalLoop = []
	globalJoint = []
	label = []
	
	def __init__(self, parent):
		super(PhotoViewer, self).__init__(parent)
		self.centralWidget = parent
		self.window = parent.window
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
		self._pos = []
		self.joint_ctr = -1
		self.person_ctr = 0

	def mousePressEvent(self, event):
		super (PhotoViewer, self).mousePressEvent(event)
		if self.boolSetPath:
			self.bb = window.bb_checkbox.checkState()
			self.lm = window.lm_checkbox.checkState()
			if self.lm:
				rad = 8
				self.joint_ctr += 1
				pos = self.mapToScene(event.x(), event.y())
				self._pos.append(pos)
				if self.joint_ctr == 0:
					self.loopStart = 1
					self.globalJoint.append([])
					self.person_ctr += 1
				self.globalJoint[-1].append((pos.x(), pos.y()))
				if self.joint_ctr == 3 or self.joint_ctr == 9:
					color = QtGui.QColor(0, 51, 0)
					line_pen = QtGui.QPen(color, 4, QtCore.Qt.DashLine)
				elif self.joint_ctr < 3:
					color = QtGui.QColor(255, 0, 0)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				elif self.joint_ctr < 6:
					color = QtGui.QColor(0, 0, 255)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				elif self.joint_ctr < 9:
					color = QtGui.QColor(0, 255, 0)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				elif self.joint_ctr < 12:
					color = QtGui.QColor(255, 165, 0)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				elif self.joint_ctr < 14:
					color = QtGui.QColor(153, 0, 115)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				if event.button() == QtCore.Qt.LeftButton:
					color = QtGui.QColor(255, 255, 0)
				else:
					color = QtGui.QColor(0, 255, 255)
					self.globalJoint[-1][-1] = (-self.globalJoint[-1][-1][0], -self.globalJoint[-1][-1][1])
				circle_pen = QtGui.QPen(color, 4, QtCore.Qt.SolidLine)

				self.globalCircleItem.append(QtGui.QGraphicsEllipseItem(pos.x(), pos.y(), rad, rad))
				self.globalItem.append(self.globalCircleItem[-1])
				self.globalCircleItem[-1].setPen(circle_pen)
				self._scene.addItem(self.globalItem[-1])
				if self.joint_ctr % 6:
					start = self._pos[-2]
					end = self._pos[-1]
					self.globalConnectItem.append(QtGui.QGraphicsLineItem(QtCore.QLineF(start, end)))
					self.globalConnectItem[-1].setPen(line_pen)
					self.globalItem.append(self.globalConnectItem[-1])
					self._scene.addItem(self.globalItem[-1])
				if self.joint_ctr == 13:
					self._pos = []
					self.joint_ctr = -1
					#add action
					self.scrollWidget.addPersonDetails()
					self.label.append(self._scene.addSimpleText('Person %d' % self.person_ctr))
					self.label[-1].setBrush(QtCore.Qt.red)
					self.label[-1].setPen(QtCore.Qt.white)
					self.label[-1].setPos(pos.x(), pos.y() - 25)
			elif self.bb:
				pass
		else:
			QtGui.QMessageBox.information(self, 'INFO', "Enter the image and annotation paths to mark the joints!", QtGui.QMessageBox.Ok)

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
		self.window = parent
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
		f = open(self.annotationPath+self.annotationName,'r')
		personCount = 0
		self.viewer.globalJoint = []
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
									pass	#implement
						if person == '\tJoints:\n':
							for joint in f:
								if joint == '\t{\n':
									pass
								elif joint == '\t}\n':
									break
								else:
									self.viewer.globalJoint.append(eval(joint))
						if person == '\tImageAction:\n':
							for ia in f:
								if ia == '\t{\n':
									pass
								elif ia == '\t}\n':
									break
								else:
									action = ia.lstrip().rstrip()
									self.scrollWidget.addPersonDetails()
									if action == 'None':
										actionId = 0
									else:
										actionId = self.imgActionDict.index(action)
									self.scrollWidget.actionSelect(self.viewer.person_ctr-1, actionId)

		#marking the joints
		self.viewer.joint_ctr = -1
		rad = 8
		
		for person in self.viewer.globalJoint:
			for i in person:
				self.viewer.joint_ctr += 1
				#pos = self.viewer.mapToScene(i[0], i[1])
				if self.viewer.joint_ctr == 0:
					self.viewer.person_ctr += 1
				if self.viewer.joint_ctr == 3 or self.viewer.joint_ctr == 9:
					color = QtGui.QColor(0, 51, 0)
					line_pen = QtGui.QPen(color, 4, QtCore.Qt.DashLine)
				elif self.viewer.joint_ctr < 3:
					color = QtGui.QColor(255, 0, 0)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				elif self.viewer.joint_ctr < 6:
					color = QtGui.QColor(0, 0, 255)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				elif self.viewer.joint_ctr < 9:
					color = QtGui.QColor(0, 255, 0)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				elif self.viewer.joint_ctr < 12:
					color = QtGui.QColor(255, 165, 0)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				elif self.viewer.joint_ctr < 14:
					color = QtGui.QColor(153, 0, 115)
					line_pen = QtGui.QPen(color, 5, QtCore.Qt.SolidLine)
				if i[0] < 0:
					color = QtGui.QColor(0, 255, 255)
					i = (-i[0], -i[1])
				else:
					color = QtGui.QColor(255, 255, 0)
				circle_pen = QtGui.QPen(color, 4, QtCore.Qt.SolidLine)
				
				pos = QtCore.QPoint(i[0], i[1])
				self.viewer._pos.append(pos)

				self.viewer.globalCircleItem.append(QtGui.QGraphicsEllipseItem(pos.x(), pos.y(), rad, rad))
				self.viewer.globalItem.append(self.viewer.globalCircleItem[-1])
				self.viewer.globalCircleItem[-1].setPen(circle_pen)
				self.viewer._scene.addItem(self.viewer.globalCircleItem[-1])
				if self.viewer.joint_ctr % 6:
					start = self.viewer._pos[-2]
					end = self.viewer._pos[-1]
					self.viewer.globalConnectItem.append(QtGui.QGraphicsLineItem(QtCore.QLineF(start, end)))
					self.viewer.globalConnectItem[-1].setPen(line_pen)
					self.viewer.globalItem.append(self.viewer.globalConnectItem[-1])
					self.viewer._scene.addItem(self.viewer.globalConnectItem[-1])
				if self.viewer.joint_ctr == 13:
					self.viewer._pos = []
					self.viewer.joint_ctr = -1
					self.viewer.label.append(self.viewer._scene.addSimpleText('Person %d' % self.viewer.person_ctr))
					self.viewer.label[-1].setBrush(QtCore.Qt.red)
					self.viewer.label[-1].setPen(QtCore.Qt.white)
					self.viewer.label[-1].setPos(pos.x(), pos.y() - 25)

	def saveAnnotation(self):
		if self.viewer.person_ctr or os.path.isfile(self.annotationPath+self.annotationName):
			f = open(self.annotationPath + self.annotationName, 'w+')
			for person in xrange(self.viewer.person_ctr):
				f.write("Person:\n")
				f.write("{\n")

				f.write("\tBoundingBox:\n")
				f.write("\t{\n")
				#f.write("\t\t%f,%f,%f,%f\n"%(self.viewer.globalBoundingBox[varJ][0], self.viewer.globalBoundingBox[varJ][1], self.viewer.globalBoundingBox[varJ][2], self.viewer.globalBoundingBox[varJ][3]))
				f.write("\t}\n")

				f.write("\tJoints:\n")
				f.write("\t{\n")
				f.write("\t\t")
				f.write("[")
				for i in xrange(13):
					f.write("(%d, %d), " %(self.viewer.globalJoint[person][i][0], self.viewer.globalJoint[person][i][1]))
				f.write("(%d, %d)]\n" %(self.viewer.globalJoint[person][13][0], self.viewer.globalJoint[person][13][1]))
				f.write("\t}\n")				

				f.write("\tImageAction:\n")
				f.write("\t{\n")
				if self.scrollWidget.personBox[person].actionBox.currentIndex():
					f.write("\t\t%s\n"%self.scrollWidget.personBox[person].actionBox.itemText(self.scrollWidget.personBox[person].actionBox.currentIndex()))
				else:
					f.write('\t\tNone\n')
				f.write("\t}\n")

				f.write("}\n")
			f.close()
		
	def clearAnnotation(self):
		for varI in xrange(len(self.viewer.globalItem)):
			self.viewer._scene.removeItem(self.viewer.globalItem[varI])
		for varI in xrange(self.viewer.person_ctr):
			self.viewer._scene.removeItem(self.viewer.label[varI])
		for varI in xrange(len(self.scrollWidget.personBox)):
			self.scrollWidget.removePersonDetails()
		self.viewer.globalLoop = []
		self.viewer.globalItem = []
		self.viewer.globalCircleItem = []
		self.viewer.globalConnectItem = []
		self.viewer.globalJoint = []
		self.viewer.label = []
		self.viewer.person_ctr = 0

	def checkJointCompletion(self):
		if self.viewer.joint_ctr >= 0 and self.viewer.joint_ctr < 14:
			QtGui.QMessageBox.critical(self, 'Incomplete joints!', 'Not enough joints.', QtGui.QMessageBox.Ok)
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
					" H \tTo go to help menu\n"
					"\n"
					"How to use:\n"
					"Start annotating (by clicking) in a left to right direction, starting with legs, then hands, neck and finally the face.\n"
					"Right click to annotate hidden joints.\n")
		QtGui.QMessageBox.information(self, 'Help Menu', helpMenu, QtGui.QMessageBox.Ok)
		
	mysignal = QtCore.pyqtSignal(int, name='mysignal')
	def keyPressEvent(self, event):
		super (CentralWidget, self).keyPressEvent(event)
		
		if self.viewer.boolSetPath:
			if event.key() == QtCore.Qt.Key_U:	# undo last label
				if self.viewer.globalItem:
					if not len(self.viewer._pos):
						self.viewer._pos = [QtCore.QPoint(i[0], i[1]) for i in self.viewer.globalJoint[-1]]
						self.viewer.joint_ctr = 13
						self.scrollWidget.removePersonDetails()
						self.viewer._scene.removeItem(self.viewer.label.pop())
					if self.viewer.joint_ctr % 6:
						self.viewer._scene.removeItem(self.viewer.globalItem[-1])
						self.viewer.globalItem.pop()
						self.viewer.globalConnectItem.pop()
					self.viewer._scene.removeItem(self.viewer.globalItem[-1])
					self.viewer.globalItem.pop()
					self.viewer.globalCircleItem.pop()
					self.viewer._pos.pop()
					self.viewer.globalJoint[-1].pop()
					self.viewer.joint_ctr -= 1
					if not len(self.viewer.globalJoint[-1]):
						self.viewer.globalJoint.pop()
						self.viewer.person_ctr -= 1
			elif event.key() == QtCore.Qt.Key_C and self.checkJointCompletion():	#clear all labels in the image
				self.clearAnnotation()
			elif event.key() == QtCore.Qt.Key_N and self.checkJointCompletion():	#goto next image
				self.saveAnnotation()
				self.clearAnnotation()
				if self.imgCount == len(self.imageNames):
					self.hide()
					event.ignore()
					sys.exit()
				else:
					self.imageAnnotation(self.imgCount)
			elif event.key() == QtCore.Qt.Key_P and self.checkJointCompletion():	# goto previous image
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
					if idxVal and self.checkJointCompletion():
						self.saveAnnotation()
						self.clearAnnotation()
						self.imgCount = idxVal - 1
						self.imageAnnotation(self.imgCount)
			elif event.key() == QtCore.Qt.Key_Q and self.checkJointCompletion():	# quit
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
		self.label1.setText('Total number of images is : %d' % self.imgCount)
		self.label2.setText('Skip to (0 - %d) :' % self.imgCount)
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
		pass

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
			Menu += ("%d\t\t%s\n")%(varI, action)
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

class SettingsDialog(QtGui.QDialog):
	def __init__(self, parent):
		super(SettingsDialog, self).__init__(parent)
		self.setWindowTitle("Settings")

		self.window = parent
		
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

		self.window.bb_checkbox.setEnabled(False)

		layout = QtGui.QGridLayout(self)
		layout.addWidget(self.imgActionDictLabel, 0, 0)
		layout.addWidget(self.imgActionDictEdit, 0, 1)
		layout.addWidget(self.imgActionDictButton, 0, 2)
		layout.addWidget(self.popupLabelerCheckBox, 1, 0, 1, 3)
		layout.addWidget(self.window.bb_checkbox, 2, 0, 1, 3)
		layout.addWidget(self.window.lm_checkbox, 3, 0, 1, 3)
		layout.addWidget(self.OKbutton, 4, 3, 1, 2)
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
		f = open('settings.txt', 'w')
		if f and self.window.lm_checkbox.checkState():
			f.write('lm')
		else:
			f.write('bb')
		f.close()
		self.close()
		
	def getImgActionFile(self,parent):
		parent.settingsObj.imgActionDictFName = QtGui.QFileDialog.getOpenFileName(
				self, 'Choose Image Action Dictionary Path', self.imgActionDictEdit.text())
		self.imgActionDictEdit.setText(parent.settingsObj.imgActionDictFName)

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
		
		self.check = 'lulz'

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

		self.bb_checkbox = QtGui.QCheckBox("Enable Bounding Boxes")
		self.lm_checkbox = QtGui.QCheckBox("Enable Joints")

		try:
			f = open('settings.txt', 'r')
			settings = f.read()
			f.close()
		except:
			settings = None
		if settings == 'bb':
			self.bb_checkbox.setCheckState(2)
			self.lm_checkbox.setCheckState(0)
		else:
			self.lm_checkbox.setCheckState(2)
			self.bb_checkbox.setCheckState(0)

if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)
	screenWidth = app.desktop().screenGeometry().width()
	screenHeight = app.desktop().screenGeometry().height()
	window = Window()
	window.setGeometry(200, 200, screenWidth*0.7, screenHeight*0.7)
	window.show()
	
	sys.exit(app.exec_())