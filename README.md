# loom
Python program to generate and analyze spectral networks

## Overview
loom has the following functionality.
* Generate a single spectral network for a given Seiberg-Witten data at a phase.
* Generate multiple spectral networks at various phases by utilizing parallel computation.
  * To generate multiple spectral networks, need to specifiy ```phase``` to ```None```.
  * Generating multiple spectral networks doesn't work on Windows.
* Save and load analytical and numerical configurations.
* Save and load generated data in JSON.
* Plot spectral networks with interactive labeling.

## Screenshots

![loom screenshot](https://github.com/chan-y-park/loom/blob/master/screeenshots/loom_desktop.png "loom desktop")
![loom menu screenshot](https://github.com/chan-y-park/loom/blob/master/screeenshots/loom_menu.png "loom menu")
![loom plot screenshot](https://github.com/chan-y-park/loom/blob/master/screeenshots/loom_plot.png "loom plot")

## To Do List
### Core
* sometimes loom does not exit after making a plot and closing it.
* mplcursor not working properly.
  * right-click doesn't remove the label when plotting multiple networks
  * make label appear when hovering the mouse cursor over an artist.
    * hard to point a branch point and show the label in this case.
* implement an option to change between the intersection finding routines. 
* logging to file
* egg?
* SciPy warnings
  * ```/usr/local/lib/python2.7/dist-packages/scipy/optimize/zeros.py:150: RuntimeWarning: Tolerance of 0.000513046300877562 reached
  warnings.warn(msg, RuntimeWarning)```
  * divide by zero
* API for getting D-type joints using other method than the Z_2 projection.
### GUI

## How to run this program
An easy way to run ```loom``` is downloading a standalone binary and executing it.

### Standalone

#### Windows
* Generating multiple spectral networks doesn't work on Windows.
* Was not able to make it work yet.

#### Linux
* Download ```gui_loom``` from:
  * http://chan.physics.rutgers.edu/files/gui_loom.tar

#### Max OS X
* not built yet.

### Using Python
1. First install the required version of Python & its libraries, as described below.
1. There are three ways to run ```loom```.
  * ```gmain.py``` is an executable Python script that launches a GUI version of ```loom```.
  * ```main.py``` is a command-line version executable Python script.
  * In the Python interpreter import ```loom``` module.

#### Requirements
* Python >= 2.7.6
* Not tested on Python 3.

##### Library requirements
* NumPy >= 1.8.2
* SciPy >= 0.15.1
* SymPy >= 0.7.6
* Matplotlib > 1.4.1

#### Linux

##### Scientific Linux
  1. Install Tcl/Tk and their -devel packages
  1. BLAS/LAPACK/ATLAS (we did this after installing Python but I think it makes more sense if we do it before the build & the installation of Python)
  1. Build Python 2.7.6 and install it (possibly need to change CPPFLAGS variables to include header files for Tcl/Tk)
  1. Install pip by getting its Python source code and run it using Python (http://pip.readthedocs.org/en/latest/installing.html)
  1. Install nose (`sudo pip install nose`)
  1. NumPy
  1. SciPy
  1. Matplotlib
  1. SymPy

##### Ubuntu 14.04

1. from Ubuntu package
  1. ```sudo apt-get install python python-dev libatlas-base-dev gcc gfortran g++ python-numpy python-matplotlib ipython ipython-notebook python-pandas python-nose```
1. install SciPy 0.15.1
  1. Get the source code from http://sourceforge.net/projects/scipy/files/scipy/
  1. Unpack ```scipy-<version>.tar.gz```, change to the ```scipy-<version>/``` directory.
  1. ```python setup.py install```
  1. see http://www.scipy.org/install.html for additional help.

1. install SymPy 0.7.6
  1. Get the source code from https://github.com/sympy/sympy/releases 
  1. Unpack ```sympy-<version>.tar.gz```, change to the ```sympy-<version>/``` directory.
  1. ```sudo python setup.py install``` 

#### Windows
* Generating multiple spectral networks doesn't work on Windows.

##### Use Enthought Canopy
* As of now, incompatible with the current usage of matplotlib Tk backend

##### Installing Python and required libraries
1. Install Python 2.7.9
  1. https://www.python.org/downloads/
1. Install NumPy 1.9.2
  1. http://sourceforge.net/projects/numpy/files/NumPy/
  1. Choose a Windows installer, not .zip file.
1. Install SciPy 0.15.1
  1. http://sourceforge.net/projects/scipy/files/scipy/
  1. Choose a Windows installer, not .zip file.
1. Install matplotlib 1.4.3
  1. http://matplotlib.org/downloads.html
  1. requires ```dateutil, pytz, pyparsing, six```
    1. ```pip install python-dateutil```, ...
1. Install SymPy
  1. https://github.com/sympy/sympy/releases