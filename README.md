# OpenPMU XML SV Simulator

This provides a GUI which creates a simulated stream of sampled values (SV) in [OpenPMU V2's XML format](https://github.com/OpenPMU/OpenPMU/tree/master/XML_Datagrams).  These should be piped into the OpenPMU Phasor Estimator to produce a synchrophasor.  This is useful for development of new phasor estimation algorithms in a software only environment, without need for the OpenPMU ADC hardware.

The structure and format of the XML datagrams is [described here](https://github.com/OpenPMU/OpenPMU/tree/master/XML_Datagrams).

![Screenshot](/code/OpenPMU_XML_SV_Sim.png)

Licensed under GPLv3.  Collaborations towards development of this code and other aspects of the OpenPMU project are very welcome.

Requires Python 3.7 or later.  Has been tested using [WinPython](https://winpython.github.io/) 3.9.4 and on [Raspberry Pi OS](https://www.raspberrypi.org/software/operating-systems/) (March 4th 2021).

## Getting Started:

The code is run from the command line using `python OpenPMU_XML_SV_SimulatorGUI.py`. You may be asked to install some dependencies.

This simulator is useful to provide simulated waveform data to the [OpenPMU Phasor Estimator](https://github.com/OpenPMU/OpenPMU_Phasor_Estimator).

## Cite this work:

When citing this work, we recommend citing the following publication:

> X. Zhao, D. M. Laverty, A. McKernan, D. J. Morrow, K. McLaughlin and S. Sezer, "[GPS-Disciplined Analog-to-Digital Converter for Phasor Measurement Applications](https://ieeexplore.ieee.org/document/7931698)," in IEEE Transactions on Instrumentation and Measurement, vol. 66, no. 9, pp. 2349-2357, Sept. 2017, doi: 10.1109/TIM.2017.2700158.
