"""
OpenPMU XML SV Simulator produces a stream of data like that from an OpenPMU ADC board.
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


from __future__ import print_function
import os
import time
from datetime import datetime, timedelta
import numpy as np
import socket
from lxml import etree
import base64
from PyQt5.QtCore import QThread

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

# convert from dict to xml value
# if no conversion needed, delete it from the expression
dictTypeConvert = lambda key: {'Frame': str,
                               'Fs': str,
                               'n': str,
                               'Channels': str,
                               'Payload': base64.standard_b64encode,
                               'bits': str,
                               }.get(key, lambda x: x)


class PMUCape(QThread):
    def __init__(self, frequencies, phaseAngles, channels, ip="127.0.0.1", port=48001):
        QThread.__init__(self, )

        self.frequencies = np.array(frequencies, ndmin=2).T
        self.phaseAngles = np.array(phaseAngles, ndmin=2).T
        self.channels = channels

        self.interval = 0.01  # seconds
        self.Fs = 12800
        self.n = int(self.Fs * self.interval)
        self.ADCRange = 2 ** 15 - 1
        self.bits = 16

        self.newFrequencies = [0] * channels
        self.fChanged = False

        self.ip = ip
        self.port = port

        self.stopThread = False
        self.xmlTemplate = etree.parse(os.path.join(SCRIPT_DIRECTORY, "PMUCape.xml"))

    def run(self):
        self.stopThread = False

        socketOut = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketFwd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    
        # basic information
        resultDict = dict()
        resultDict["Fs"] = self.Fs
        resultDict["n"] = self.n
        resultDict["Channels"] = self.channels
        resultDict["bits"] = self.bits

        # frame count
        frame = 0
        # time information for cos function
        intervalDelta = timedelta(seconds=self.interval)
        prePhase = np.zeros([self.channels, 1])  # phase angle
        preOmega = np.zeros([self.channels, 1])  # last angular speed
        tSeries = np.expand_dims(np.linspace(0, self.interval, self.n+1, endpoint=True), axis=0)  # time

        while not self.stopThread:
            now = datetime.now()
            resultDict["Time"] = now.time().strftime("%H:%M:%S") + ".%03d" % (frame * self.interval * 1000)
            resultDict["Date"] = now.date().strftime("%Y-%m-%d")
            resultDict["Frame"] = frame

            newOmega = 2 * np.pi * self.frequencies  # angular speed
            # linear chirp
            phaseSeries = np.dot(newOmega, tSeries) + np.dot((newOmega - preOmega), np.power(tSeries, 2)) / 2.0 / self.interval + prePhase
            prePhase = np.expand_dims(phaseSeries[:, -1], axis=1)
            preOmega = newOmega

            payload = (np.cos(phaseSeries[:,0:-1] + self.phaseAngles) * self.ADCRange).astype(np.int16).byteswap()
            for i in range(self.channels):
                Channel_i = "Channel_%d" % i
                resultDict[Channel_i] = dict()
                resultDict[Channel_i]["Payload"] = payload[i, :]

            xml = self.toXML(resultDict)
            socketOut.sendto(xml, (self.ip, self.port))
            socketFwd.sendto(xml, ("127.0.0.1", 48005))    
            
            frame += 1
            if (frame == int(1 / self.interval)):
                frame = 0

            # delay some time, this is not accurate
            s = (intervalDelta - (datetime.now() - now)).total_seconds()
            # print (s)
            time.sleep(s if s > 0 else 0)

    def stop(self):
        self.stopThread = True

    # convert from python dictionary to a XML string
    def toXML(self, resultDict):
        level0 = self.xmlTemplate.getroot()

        try:
            for level1 in list(level0):
                tag1 = level1.tag
                if tag1 in resultDict.keys():
                    if tag1.startswith("Channel_"):
                        for level2 in list(level1):
                            tag2 = level2.tag
                            if tag2 in resultDict[tag1].keys():
                                level2.text = dictTypeConvert(tag2)(resultDict[tag1][tag2])

                    else:
                        level1.text = dictTypeConvert(tag1)(resultDict[tag1])
                else:
                    level0.remove(level1)
        except KeyError as e:
            print("XML tag error: ", e)
        xml = etree.tostring(level0, encoding="utf-8")
        return xml

    def setFrequency(self, frequencies):
        self.frequencies = np.array(frequencies, ndmin=2).T

