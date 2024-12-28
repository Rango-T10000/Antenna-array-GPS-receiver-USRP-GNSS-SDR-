# Antenna-array-GPS-receiver-USRP-GNSS-SDR
This is a GPS receiver testbed with antenna array, built based on USRP X310 and GNSS-SDR.
Follow this instruction, you can build a testbed quickly 😎.
## Introduction
This project is a GPS receiver testbed with antenna array, built based on USRP X310 and GNSS-SDR. The receiver is designed to receive GPS signals from multiple antennas(1x4 ants) and process them to improve the accuracy of the position estimation. The gps signal is received by an USRP X310, and then the signal is processed by GNSS-SDR to get the position information. This project can be used for GPS positioning, navigation, and some other research purposes, which need to receive gps signal via an antenna array.

## Hardware
The hardware used in this project includes:
- **USRP X310:** a software-defined radio platform (RF_front_end) for receiving and transmitting radio signals. My USRP X310 has two TwinRX-80MHz daughterboards with 4 RX channels in total, which can be connected to 4 antennas.
- **GPS active antenna**:  4 active GNSS antennas, which have internal LNA and need to be powered with 3~5 V DC. Due to that signal strangth is too weak, I do not recommand to use passive gps antennas, which don't have LNA within and only a patch antenna wrapped with a plastic casing.
- **Antenna array:** using above described 4 active GNSS antennas fixed on a line with $\frac{\lambda }{2} \approx 9.5cm$ spacing among them. In this project, I build a 1x4 antenna array. To build an array with more elements like 2x4, you need two synchronized USRP X310 with 8 RF channels.
- **Bias-Tee**: a bias tee is a three-port network used for setting the DC bias point of some electronic components without disturbing other components. In this project, this RF Bias Tee is used to feed DC power to active antenna.
- **GPSDO:** a GPS disciplined oscillator is used to provide a stable reference clock for the USRP X310. And this GPSDO need to connect a passive GPS antenna. Once it runs correctly and shows GPS locked, 10MHz signal and 1PPS signal will be generated and provided to USRP X310.
- **PC:** a computer with GNSS-SDR installed, which is used to configure and control the USRP X310 and GNSS-SDR. I use a compact industrial computer: IPC-240 with Ubuntu 20.04. To have enough communication bandwidth to aviod overflow error, I have a 10Gbps Ethernet controller in my PC and use a 10Gbps Ethernet cable to connect the PC and the USRP X310.

## Software
The software used in this project includes:
- **GNSS-SDR:** an open-source software defined radio receiver for GNSS signals.You can install the gnss-sdr following the instruction in https://gnss-sdr.org/.
- **UHD:** a driver for USRP X310 to communicate with the computer.
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

If using Ubuntu 20.04 or 22.04, I provide the optimal install steps as follow:<br>
**(1) install all dependencies**
```
sudo apt-get update
```
```
sudo apt-get install build-essential cmake git pkg-config libboost-dev libboost-date-time-dev \
       libboost-system-dev libboost-filesystem-dev libboost-thread-dev libboost-chrono-dev \
       libboost-serialization-dev liblog4cpp5-dev libuhd-dev gnuradio-dev gr-osmosdr \
       libblas-dev liblapack-dev libarmadillo-dev libgflags-dev libgoogle-glog-dev \
       libgnutls-openssl-dev libpcap-dev libmatio-dev libpugixml-dev libgtest-dev \
       libprotobuf-dev protobuf-compiler python3-mako
```
**(2) build and install gnss-sdr from source code**
```
git clone https://github.com/gnss-sdr/gnss-sdr.git
cd gnss-sdr
git branch -a        # check the different version/branch
git checkout next    # switch to the 'next' branch
git status           # check the current branch
mkdir build
cd build
cmake ..
make
sudo make install
```
>[1]: Before I install this gnss-sdr, I have already installed gnuradio and uhd. I have tested these two versions: 
> - gnss-sdr 0.19 + gnuradio 3.9 + uhd 4.0 on Ubuntu 20.04
> - gnss-sdr 0.19 + gnuradio 3.10.7.0 + uhd 4.1.0.5-3 on Ubuntu 22.04
> 
> If you don't have them, you can install them by following the instruction in https://wiki.gnuradio.org/index.php/InstallingGR. 
> 
>[2]: In above command, I use the 'next' branch. This is because after using `git clone https://github.com/gnss-sdr/gnss-sdr.git`, you are in the 'main' branch by default. However, I met so many problems when I use the 'main' branch to build and install. Here are some detailed errors:
> - Using the 'main' branch: https://github.com/gnss-sdr/gnss-sdr/issues/829#issue-2730121561
> - Build and install on MacOS: https://github.com/gnss-sdr/gnss-sdr/issues/835#issuecomment-2560897806; https://github.com/gnss-sdr/gnss-sdr/issues/829#issuecomment-2558781142
>
> [3]: Usually, when using `cmake ..` and `make`, a lot of errors will appear and most of them result of lack of some dependencies or the version of some dependencies is not compatible with gnss-sdr. You need to fix that by yourself. Using Linux is much easier than MacOS. Never try to waste time to install it on the MacOS. It's stupid and I have tried that 🤮.

**(3) test and make sure if install successfully**
According to the instruction in gnss-sdr(https://gnss-sdr.org/my-first-fix/), you need to run two executable files, go to the folder: `gnss-sdr/install` and run the following commands:
```
volk_profile
volk_gnsssdr_profile
```
Then, you can run the following command to test if the installation is successful:
```
gnss-sdr --version
```
If you see something like: `gnss-sdr version 0.0.19-xxx`, which means everything is great.
### 2. Build this testbed
![connect](/figs/connect.png)

### 3. Matters need attention




### 4. Run and process the result



## Reference
- GNSS-SDR: https://gnss-sdr.org/
- USRP X310: https://www.ettus.com/products/boards/usrp-x310 
