# Antenna-array-GPS-receiver-USRP-GNSS-SDR
This is a GPS receiver with antenna array, built based on USRP X310 and GNSS-SDR.

## Introduction
This project is a GPS receiver with antenna array, built based on USRP X310 and GNSS-SDR. The receiver is designed to receive GPS signals from multiple antennas(1x4 ants) and process them to improve the accuracy of the position estimation. The gps signal is received by an USRP X310, and then the signal is processed by GNSS-SDR to get the position information. This project can be used for GPS positioning, navigation, and some other research purposes, which need to receive gps signal via an antenna array.

## Hardware
The hardware used in this project includes:
- USRP X310: a software-defined radio platform for receiving and transmitting radio signals.
- GPS antennas: multiple antennas are used to receive GPS signals from different directions.
- Antenna array: an antenna array is used to receive GPS signals from multiple antennas and process them to improve the accuracy of the position estimation.

## Software
The software used in this project includes:
- GNSS-SDR: an open-source software defined radio receiver for GNSS signals.
- USRP driver: a driver for USRP X310 to communicate with the USRP hardware.
- GPS receiver driver: a driver for GPS receiver module to communicate with the GPS receiver hardware.

## Usage
To use this project, you need to install GNSS-SDR, USRP driver, and GPS receiver driver. Then, you can configure the GNSS-SDR to use the USRP X310 and GPS receiver module to receive GPS signals from multiple antennas and process them to improve the accuracy of the position estimation. The configuration file for GNSS-SDR can be modified to adjust the parameters of the receiver, such as the sampling rate, the number of antennas, and the position of the antennas.

## Reference
- GNSS-SDR: https://gnss-sdr.org/
- USRP X310: https://www.ettus.com/products/boards/usrp-x310
- GPS receiver: https://www.u-blox.com/en/products/gps-modules/u-blox-gps-modules
- Antenna array: https://www.antennaarray.com/

![test](/imgs/Snipaste_2024-12-27_10-43-32.png)