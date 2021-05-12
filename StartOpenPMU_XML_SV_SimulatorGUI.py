"""
OpenPMU XML SV Simulator (GUI) produces a stream of data like that from an OpenPMU ADC board.
Copyright (C) 2021  OpenPMU

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""


#!/usr/bin/python

import os, sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSettings, QSize, QPoint
#from PyQt5.QtGui import QApplication, QIcon, QDoubleSpinBox, QDial
from PyQt5 import uic
from OpenPMU_XML_SV_Simulator import PMUCape
import numpy as np

# sys.path.append('../..')
from dependencies import tools


# the main ui
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
UI_FILE = os.path.join(SCRIPT_DIRECTORY, 'PMUCapeSimulatorGUI.ui')
FormTemplate, BaseTemplate = uic.loadUiType(UI_FILE)


class MainWindow(BaseTemplate):
    def __init__(self):
        BaseTemplate.__init__(self)
        self.ui = FormTemplate()
        self.ui.setupUi(self)
        self.readSettings()

        self.channels = 6

        self.ui.ip.addItems(tools.getLocalIP())
        self.ui.startBtn.clicked.connect(self.start)
        self.isStarted = False

        self.spins = self.findChildren(QDoubleSpinBox)
        #self.spins.sort(cmp=lambda x, y: cmp(str(x.objectName()), str(y.objectName())))
        
        # New Sort Function by DML for Python 3
        # Sorts the QDoubleSpinBoxes in order  of last character of objectName
        x = [0]*len(self.spins)
        
        for s in self.spins:
            x[int(s.objectName()[-1])] = s
            
        self.spins = x
        
        for s in self.spins:
            s.valueChanged.connect(self.frequencyChanged)

        self.dials = self.findChildren(QDial)
        #self.dials.sort(cmp=lambda x, y: cmp(str(x.objectName()), str(y.objectName())))
        
        # New Sort Function by DML for Python 3
        # Sorts the QDials in order of last character of objectName
        x = [0]*len(self.dials)
        
        for s in self.dials:
            x[int(s.objectName()[-1])] = s
            
        self.dials = x

        
        for d in self.dials:
            d.valueChanged.connect(self.frequencyChanged)

        self.frequencies = [s.value() for s in self.spins]
        self.dataThread = PMUCape(self.frequencies, np.array([0, 1, 2, 0, 1, 2]) * np.pi * 2 / 3, self.channels)
        self.frequencies = [50.0] * self.channels

    def frequencyChanged(self, fre):
        s = self.sender()
        id = int(s.objectName()[-1])
        f = s.value()
        print(id,f)
        self.dials[id].blockSignals(True)
        self.spins[id].blockSignals(True)
        self.dials[id].setValue(int(f))
        self.spins[id].setValue(f)
        self.dials[id].blockSignals(False)
        self.spins[id].blockSignals(False)

        self.frequencies = [s.value() for s in self.spins]
        self.dataThread.setFrequency(self.frequencies)
        # if isinstance(s, QDoubleSpinBox):
        #     self.dials[id].setValue(int(f))
        #     self.frequencies = [s.value() for s in self.spins]
        #     self.dataThread.setFrequency(self.frequencies)
        #     print(f)
        # if isinstance(s, QDial):
        #     # print(id,s.objectName(),self.spins[id].objectName())
        #     self.spins[id].setValue(f)
        #     print(s.objectName(), self.spins[id].objectName())

    def start(self):
        if not self.isStarted:
            self.ui.startBtn.setText('Stop')
            self.dataThread.ip = self.ui.ip.lineEdit().text()
            self.dataThread.port = int(self.ui.port.text())
            self.dataThread.start()
            self.isStarted = True
        else:
            self.ui.startBtn.setText('Start')
            self.dataThread.stop()
            self.isStarted = False

    # when closing app, save settings
    def closeEvent(self, event):

        if self.isStarted:
            self.dataThread.stop()
            self.dataThread.wait(1000)
        self.writeSettings()
        event.accept()

    # save settings
    def writeSettings(self):
        settings = QSettings("xzhao", "PMUCapeSimulatorGUI")
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
        settings.setValue("ip", self.ui.ip.lineEdit().text())
        settings.setValue("port", self.ui.port.text())

        for s in self.spins:
            settings.setValue(s.objectName(), s.value())

        for d in self.dials:
            settings.setValue(d.objectName(), d.value())

    # read settings
    def readSettings(self):
        settings = QSettings("xzhao", "PMUCapeSimulatorGUI")
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.resize(size)
        self.move(pos)
        self.ui.ip.lineEdit().setText(settings.value("ip", "127.0.0.1"))
        self.ui.port.setText(settings.value("port", "48001"))

        spins = self.findChildren(QDoubleSpinBox)
        for s in spins:
            s.setValue(float(settings.value(s.objectName(), 50)))

        dials = self.findChildren(QDial)
        for d in dials:
            d.setValue(float(settings.value(d.objectName(), 50)))


def main():

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
