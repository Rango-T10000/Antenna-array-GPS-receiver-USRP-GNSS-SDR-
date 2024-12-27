# Antenna-array-GPS-receiver-USRP-GNSS-SDR
This is a GPS receiver testbed with antenna array, built based on USRP X310 and GNSS-SDR.
Follow this instruction, you can build a testbed quickly 😎.
## Introduction
This project is a GPS receiver testbed with antenna array, built based on USRP X310 and GNSS-SDR. The receiver is designed to receive GPS signals from multiple antennas(1x4 ants) and process them to improve the accuracy of the position estimation. The gps signal is received by an USRP X310, and then the signal is processed by GNSS-SDR to get the position information. This project can be used for GPS positioning, navigation, and some other research purposes, which need to receive gps signal via an antenna array.

## Hardware
The hardware used in this project includes:
- **USRP X310:** a software-defined radio platform (RF_front_end) for receiving and transmitting radio signals. My USRP X310 has two TwinRX-80MHz daughterboards with 4 RX channels in total, which can be connected to 4 antennas.
- **GPS active antenna**:  4 active GNSS antennas, which have internal LNA and need to be powered with 3~5 V DC.
- Antenna array: using above described 4 active GNSS antennas fixed on a line with $\frac{\lambda }{2} \approx 9.5cm$ spacing among them.
- **Bias-Tee**: a RF Bias Tee is used to feed DC power to active antenna.
- **GPSDO:** a GPS disciplined oscillator is used to provide a stable reference clock for the USRP X310. And this GPSDO need to connect a passive GPS antenna. Once it runs correctly and shows GPS locked, 10MHz signal and 1PPS signal will be generated and provided to USRP X310.
- **PC:** a computer with GNSS-SDR installed, which is used to configure and control the USRP X310 and GNSS-SDR. I use a compact industrial computer: IPC-240 with Ubuntu 20.04. To have enough communication bandwidth to aviod overflow error, I have a 10Gbps Ethernet controller in my PC and use a 10Gbps Ethernet cable to connect the PC and the USRP X310.

## Software
The software used in this project includes:
- **GNSS-SDR:** an open-source software defined radio receiver for GNSS signals.You can install the gnss-sdr following the instruction in https://gnss-sdr.org/.
- **UHD:** a driver for USRP X310 to communicate with the USRP hardware.
- **GNURadio:** a software development toolkit that enables the creation of radio communications applications using GNU Radio blocks.

## Testbed Overview
![testbed](/figs/testbed.png)

## Usage
To use this project, you need to install GNSS-SDR on your computer at first. Then, you can build this testbed and configure the GNSS-SDR to receive GPS signals from multiple antennas and process them to get the output decoded files. The configuration file for GNSS-SDR can be modified to adjust the parameters of the receiver, such as the sampling rate, the number of antennas, and the signal source if you use other type of SDR.

### 1. Install gnss-sdr
You can install gnss-sdr following the instruction in https://gnss-sdr.org/. After installing it in Ubuntu 22.04, 20.04 and MacOS, I really recommand to Install on an Ubuntu. Don't waste your time to install gnss-sdr on MacOS, it's really difficult and bad to use. My software versions are:
- Ubuntu 20.04 (on IPC-240)
- gnss-sdr 0.19
- UHD 4.0
- GNU Radio 3.9

If using Ubuntu 20.04 or 22.04, I provide the optimal install steps as follow:
（1） 

### 2. Build this testbed

### 3. Matters need attention

### 4. Run and process the result



## Reference
- GNSS-SDR: https://gnss-sdr.org/
- USRP X310: https://www.ettus.com/products/boards/usrp-x310 
