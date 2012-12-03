#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
import math
from PySide import QtGui, QtCore
import time


### Wishes:

# Disable sources
#  
class PhaseDial(QtGui.QDial):
	def __init__(self):
		super(PhaseDial, self).__init__()
	def sizeHint(self):
		return QtCore.QSize(50,50)


class slitItem(QtGui.QGraphicsRectItem):
	def __init__(self,index,mainWindow,x,y,w,h):
		super(slitItem, self).__init__(0,0,w,h,None)
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
		self.index = index
		self.mainWindow = mainWindow
		self.setPos(x,y)
		self.min_y = np.linspace(0,mainWindow.sceneHeight-1,mainWindow.nrSources+1)[index]
		self.max_y = np.linspace(0,mainWindow.sceneHeight-1,mainWindow.nrSources+1)[index+1]-mainWindow.slitSize[index]

	def mouseMoveEvent(self, event):
		delta_y = event.scenePos().y()-event.lastScenePos().y()
		if(self.scenePos().y() + delta_y > self.max_y):
			self.setY(self.max_y)
		elif(self.scenePos().y() + delta_y < self.min_y):
			self.setY(self.min_y)
		else:
			self.moveBy(0,delta_y)
	def mouseReleaseEvent(self, event):
		self.mainWindow.toolpanel.selectedSourceSpin.setValue(self.index+1)
		self.mainWindow.toolpanel.positionSpin.setValue(self.y()+self.mainWindow.slitSize[self.index]/2.0)



class pointSourceItem(QtGui.QGraphicsEllipseItem):
	def __init__(self,index,mainWindow,x,y,w,h):
		super(pointSourceItem, self).__init__(0,0,w,h,None)
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
		self.index = index
		self.mainWindow = mainWindow
		self.setPos(x,y)
		self.min_y = 0
		self.max_y = mainWindow.sceneHeight-1
		self.min_x = mainWindow.baseX-self.mainWindow.pointSize/2
		self.max_x = mainWindow.nearSceneWidth/3-1
	def mouseMoveEvent(self, event):
		delta_y = event.scenePos().y()-event.lastScenePos().y()
		if(self.scenePos().y() + delta_y > self.max_y):
			self.setY(self.max_y)
		elif(self.scenePos().y() + delta_y < self.min_y):
			self.setY(self.min_y)
		else:
			self.moveBy(0,delta_y)		
		delta_x = event.scenePos().x()-event.lastScenePos().x()
		if(self.scenePos().x() + delta_x > self.max_x):
			self.setX(self.max_x)
		elif(self.scenePos().x() + delta_x < self.min_x):
			self.setX(self.min_x)
		else:
			self.moveBy(delta_x,0)
	def mouseReleaseEvent(self, event):
		self.mainWindow.toolpanel.selectedSourceSpin.setValue(self.index+1)
		self.mainWindow.toolpanel.positionSpin.setValue(self.y()+self.mainWindow.pointSize/2)
		self.mainWindow.toolpanel.positionXSpin.setValue(self.x()+self.mainWindow.pointSize/2)

class pointSelector(QtGui.QGraphicsEllipseItem):
	def __init__(self,mainWindow):
		super(pointSelector, self).__init__(-mainWindow.pointSize/2.0,-mainWindow.pointSize/2.0,mainWindow.pointSize,mainWindow.pointSize)
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
		self.setBrush(QtGui.QBrush(QtGui.QColor("#cc0000")))
		self.setPen(QtGui.QPen(QtGui.QColor(255,0,0,0),20))
		self.setFlag(QtGui.QGraphicsItem.ItemIsMovable)
		self.setPos(mainWindow.nearSceneWidth/2.0,mainWindow.sceneHeight/2.0)
		self.setZValue(100)
		self.mainWindow = mainWindow
		self.min_y = 0
		self.max_y = mainWindow.sceneHeight-1
		self.min_x = mainWindow.baseX
		self.max_x = mainWindow.nearSceneWidth-1
		self.xLine = QtGui.QGraphicsLineItem(-mainWindow.nearSceneWidth,0,mainWindow.nearSceneWidth,0,self)
		self.xLine.setPen(QtGui.QPen(QtGui.QColor("#3465a4"),2,QtCore.Qt.DashLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
		self.xLine.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent)
		self.yLine = QtGui.QGraphicsLineItem(0,-mainWindow.sceneHeight,0,mainWindow.sceneHeight,self)
		self.yLine.setPen(QtGui.QPen(QtGui.QColor("#3465a4"),2,QtCore.Qt.DashLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
		self.yLine.setFlag(QtGui.QGraphicsItem.ItemStacksBehindParent)
	def mouseMoveEvent(self, event):
		delta_y = event.scenePos().y()-event.lastScenePos().y()
		if(self.scenePos().y() + delta_y > self.max_y):
			self.setY(self.max_y)
		elif(self.scenePos().y() + delta_y < self.min_y):
			self.setY(self.min_y)
		else:
			self.moveBy(0,delta_y)		
		delta_x = event.scenePos().x()-event.lastScenePos().x()
		if(self.scenePos().x() + delta_x > self.max_x):
			self.setX(self.max_x)
		elif(self.scenePos().x() + delta_x < self.min_x):
			self.setX(self.min_x)
		else:
			self.moveBy(delta_x,0)
		self.mainWindow.updateField()
	def hideLines(self):
		self.xLine.hide()
		self.yLine.hide()
	def showLines(self):
		self.xLine.show()
		self.yLine.show()

class ArgandHand(QtGui.QGraphicsLineItem):
	def __init__(self,father,farSceneWidth,scale=1):
		super(ArgandHand, self).__init__(father)		
		self.scale = scale
		self.farSceneWidth = farSceneWidth
		self.color = "#3465a4"		
		self.arrowTop = QtGui.QGraphicsLineItem(0,0,-10,-7,self)
		self.arrowBottom = QtGui.QGraphicsLineItem(0,0,-10,+7,self)
		self.originX = 0
		self.originY = 0
		self.draw()
	def draw(self):
		self.setLine(0,0,self.scale*(self.farSceneWidth/2.0-10),0)
		self.setPos(self.farSceneWidth/2.0+self.originX ,self.farSceneWidth/2.0+self.originY)
		self.setPen(QtGui.QPen(QtGui.QColor(self.color),self.scale*2))		
		self.arrowTop.setLine(0,0,self.scale*-10,self.scale*-7)
		self.arrowTop.setPos(self.scale*(self.farSceneWidth/2.0-10),0)
		self.arrowTop.setPen(QtGui.QPen(QtGui.QColor(self.color),self.scale*2,QtCore.Qt.SolidLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))		
		self.arrowBottom.setLine(0,0,self.scale*-10,self.scale*7)
		self.arrowBottom.setPos(self.scale*(self.farSceneWidth/2.0-10),0)
		self.arrowBottom.setPen(QtGui.QPen(QtGui.QColor(self.color),self.scale*2,QtCore.Qt.SolidLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
	def setScale(self,scale):
		self.scale = scale
		self.draw()
	def setColor(self,color):
		self.color = color
		self.draw()
	def setOrigin(self,E):
		self.originX = np.real(E)*(self.farSceneWidth/2.0-10)
		self.originY = np.imag(E)*(self.farSceneWidth/2.0-10)
		self.draw()


class Argand(QtGui.QGraphicsEllipseItem):
	def __init__(self,mainWindow):
		super(Argand, self).__init__(10,10,mainWindow.farSceneWidth-20,mainWindow.farSceneWidth-20)
		farSceneWidth = mainWindow.farSceneWidth
		self.farSceneWidth = farSceneWidth
		self.mainWindow = mainWindow
		self.setPen(QtGui.QColor("#ffffff"))
		self.setPos(0,mainWindow.animationBox.height())
		line = QtGui.QGraphicsLineItem(farSceneWidth/2.0,10,farSceneWidth/2.0,farSceneWidth-10,self)
		line.setPen(QtGui.QPen(QtGui.QColor("#ffffff"),1,QtCore.Qt.DashLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
		line = QtGui.QGraphicsLineItem(10,farSceneWidth/2.0,farSceneWidth-10,farSceneWidth/2.0,self)
		line.setPen(QtGui.QPen(QtGui.QColor("#ffffff"),1,QtCore.Qt.DashLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
		self.sources = []
		self.sumHand = ArgandHand(self,farSceneWidth,1)
		self.sumHand.setColor("#f57900")
		self.sumHand.hide()
		self.sumHand.setZValue(1000)
		self.E = complex(0,0)
	def addSource(self,i,angle):
		if(len(self.sources) <= i):
			self.sources.append(ArgandHand(self,self.farSceneWidth,1.0/self.mainWindow.nrSources))		
		self.sources[i].setScale(1.0/self.mainWindow.nrSources)
		self.sources[i].setRotation(angle)
		self.sources[i].setOrigin(self.E/self.mainWindow.nrSources)
		self.sources[i].show()
		self.E += np.exp(angle/180.0*math.pi*1.0j)
		self.sumHand.setRotation(180.0*np.angle(self.E)/math.pi)
		self.sumHand.setScale(np.abs(self.E)/self.mainWindow.nrSources)
		self.sumHand.show()
	def hideHands(self):
		for h in self.sources:
			h.hide()			
		self.sumHand.hide()		
		self.E = complex(0,0)
	def removeSource(self,i):
		self.sources[i].hide()
		angle = self.sources.pop().rotation()
		self.E -= np.exp(angle/180.0*math.pi*1.0j)		
		if(len(self.sources) > 0):
			self.sumHand.setRotation(180.0*np.angle(self.E)/math.pi)
			self.sumHand.setScale(np.abs(self.E)/self.mainWindow.nrSources)
			self.sumHand.show()
		else:
			self.sumHand.hide()

class MainWindow(QtGui.QMainWindow): 
	def __init__(self):
		super(MainWindow, self).__init__()
		self.sceneHeight = 650
		self.nearSceneWidth = 800
		self.farSceneWidth = 200
		self.pointSize = 6
		self.slitThickness = 6
		self.baseSlitSize = 40
		self.baseX = 10
		self.downSampling = 1
		self.farX = 1e9
		self.animationStep = 0;
		self.initSources()
		self.initField()
		self.initUI() 
		self.toolpanel.nrSourcesSpin.setValue(2)
	def initSources(self):
		self.nrSources = 1
		self.sourcePositions = [self.sceneHeight/2]
		self.sourceX = [self.baseX]
		self.wavelength = 50
		self.globalPhase = 0
		self.slitSize = [self.baseSlitSize]
		self.phaseShift = [0]
		timer = QtCore.QTimer()
		timer.setInterval(20)
		timer.timeout.connect(self.onAnimationTimerTimeout)
		timer.source = 0
		self.sourceTimers = [timer]
	def initField(self):
		self.E = np.zeros((self.sceneHeight/self.downSampling,self.nearSceneWidth/self.downSampling,),complex)
		self.pixmap = QtGui.QPixmap(self.E.shape[1],self.E.shape[0])
		self.Ex,self.Ey = np.meshgrid(np.arange(self.downSampling/2.0,self.E.shape[1]*self.downSampling,self.downSampling),np.arange(self.downSampling/2.0,self.E.shape[0]*self.downSampling,self.downSampling))
		self.pointDX2 = (self.Ex-self.baseX)**2.0
		self.slitDX2 = (self.Ex-self.baseX-self.slitThickness/2.0)**2.0
		self.calculateFieldTimer = QtCore.QTimer()
		self.calculateFieldTimer.setInterval(500)
		self.calculateFieldTimer.setSingleShot(True)
		self.calculateFieldTimer.timeout.connect(self.calculateField)

		self.farE = np.zeros((self.sceneHeight/self.downSampling),complex)
	def initUI(self):		
		hbox = QtGui.QHBoxLayout()
		view = self.initNearView()
#		hbox.addStretch()
		hbox.addWidget(view)
		view = self.initFarView()
		hbox.addWidget(view)
		toolpanel = self.initToolPanel()
		self.toolpanel = toolpanel
		hbox.addWidget(toolpanel)
		hbox.addStretch()
		self.statusBar().showMessage('Ready')       
		self.setWindowTitle('Diffraction Workbench')    
		widget = QtGui.QWidget()
		widget.setLayout(hbox)
		self.setCentralWidget(widget)
		self.drawField()
		self.drawSources()		
		self.simulateTimeTimer = QtCore.QTimer()
		self.simulateTimeTimer.setInterval(25)
		self.simulateTimeTimer.setSingleShot(False)
		self.simulateTimeTimer.timeout.connect(self.timeStep)
		self.show()
	def initNearView(self):
		self.sourceObjects = []
		self.sourceLines = []

		scene = QtGui.QGraphicsScene(0, 0, self.nearSceneWidth, self.sceneHeight);
		graphicsView = QtGui.QGraphicsView(scene)
		graphicsView.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#000000")))
		graphicsView.setSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
		graphicsView.setScene(scene)
		graphicsView.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform);
		self.nearScene = scene
		self.fieldItem = QtGui.QGraphicsPixmapItem()
		scene.addItem(self.fieldItem)
		self.fieldItem.setScale(self.downSampling)
		self.fieldItem.setTransformationMode(QtCore.Qt.SmoothTransformation)

		self.pointSelection = pointSelector(self)
		scene.addItem(self.pointSelection)
		return graphicsView
	def initFarView(self):
		self.plotObjects = []
		scene = QtGui.QGraphicsScene(0, 0, self.farSceneWidth, self.sceneHeight);
		graphicsView = QtGui.QGraphicsView(scene)
		graphicsView.setScene(scene)
		graphicsView.setSizePolicy(QtGui.QSizePolicy.Fixed,QtGui.QSizePolicy.Fixed)
		graphicsView.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#000000")))
		graphicsView.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform);
		self.farScene = scene
		self.farFieldItem = QtGui.QGraphicsPixmapItem()
		scene.addItem(self.farFieldItem)
		self.farFieldPlot = QtGui.QGraphicsPixmapItem()
		scene.addItem(self.farFieldPlot)

		self.farFieldItem.setScale(self.downSampling)
		self.farFieldItem.setTransformationMode(QtCore.Qt.SmoothTransformation)

		self.animationBox = QtGui.QGroupBox("Selected Point");
		self.animationBox.resize(self.farSceneWidth,self.sceneHeight/5)
		self.animationBox.setLayout(QtGui.QVBoxLayout())
		self.animationBoxX = QtGui.QLabel()
		self.animationBox.layout().addWidget(self.animationBoxX)
		self.animationBoxY = QtGui.QLabel()
		self.animationBox.layout().addWidget(self.animationBoxY)
		self.animationBoxE = QtGui.QLabel()
		self.animationBox.layout().addWidget(self.animationBoxE)
		self.animationBox.layout().addSpacing(20)
		self.animationBoxStep =  QtGui.QLabel()
		self.animationBox.layout().addWidget(self.animationBoxStep)
		self.animationSlider = QtGui.QSlider(QtCore.Qt.Horizontal)
		self.animationSlider.setValue(self.animationStep)
		self.animationSlider.valueChanged.connect(self.onAnimationSliderValueChanged)
		self.animationBox.layout().addWidget(self.animationSlider)
		self.proxy = self.farScene.addWidget(self.animationBox);
		self.proxy.hide()
		text = QtGui.QGraphicsTextItem("Source Amplitude")
		text.setFont(QtGui.QFont("Helvetiva",20))
		text.setDefaultTextColor(QtGui.QColor("#3465a4"))
		text.setPos(18,self.animationBox.height()+4)
		self.farScene.addItem(text)
		self.topArgand = Argand(self)
		self.topArgand.hand = ArgandHand(self.topArgand,self.farSceneWidth)
		self.topArgand.setPos(0,self.animationBox.height()+26)
		text = QtGui.QGraphicsTextItem("Total Amplitude")
		text.setFont(QtGui.QFont("Helvetiva",20))
		text.setDefaultTextColor(QtGui.QColor("#f57900"))
		text.setPos(27,self.animationBox.height()+self.farSceneWidth+26)
		self.farScene.addItem(text)

		self.bottomArgand = Argand(self)
		self.bottomArgand.setPos(0,self.animationBox.height()+self.farSceneWidth+48)


		self.farScene.addItem(self.topArgand)
		self.farScene.addItem(self.bottomArgand)
		return graphicsView
	def initToolPanel(self):
		toolpanel = QtGui.QWidget();
		self.toolpanel = toolpanel
		vbox = QtGui.QVBoxLayout()
		vbox.addStretch()
		toolpanel.setLayout(vbox)
		sourceGroup = QtGui.QGroupBox("Source Type")
		sourceGroup.setLayout(QtGui.QVBoxLayout())
		toolpanel.pointsRadio = QtGui.QRadioButton("Points")
		toolpanel.pointsRadio.setChecked(True)
		toolpanel.slitsRadio = QtGui.QRadioButton("Slits")
		toolpanel.slitsRadio.toggled.connect(self.onSlitsRadioToggled)
		sourceGroup.layout().addWidget(toolpanel.pointsRadio)
		sourceGroup.layout().addWidget(toolpanel.slitsRadio)
		vbox.addWidget(sourceGroup)

		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(QtGui.QLabel("Nr. of sources: "))
		toolpanel.nrSourcesSpin = QtGui.QSpinBox()
		toolpanel.nrSourcesSpin.setMinimum(1)
		toolpanel.nrSourcesSpin.setMaximum(5)
		toolpanel.nrSourcesSpin.valueChanged.connect(self.onNrSourcesSpinValueChanged)
		hbox.addWidget(toolpanel.nrSourcesSpin)
		vbox.addLayout(hbox)
		
		positionGroup = QtGui.QGroupBox("Source Properties")
		positionGroup.setLayout(QtGui.QVBoxLayout())
		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(QtGui.QLabel("Selected source: "))
		toolpanel.selectedSourceSpin = QtGui.QSpinBox()
		toolpanel.selectedSourceSpin.setMinimum(1)		
		toolpanel.selectedSourceSpin.setMaximum(self.nrSources)	
		toolpanel.selectedSourceSpin.valueChanged.connect(self.onSelectedSourceSpinValueChanged)	
		hbox.addWidget(toolpanel.selectedSourceSpin)
		positionGroup.layout().addLayout(hbox)

		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(QtGui.QLabel("Y Position: "))
		toolpanel.positionSpin = QtGui.QSpinBox()
		toolpanel.positionSpin.setMaximum(self.sceneHeight)
		toolpanel.positionSpin.setValue(self.sourcePositions[toolpanel.selectedSourceSpin.value()-1])
		toolpanel.positionSpin.valueChanged.connect(self.onPositionSpinValueChanged)	
		hbox.addWidget(toolpanel.positionSpin)

		positionGroup.layout().addLayout(hbox)

		hbox = QtGui.QHBoxLayout()
		toolpanel.positionXLabel = QtGui.QLabel("X Position: ")
		hbox.addWidget(toolpanel.positionXLabel)
		toolpanel.positionXSpin = QtGui.QSpinBox()
		toolpanel.positionXSpin.setMaximum(self.nearSceneWidth/3-1)
		toolpanel.positionXSpin.setMinimum(self.baseX)
		toolpanel.positionXSpin.setValue(self.sourceX[toolpanel.selectedSourceSpin.value()-1])
		toolpanel.positionXSpin.valueChanged.connect(self.onPositionXSpinValueChanged)	
		hbox.addWidget(toolpanel.positionXSpin)

		positionGroup.layout().addLayout(hbox)

		hbox = QtGui.QHBoxLayout()
		toolpanel.phaseShiftLabel = QtGui.QLabel("Phase Shift: ")
		hbox.addWidget(toolpanel.phaseShiftLabel)		
		toolpanel.phaseShiftDial = PhaseDial()
		toolpanel.phaseShiftDial.setWrapping(True)
		toolpanel.phaseShiftDial.setMaximum(359)
		toolpanel.phaseShiftDial.setValue(0)
		toolpanel.phaseShiftDial.valueChanged.connect(self.onPhaseShiftDialValueChanged)
		toolpanel.phaseShiftDisplay = QtGui.QLCDNumber()
		toolpanel.phaseShiftDisplay.setNumDigits(3)
		toolpanel.phaseShiftDial.valueChanged.connect(toolpanel.phaseShiftDisplay.display)
		hbox.addWidget(toolpanel.phaseShiftDial)		
		hbox.addWidget(toolpanel.phaseShiftDisplay)
		positionGroup.layout().addLayout(hbox)

		hbox = QtGui.QHBoxLayout()
		toolpanel.slitSizeLabel = QtGui.QLabel("Slit size: ")
		hbox.addWidget(toolpanel.slitSizeLabel)
		toolpanel.slitSizeSpin = QtGui.QSpinBox()
		toolpanel.slitSizeSpin.setMinimum(1)
		toolpanel.slitSizeSpin.setMaximum(200)
		toolpanel.slitSizeSpin.setValue(self.slitSize[toolpanel.selectedSourceSpin.value()-1])
		toolpanel.slitSizeSpin.setVisible(False)
		toolpanel.slitSizeLabel.setVisible(False)
		toolpanel.slitSizeSpin.valueChanged.connect(self.onSlitSizeSpinValueChanged)	
		hbox.addWidget(toolpanel.slitSizeSpin)
		positionGroup.layout().addLayout(hbox)

		vbox.addWidget(positionGroup)

		beamGroup = QtGui.QGroupBox("Beam Properties")
		beamGroup.setLayout(QtGui.QVBoxLayout())
		hbox = QtGui.QHBoxLayout()
		toolpanel.wavelengthSpin = QtGui.QSpinBox()
		toolpanel.wavelengthSpin.setMinimum(20)
		toolpanel.wavelengthSpin.setMaximum(400)
		toolpanel.wavelengthSpin.setValue(self.wavelength)
		toolpanel.wavelengthSpin.valueChanged.connect(self.onWavelengthSpinValueChanged)
		hbox.addWidget(QtGui.QLabel("Wavelength: "))
		hbox.addWidget(toolpanel.wavelengthSpin)
		beamGroup.layout().addLayout(hbox)

		hbox = QtGui.QHBoxLayout()
		toolpanel.phaseLabel = QtGui.QLabel("Global phase: ")
		hbox.addWidget(toolpanel.phaseLabel)
		toolpanel.phaseDial = PhaseDial()
		toolpanel.phaseDial.setWrapping(True)
		toolpanel.phaseDial.setMaximum(359)
		toolpanel.phaseDial.setValue(self.globalPhase)
		toolpanel.phaseDial.valueChanged.connect(self.onPhaseDialValueChanged)
		toolpanel.phaseDisplay = QtGui.QLCDNumber()
		toolpanel.phaseDisplay.setNumDigits(3)
		toolpanel.phaseDial.valueChanged.connect(toolpanel.phaseDisplay.display)
		hbox.addWidget(toolpanel.phaseDial)
		hbox.addWidget(toolpanel.phaseDisplay)
		beamGroup.layout().addLayout(hbox)

		hbox = QtGui.QHBoxLayout()
		toolpanel.simulateTimeLabel = QtGui.QLabel("Simulate Time: ")
		hbox.addWidget(toolpanel.simulateTimeLabel)		
		toolpanel.simulateTimeCheck = QtGui.QCheckBox()
		toolpanel.simulateTimeCheck.toggled.connect(self.onSimulateTimeCheckToggled)

		hbox.addWidget(toolpanel.simulateTimeCheck)
		beamGroup.layout().addLayout(hbox)

		vbox.addWidget(beamGroup)


		displayGroup = QtGui.QGroupBox("Left Display")
		displayGroup.setLayout(QtGui.QVBoxLayout())

#		displayWhatGroup = QtGui.QGroupBox("Variable")
#		displayWhatGroup.setLayout(QtGui.QVBoxLayout())
		toolpanel.intensitiesRadio = QtGui.QRadioButton("Averaged Intensities")
		toolpanel.intensitiesRadio.toggled.connect(self.onIntensitiesRadioToggled)
		toolpanel.amplitudesRadio = QtGui.QRadioButton("Instantaneous E Field")
		toolpanel.amplitudesRadio.setChecked(True)
		toolpanel.amplitudesRadio.toggled.connect(self.onAmplitudesRadioToggled)
		displayGroup.layout().addWidget(toolpanel.amplitudesRadio)
		displayGroup.layout().addWidget(toolpanel.intensitiesRadio)


#		displayGroup.layout().addWidget(displayWhatGroup)

		vbox.addWidget(displayGroup)

		plotGroup = QtGui.QGroupBox("Right Display")
		plotGroup.setLayout(QtGui.QVBoxLayout())

		toolpanel.farFieldRadio = QtGui.QRadioButton("Far Field Intensities")
		toolpanel.farFieldRadio.toggled.connect(self.onFarFieldRadioToggled)
		toolpanel.pointCalculationRadio = QtGui.QRadioButton("Animate Calculation ")
		toolpanel.pointCalculationRadio.setVisible(False)
		toolpanel.farFieldRadio.setChecked(True)
		plotGroup.layout().addWidget(toolpanel.farFieldRadio)
		plotGroup.layout().addWidget(toolpanel.pointCalculationRadio)


#		displayGroup.layout().addWidget(displayWhatGroup)

		vbox.addWidget(plotGroup)


		integrationGroup = QtGui.QGroupBox("Time Integration")
		integrationGroup.setLayout(QtGui.QVBoxLayout())

		toolpanel.instantaneousRadio = QtGui.QRadioButton("Instantaneous Values")
		toolpanel.integratedRadio = QtGui.QRadioButton("Time Integrated Values")	
		toolpanel.integratedRadio.toggled.connect(self.onTimeIntegratedRadioToggled)
		toolpanel.integratedRadio.setChecked(True)
		integrationGroup.layout().addWidget(toolpanel.instantaneousRadio)
		integrationGroup.layout().addWidget(toolpanel.integratedRadio)

#		displayGroup.layout().addWidget(displayWhatGroup)

#		vbox.addWidget(integrationGroup)
		vbox.addStretch()
		toolpanel.setSizePolicy(QtGui.QSizePolicy.Preferred,QtGui.QSizePolicy.Preferred)

		return toolpanel
	def onNrSourcesSpinValueChanged(self, newValue):
		if(self.nrSources == newValue):
			return
		self.nrSources = newValue
		self.sourcePositions = []
		self.sourceX = []
		self.slitSize = []
		self.sourceTimers = []
		for i in range(0,newValue):
			self.sourcePositions.append(((i+1)*self.sceneHeight)/(newValue+1))
			self.slitSize.append(self.baseSlitSize)
			self.sourceX.append(self.baseX)
			self.phaseShift.append(0)
			timer = QtCore.QTimer()
			timer.source = i
			timer.setInterval(50)
			timer.timeout.connect(self.onAnimationTimerTimeout)
			self.sourceTimers.append(timer)

		self.toolpanel.selectedSourceSpin.setMaximum(self.nrSources)	
		self.onSelectedSourceSpinValueChanged(self.toolpanel.selectedSourceSpin.value())


		self.drawSources()
	def onSelectedSourceSpinValueChanged(self, newValue):		
		self.toolpanel.positionSpin.setValue(self.sourcePositions[newValue-1])
		self.toolpanel.slitSizeSpin.setValue(self.slitSize[newValue-1])
		self.toolpanel.positionXSpin.setValue(self.sourceX[newValue-1])
		self.toolpanel.phaseShiftDial.setValue(self.phaseShift[newValue-1])
	def onSlitsRadioToggled(self,checked):
		if(not checked):
			self.toolpanel.slitSizeSpin.setVisible(False)
			self.toolpanel.slitSizeLabel.setVisible(False)
			self.toolpanel.positionXSpin.setVisible(True)
			self.toolpanel.positionXLabel.setVisible(True)
			self.toolpanel.phaseShiftDial.setVisible(True)
			self.toolpanel.phaseShiftLabel.setVisible(True)
			self.toolpanel.phaseShiftDisplay.setVisible(True)
			self.toolpanel.pointCalculationRadio.setVisible(True)
		else:
			self.toolpanel.slitSizeSpin.setVisible(True)
			self.toolpanel.slitSizeLabel.setVisible(True)
			self.toolpanel.positionXSpin.setVisible(False)
			self.toolpanel.positionXLabel.setVisible(False)
			self.toolpanel.phaseShiftDial.setVisible(False)
			self.toolpanel.phaseShiftLabel.setVisible(False)
			self.toolpanel.phaseShiftDisplay.setVisible(False)
			self.toolpanel.farFieldRadio.setChecked(True)
			self.toolpanel.pointCalculationRadio.setVisible(False)
		self.drawSources()
	def onIntensitiesRadioToggled(self,checked):
		if(checked):
			pass
#			print "Intensities"
		else:
			pass
#			print "Amplitudes"
	def onTimeIntegratedRadioToggled(self,checked):
		if(checked):
			pass
#			print "Time integrated"
		else:
			pass
#			print "Instantaneous"
	def onSimulateTimeCheckToggled(self,checked):
		if(checked):
			self.simulateTimeTimer.start()
		else:
			self.simulateTimeTimer.stop()
	def onWavelengthSpinValueChanged(self, newValue):
		self.wavelength = newValue
		self.updateField()			
	def onPhaseDialValueChanged(self, newValue):
		self.globalPhase = newValue		
		self.drawField()
	def onSlitSizeSpinValueChanged(self, newValue):
		if(self.slitSize[self.toolpanel.selectedSourceSpin.value()-1] == newValue):
			return
		self.slitSize[self.toolpanel.selectedSourceSpin.value()-1] = newValue
		self.drawSources()	
	def onPositionSpinValueChanged(self, newValue):
		if(self.sourcePositions[self.toolpanel.selectedSourceSpin.value()-1] == newValue):
			return
		self.sourcePositions[self.toolpanel.selectedSourceSpin.value()-1] = newValue
		self.drawSources()		
	def onPositionXSpinValueChanged(self, newValue):
		if(self.sourceX[self.toolpanel.selectedSourceSpin.value()-1] == newValue):
			return
		self.sourceX[self.toolpanel.selectedSourceSpin.value()-1] = newValue
		self.drawSources()		
	def onAmplitudesRadioToggled(self, checked):
		if(checked):
			self.toolpanel.phaseDial.setVisible(True)
			self.toolpanel.phaseLabel.setVisible(True)
			self.toolpanel.phaseDisplay.setVisible(True)
			self.toolpanel.simulateTimeCheck.setVisible(True)
			self.toolpanel.simulateTimeLabel.setVisible(True)
			self.toolpanel.farFieldRadio.setChecked(True)
			self.toolpanel.pointCalculationRadio.setVisible(False)
		else:
			self.toolpanel.phaseDial.setVisible(False)
			self.toolpanel.phaseLabel.setVisible(False)
			self.toolpanel.phaseDisplay.setVisible(False)
			self.toolpanel.simulateTimeCheck.setChecked(False)
			self.toolpanel.simulateTimeCheck.setVisible(False)
			self.toolpanel.simulateTimeLabel.setVisible(False)
			self.toolpanel.pointCalculationRadio.setVisible(True)

		self.drawField()
	def onFarFieldRadioToggled(self, checked):
		if(checked):
			self.resetAnimation()
			self.pointSelection.hide()
			self.proxy.hide()
			pass
		else:
			self.resetAnimation()
#			self.animationStep = 0
			self.pointSelection.show()
			self.proxy.show()
		self.drawFarField()
	def onPhaseShiftDialValueChanged(self,newValue):
		if(self.phaseShift[self.toolpanel.selectedSourceSpin.value()-1] != newValue):	
			self.phaseShift[self.toolpanel.selectedSourceSpin.value()-1] = newValue
			self.updateField()
	def drawSources(self):
		# Clear existing sources from scene
		for o in self.sourceObjects:
			self.nearScene.removeItem(o)
		self.sourceObjects = []

		if(self.toolpanel.slitsRadio.isChecked()):
			wall = QtGui.QGraphicsRectItem(self.baseX-self.slitThickness/2+1,0,self.slitThickness-2,self.sceneHeight)
			wall.setBrush(QtGui.QBrush(QtGui.QColor("#f57900")))
			wall.setPen(QtGui.QPen(QtGui.QColor("#f57900")))
			self.nearScene.addItem(wall)
			self.sourceObjects.append(wall)
			wall.setZValue(0.5)
		for i in range(0,self.nrSources):
			if(self.toolpanel.slitsRadio.isChecked()):
				source = slitItem(i,self,self.baseX-self.slitThickness/2,self.sourcePositions[i]-self.slitSize[i]/2,self.slitThickness,self.slitSize[i])
				source.setBrush(QtGui.QBrush(QtGui.QColor("#000000")))
				source.setPen(QtGui.QPen(QtGui.QColor("#000000")))
				source.setZValue(1)
				self.nearScene.addItem(source)
				self.sourceObjects.append(source)
			else:
				source = pointSourceItem(i,self,self.sourceX[i]-self.pointSize/2,self.sourcePositions[i]-self.pointSize/2,self.pointSize,self.pointSize)
				source.setBrush(QtGui.QBrush(QtGui.QColor("#f57900")))
				source.setPen(QtGui.QPen(QtGui.QColor(255,0,0,0),20))
				source.setZValue(1)
				self.nearScene.addItem(source)
				self.sourceObjects.append(source)
		self.updateField()		
	def calculateSlitField(self,pos,width,order):
		nsamples = (order*width)/self.wavelength
		E = np.zeros(self.E.shape,complex)
		if(nsamples < 1):
			nsamples = 1
		pos_boundaries = np.linspace(pos-width/2.0,pos+width/2.0,nsamples+1) 
		pos_boundaries = (pos_boundaries[0:-1]+pos_boundaries[1:])/2.0
		for p in pos_boundaries:
			dist = np.sqrt(self.slitDX2+(self.Ey-p)**2.0)/self.wavelength
			E += np.exp((-2.0j*math.pi*dist))
		return E
	def calculateSlitFarField(self,pos,width,order):
		nsamples = (order*width)/self.wavelength
		farE = np.zeros(self.farE.shape,complex)
		if(nsamples < 1):
			nsamples = 1
		pos_boundaries = np.linspace(pos-width/2.0,pos+width/2.0,nsamples+1) 
		pos_boundaries = (pos_boundaries[0:-1]+pos_boundaries[1:])/2.0
		farY =  np.linspace(-self.sceneHeight*self.farX/self.nearSceneWidth/2,self.sceneHeight*self.farX/self.nearSceneWidth/2,self.sceneHeight)
		for p in pos_boundaries:
			dist = np.sqrt((self.farX-self.baseX)**2.0+(farY-p)**2.0)/self.wavelength
			farE += np.exp((-2.0j*math.pi*dist))
		return farE
	def calculateField(self):		
		now = time.time()
		self.E = np.zeros(self.E.shape,complex)
		self.farE = np.zeros(self.farE.shape,complex)
		if(self.toolpanel.slitsRadio.isChecked()):
			order = 3;
			for i in range(0,self.nrSources):
				self.E += self.calculateSlitField(self.sourcePositions[i],self.slitSize[i],order)
				self.farE += self.calculateSlitFarField(self.sourcePositions[i],self.slitSize[i],order)
			self.E[:,0:self.baseX/self.downSampling] = 0
		else:	
#			x,y = np.meshgrid(np.arange(self.downSampling/2.0,self.E.shape[1]*self.downSampling,self.downSampling),np.arange(self.downSampling/2.0,self.E.shape[0]*self.downSampling,self.downSampling))
			x = self.Ex
			y = self.Ey			
			farY =  np.linspace(-self.sceneHeight*self.farX/self.nearSceneWidth/2,self.sceneHeight*self.farX/self.nearSceneWidth/2,self.sceneHeight)
			for i in range(0,self.nrSources):
				dist = np.sqrt((self.Ex-self.sourceX[i])**2.0+(y-self.sourcePositions[i])**2.0)/self.wavelength
				self.E += np.exp((-2.0j*math.pi*dist))*np.exp(-2.0j*math.pi*(self.sourceX[i]-self.baseX)/self.wavelength)*np.exp(-2.0j*math.pi*self.phaseShift[i]*math.pi/180.0)
				dist = np.sqrt((self.farX-self.sourceX[i])**2.0+(farY-self.sourcePositions[i])**2.0)/self.wavelength
				self.farE += np.exp((-2.0j*math.pi*dist))*np.exp(-2.0j*math.pi*(self.sourceX[i]-self.baseX)/self.wavelength)*np.exp(-2.0j*math.pi*self.phaseShift[i]*math.pi/180.0)
#		print time.time() - now
		self.drawField()
		self.statusBar().showMessage('Done')  
	def drawField(self):
		if(self.toolpanel.amplitudesRadio.isChecked()):
			colormap = np.real(self.E*np.exp(1.0j*math.pi*self.globalPhase/180.0))
			colormap -= np.min(colormap[:])
		else:
			colormap = np.abs((self.E*np.exp(1.0j*math.pi*self.globalPhase/180.0)))**2		
		c_max = np.max(colormap[:])
		if(c_max != 0):
			colormap *= 255.0/c_max
		colormap = colormap.astype(np.uint32)
		colormap = (255 << 24 | colormap[:,:] << 16 | colormap[:,:] << 8 | colormap[:,:]).flatten()
		im = QtGui.QImage(colormap, self.E.shape[1], self.E.shape[0], QtGui.QImage.Format_RGB32)
		self.nearScene.removeItem(self.fieldItem)
		self.pixmap = QtGui.QPixmap.fromImage(im)		
		self.fieldItem.setPixmap(self.pixmap)
		self.nearScene.addItem(self.fieldItem)
		self.drawFarField()
	def plotFarField(self,fx):
		p = QtGui.QPainterPath()
		scale = np.max(fx)
		if(scale == 0):
			scale = 1
		plot_width = 140;
		plot_start = 30;
		p.moveTo(plot_start+(plot_width*fx[0])/scale,0)
		for i in range(1,len(fx)):
			p.lineTo(plot_start+(plot_width*fx[i])/scale,i)			
		path = QtGui.QGraphicsPathItem(p)
		path.setPen(QtGui.QPen(QtGui.QColor("#3465a4"),3,QtCore.Qt.SolidLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
		self.plotObjects.append(path)
		self.farScene.addItem(path)
		path.setZValue(10)
		line = QtGui.QGraphicsLineItem(plot_start,0,plot_start,self.sceneHeight)
		line.setPen(QtGui.QPen(QtGui.QColor("#f57900"),1,QtCore.Qt.SolidLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
		self.plotObjects.append(line)
		self.farScene.addItem(line)
		line.setZValue(9)


#		path = QtGui.QGraphicsPathItem(p)
#		path.setPen(QtGui.QPen(QtGui.QColor("#000000"),3,QtCore.Qt.SolidLine,QtCore.Qt.RoundCap,QtCore.Qt.RoundJoin))
#		self.plotObjects.append(path)
#		path.setZValue(5)
#		self.farScene.addItem(path)

	def drawFarField(self):
		if(self.farFieldItem.scene()):
			self.farScene.removeItem(self.farFieldItem)
		# Clear existing sources from scene
		for o in self.plotObjects:
			self.farScene.removeItem(o)
		self.plotObjects = []
		if(self.toolpanel.farFieldRadio.isChecked()):
#			if(self.toolpanel.amplitudesRadio.isChecked()):
#				fx = np.real(self.farE*np.exp(1.0j*math.pi*self.globalPhase/180.0))
#				fx -= np.min(fx[:])
#			else:
#				fx = np.abs((self.farE*np.exp(1.0j*math.pi*self.globalPhase/180.0)))**2		
			fx = np.abs((self.farE*np.exp(1.0j*math.pi*self.globalPhase/180.0)))**2
			offset = 0
			colormap = fx[:]-offset
			scale = np.max(colormap[:])
			if(scale != 0):
				colormap *= 255.0/scale
			colormap = colormap.astype(np.uint32)
			colormap = (255 << 24 | colormap[:] << 16 | colormap[:] << 8 | colormap[:]).flatten()
			im = QtGui.QImage(colormap, 1, self.farE.shape[0], QtGui.QImage.Format_RGB32)			
			pixmap = QtGui.QPixmap.fromImage(im)		
			self.farFieldItem.setPixmap(pixmap.scaled(self.farSceneWidth,pixmap.height()))
			self.farScene.addItem(self.farFieldItem)
			self.plotFarField(fx)
		else:
			fontSize = 18
			x = int(self.pointSelection.x())
			y = int(self.pointSelection.y())
			E = np.real(self.E[y,x])
			self.animationBox = QtGui.QGroupBox("Selected Point");
			self.animationBox.resize(self.farSceneWidth,self.sceneHeight/5)
			self.animationBox.setLayout(QtGui.QVBoxLayout())
			self.animationBoxX.setText("Point x = "+str(x))
			self.animationBoxY.setText("Point y = "+str(y))
			self.animationBoxE.setText("E = %5.3g"%(E))
			self.animationBoxStep.setText("Calculation Step: %d" %(self.animationStep))
			self.animationSlider.setValue(self.animationStep)
			self.animationSlider.setMaximum(self.countSteps())
	def onAnimationSliderValueChanged(self,newValue,multiStep = False):
		if(not multiStep):
			if(newValue > self.animationStep+1):
				self.animationSlider.setValue(self.animationStep+1)
				return
			if(newValue < self.animationStep-1):
				self.animationSlider.setValue(self.animationStep-1)
				return
		step = 0
		x = int(self.pointSelection.x())
		y = int(self.pointSelection.y())
		E = np.real(self.E[y,x])
		if(self.animationStep <= step and newValue > step):
			self.pointSelection.hideLines()
		elif(newValue <= step and self.animationStep > step):
			self.pointSelection.showLines()
		step += 1
		for i in range(0,self.nrSources):	
			if(self.animationStep <= step and newValue > step):
				line = QtGui.QGraphicsLineItem(self.sourceX[i],self.sourcePositions[i],self.sourceX[i],self.sourcePositions[i])
				line.setZValue(10)
				grad = QtGui.QRadialGradient(QtCore.QPointF(self.sourceX[i], self.sourcePositions[i]), self.wavelength);
				grad.setColorAt(0, QtGui.QColor("#3465a4"))
				grad.setColorAt(0.5, QtGui.QColor("#f57900"))
				grad.setColorAt(1, QtGui.QColor("#3465a4"))
				grad.setSpread(QtGui.QGradient.RepeatSpread)

				brush = QtGui.QBrush(grad)
				line.setPen(QtGui.QPen(brush,6))
				self.sourceLines.append(line)
				self.sourceTimers[i].start(20)
				self.sourceTimers[i].step = 0
				self.sourceTimers[i].maxStep = 100
				self.sourceTimers[i].deltaX = (x-self.sourceX[i])
				self.sourceTimers[i].deltaY = (y-self.sourcePositions[i])
				self.nearScene.addItem(line)
				self.animationSlider.setEnabled(False);
			elif(newValue <= step and self.animationStep > step):
				if(len(self.sourceLines)):
					self.nearScene.removeItem(self.sourceLines.pop())
					self.bottomArgand.removeSource(len(self.sourceLines))
					self.topArgand.hand.hide()
					self.topArgand.hand.setRotation(0)
					self.topArgand.hand.show()
			step += 1

		if(newValue != self.animationStep):
			self.animationStep = newValue
			self.drawFarField()
	def resetAnimation(self):
		self.animationStep = self.countSteps()
		self.onAnimationSliderValueChanged(0,True)		
		self.bottomArgand.hideHands()
		self.topArgand.hand.hide()
		self.topArgand.hand.setRotation(0)
		self.topArgand.hand.show()
	def timeStep(self):
		self.toolpanel.phaseDial.setValue(self.toolpanel.phaseDial.value()+5)
	def updateField(self):
		self.resetAnimation()
		self.statusBar().showMessage('Calculating Field...')
		self.calculateFieldTimer.start()
	def countSteps(self):
		return 1+self.nrSources
	def onAnimationTimerTimeout(self):
		i = self.sender().source
		t = self.sender()
		t.step += 1
		self.sourceLines[i].setLine(self.sourceX[i],self.sourcePositions[i],self.sourceX[i]+float(t.step*t.deltaX)/t.maxStep,self.sourcePositions[i]+float(t.step*t.deltaY)/t.maxStep)
		self.topArgand.hand.setRotation(-360*t.step*math.sqrt(t.deltaX**2+t.deltaY**2)/(t.maxStep*self.wavelength)-360*(self.sourceX[i]-self.baseX)/self.wavelength)
		if(t.step == t.maxStep):
			self.bottomArgand.addSource(i,-360*t.step*math.sqrt(t.deltaX**2+t.deltaY**2)/(t.maxStep*self.wavelength))
			self.animationSlider.setEnabled(True);
			t.stop()


def main():
	app = QtGui.QApplication(sys.argv)
	mw = MainWindow()
	sys.exit(app.exec_())

if __name__ == '__main__':
  main()