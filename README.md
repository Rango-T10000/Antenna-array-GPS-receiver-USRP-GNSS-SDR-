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

### 3. Run and process the result
First of all, you can download my project by:
```
git clone https://github.com/Rango-T10000/Antenna_array_GPS_receiver_USRP_GNSS-SDR.git
```
I provide two config files for running gnss-sdr. `real_time.conf` is used for receive data and decode data in a real-time way for just one antenna. And `post_processing.conf` is used for deconding the received data from Gnuradio-companion. Because of the weak signal, it's not easy you can capture the signal that can be decoded at once with 4 antennas. I suggest you can use only one antenna to test at the beginning. You can receive data and decode data in a real-time way for just one antenna by:
```
gnss-sdr --config_file=real_time.conf
``` 
In `real_time.conf`, I set the clock ref and time ref as external. So open GPSDO and you need to wait it runs correctly. You can tell that from the LED indicator in the real planel. Always run `uhd_usrp_probe` to confirm USRP is great and watch the output information in terminal that the GPSDO is detected. If everything is great, you can run the above command to receive data and decode data in a real-time way and you will see the output information in the terminal and you will find the decoded files in your folder.

Please be patient and wait for a while after running the command. It may take tens of seconds or even more than 1 min to get the position fix at the first time. You can deocde data successfully, if you find the similar output like this:
![decoded](/figs/Snipaste_2024-12-27_11-13-12.png)

After you can receive and decode signal with one antenna successfully, you can try to run the following command to receive data and decode data with 4 antennas. I use post processing method to deal with four antennas, which means I received the signal and record the raw data by Gnuradio-companion at first, and raw data from four antennas are stored in four .dat files. Then I use gnss-sdr to decode the raw data and get the position fix. 

Go to the `gnuradio_project` folder,  and open the provided `gps_rx.grc` file in Gnuradio-companion by:
```
gnuradio-companion gps_rx.grc
```
This gnuradio project is very simple, and it just consists of `Signal Source` block for receive the signal and `file sink` block for recording the raw data. Remember to change the file path to your own path. Then run the Gnuradio-companion and you will see the following figure:
![gnuradio](/figs/Snipaste_2024-12-27_10-43-32.png)

Don't be afraid of you can not see the signal hump in this frequency figure, it's normal. Because the signal is very weak and it just be buried under the noise. Don't worry, you will decode information from the raw data later.

Besides, I also provide a `gps_rx_final.py` which is copied from the `gps_rx.py`(generated by `gps_rx.grc` ). I add some code to let the recoded raw data with timestramp as the file name. As a result, you can just run the `gps_rx_final.py` script, which is same as running the `gps_rx.grc` file in Gnuradio-companion. For example, I recorded the raw data for about 6 mins:
![data example](/figs/data_example.png)

After getting these four .dat files, I run the gnss-sdr to decode the raw data and get the position fix. Change the file path in the `post_processing.conf` and run the command:
```
gnss-sdr --config_file=post_processing.conf 
```


### 4. Matters need attention
**(1) Error: loss of lock**
When you build everything greatly, you run the whole system, you may meet the general error: loss of lock. The root of the problem is that your SDR's internal oscillator with poor stability. This is ok for most wireless communication applications, but is not enough for GNSS signal processing. The solution is to use a high-quality oscillator. I use an extrenal `GPSDO`, and it works well. (https://github.com/gnss-sdr/gnss-sdr/issues/831#issuecomment-2543501391). For checking if the GPSDO works well, you can check https://github.com/gnss-sdr/gnss-sdr/issues/831#issuecomment-2547548441.

**(2) Electromagnetic interference**
To avoid the electromagnetic interference, keep the antenna away from the RF_front. According to a similar problem: https://github.com/muccc/iridium-toolkit/issues/120#issuecomment-2441802135.

**(3) Sample rate and gain setting**
About the parameters seting in the config file: the recommanded sampling rate is 4MHz:
```
GNSS-SDR.internal_fs_sps=4000000  
SignalSource.sampling_frequency=4000000
```
The Resampler is unnecessary, when the GNSS-SDR.internal_fs_sps = SignalSource.sampling_frequency!
GNSS-SDR.internal_fs_sps is the internal target sampling rate, which is sample rate you tell the software and it will
process your signal with this rate. If it is equals to your SignalSource.sampling_frequency, you don't need to resample.

About the Gain, if the gain is set to 70dB or bigger, which may be too high, resulting in signal supersaturation and signal distortion, which affects signal locking. You need to test to find a suitable gain but not only pursing the highest gain. After testing, I think the 55~58 are all good for my testbed.

**(4) Overflow error**
The sample rate is 4MSa/s for each RF source(I have 4 RF source, i.e. 4 ants), the data format is gr_complex(complex 32float for I and Q). As a result the total data generated is 4MSa/s * 4 ants * 4B * 2 = 128MB/s, which exceeds the communication bandwidth between PC with only 1Gbps Ethernet controller and USRP. 
```
1Gbps Ethernet controller: 1Gbps = 1000Mbps = 125MB/s < 128MB/s
10Gbps Ethernet controller: 10Gbps = 10000Mbps = 1250MB/s > 128MB/s
```
So, I use the 10Gbps Ethernet controller to solve this problem. Most the general laptops have only 1Gbps Ethernet controller, which is not enough for this application. So I recommand you can buy a USB4 to 10Gbps Ethernet controller. And make sure your laptop has a thunderbolt port!

### 5. Decoded files
Generally, gnss-sdr will output some decoded files, for example in above displayed figure:

| **File Name**                  | **Content Description**                                | **Note**                              |
|--------------------------------|-------------------------------------------------------|--------------------------------------------|
| `gps_ephemeris.xml`;<br>`GSDR362k49.24N`             | GPS satellite ephemeris data (orbital parameters, clock corrections). | `.xml` and `.xxn` are the same data with different format. <br>There are all satellite ephemeris data decoded from the received signal. <br>They just contain GPS satellite ephemeris data within the receiving period, which is different from the broadcast ephemeris file that you can download from https://cddis.nasa.gov/archive/gnss/data/daily/2024/brdc/|
| `GSDR362k49.240`         | RINEX file (v3.02) with observation data, navigation messages, receiver metadata. | Post-processing, accurate positioning, interoperability. <br>This RINEX file constains carrier phase, pseudo-range, Doppler frequency, and RSS data. you can check detailed information by: https://www.spatial.nsw.gov.au/__data/assets/pdf_file/0018/232452/2023_Janssen_Coordinates1911_understanding_the_RINEX_format.pdf or https://igs.org/formats-and-standards/|
| `nmea_pvt.nmea`                | NMEA-standard GNSS positioning data (time, coordinates, speed). | Real-time visualization, trajectory analysis. |
| `pvt.dat_241227_104907.geojson`| GeoJSON file with geolocation data (points, timestamps, metadata). | GIS visualization, geospatial analysis.   |
| `pvt.dat_241227_104907.gpx`    | GPX file with trajectory data (waypoints, routes, metadata). | Navigation, sharing with GPS devices/apps. <br>Create a new map in https://www.google.com/maps/d/u/0/ and import the `.gpx` file.|
| `pvt.dat_241227_104907.kml`    | KML file with trajectory data for Google Earth.       | 3D visualization, trajectory presentation. <br>Create a new map in https://www.google.com/maps/d/u/0/ and import the `.kml` file.|


## Reference
- GNSS-SDR: https://gnss-sdr.org/
- USRP X310: https://www.ettus.com/products/boards/usrp-x310 
