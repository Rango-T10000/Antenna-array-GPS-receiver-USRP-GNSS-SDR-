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
| `pvt.dat_241227_104907.kml`    | KML file with trajectory data for Google Earth.       | 3D visualization, trajectory presentation. <br>Create a new map in https://www.google.com/maps/d/u/0/ and import the `.kml` file. <br>And also, you can import the `.kml` file in https://www.google.com/earth/about/versions/#earth-for-web for 3D visualization.|



### 6. Extract information from decoded files
I provide the code for extracting information from the decoded files, including `.nema` file, `.xxo` file, and `.rnx` file download from the Internet. Using this code, you can extract the following information recorded in the `csv` files like the examples in the folder `./code/data/ant0.csv` :
```
Timestamp,Rx_X,Rx_Y,Rx_Z,PRN,Sat_X,Sat_Y,Sat_Z,Elevation,Azimuth,Carrier_Phase(cycles),RSS(dBHz)
2024-12-27 02:43:48.390000,-2418189.139113585,5385823.559379437,2405652.2286304315,G26,-17471192.10001667,19679063.951060183,952052.2374084838,69.0,240.0,128088169.369,42.692
2024-12-27 02:43:48.390000,-2418189.139113585,5385823.559379437,2405652.2286304315,G28,8116807.666167371,-25155650.334401198,-2654593.203265004,47.0,10.0,135533226.424,41.392
2024-12-27 02:43:48.390000,-2418189.139113585,5385823.559379437,2405652.2286304315,G29,22033026.332381085,9673379.434590535,11064110.709128043,22.0,79.0,146178780.326,41.885
2024-12-27 02:43:48.390000,-2418189.139113585,5385823.559379437,2405652.2286304315,G32,15340710.572897878,19983728.84202612,8933294.964710569,60.0,90.0,131743103.517,44.892
2024-12-27 02:43:48.490000,-2418191.1087058643,5385818.364426423,2405653.4754515854,G26,-17471242.922931515,19679012.983145047,952140.3493899454,69.0,240.0,128088169.369,42.692
2024-12-27 02:43:48.490000,-2418191.1087058643,5385818.364426423,2405653.4754515854,G28,8116994.357508367,-25155562.527996276,-2654856.4888132513,47.0,10.0,135533226.424,41.392
2024-12-27 02:43:48.490000,-2418191.1087058643,5385818.364426423,2405653.4754515854,G29,22033206.028190624,9673365.088513652,11063765.570014128,22.0,79.0,146178780.326,41.885
2024-12-27 02:43:48.490000,-2418191.1087058643,5385818.364426423,2405653.4754515854,G32,15340915.738580769,19983360.801088165,8933773.831885163,60.0,90.0,131743103.517,44.892
2024-12-27 02:43:48.590000,-2418197.3144785874,5385825.825604284,2405664.283551862,G26,-17471293.743363842,19678962.01692558,952228.459365025,69.0,240.0,128088169.369,42.692
2024-12-27 02:43:48.590000,-2418197.3144785874,5385825.825604284,2405664.283551862,G28,8117181.050688698,-25155474.716655854,-2655119.7733534994,47.0,10.0,135533226.424,41.392
2024-12-27 02:43:48.590000,-2418197.3144785874,5385825.825604284,2405664.283551862,G29,22033385.718153264,9673350.7373472,11063420.43332684,22.0,79.0,146178780.326,41.885
```

Each line in above extracted data includes:
- Timestamp of the received signal (UTC)
- Receiver position (Rx_X, Rx_Y, Rx_Z); ECEF coordinates; Unit: m
- Satellite position (Sat_X, Sat_Y, Sat_Z); ECEF coordinates; Unit: m
- Satellite PRN (ID)
- Elevation and Azimuth
- Carrier phase (cycles)
- Received signal strength, RSS (dBHz)
  
**(1) How to use ?**
I provide examples in `./12_27_4_ants` folder, which are the decoded files by using the gnss-sdr to process the received raw data in 2024/12/27. The folders include 4 folders from 4 different antennas in the array.  Find the `code/main.py`,change the file path and run this script. You will get the generated `.csv` file in the path you just set.

In the `./12_27_4_ants` folder, `12_27_4_ants/BRDM00DLR_S_20243620000_01D_MN.rnx` file is the broadcast ephemeris files download from https://cddis.nasa.gov/archive/gnss/data/daily/2024/brdc/. 


**(2) Code explanation**
- **About decoded ephemeris files:** In fact, the decoded files include the ephemeris file decoded from the received signal, i.e. `gps_ephemeris.xml; GSDR362k49.24N` in my example. However, if check these ephemeris file, you will find that it only shows the ephemeris data in a timestamp. For example, `.nema` file shows your position at `2024-12-27 02:43:48.590000`, but the ephemeris file only shows the ephemeris data at `2024 12 27 04 00 00`. So, I need to use the broadcast ephemeris file to get the ephemeris data at the timestamp of the `.nema` file. The broadcast ephemeris file download from the Internet show the complete ephemeris data for the whole day. 
- **About broadcast ephemeris files:** For example, to compute the satellite position at  `2024-12-27 02:43:48.590000`, I need to find the broadcast ephemeris file including close time epoch with the target time and download it. In my example, the broadcast ephemeris file is `BRDM00DLR_S_20243620000_01D_MN.rnx`. Because the broadcast ephemeris file records the ephemeris data at intervals of every two hours. For example:
```
G26 2024 12 27 01 59 44-2.407375723124e-05-1.455191522837e-11 0.000000000000e+00
     7.400000000000e+01 4.884375000000e+01 5.061996566761e-09-6.864365990568e-01
     2.671033143997e-06 9.770426666364e-03 9.756535291672e-06 5.153752902985e+03
     4.391840000000e+05 1.303851604462e-07 2.364065943281e+00 9.872019290924e-08
     9.298577293354e-01 1.724062500000e+02 5.992290138708e-01-8.270344493045e-09
    -3.082271246112e-10 1.000000000000e+00 2.346000000000e+03 0.000000000000e+00
     2.000000000000e+00 0.000000000000e+00 6.519258022308e-09 7.400000000000e+01
     4.320180000000e+05 4.000000000000e+00                                      
G26 2024 12 27 04 00 00-2.417853102088e-05-1.455191522837e-11 0.000000000000e+00
     7.700000000000e+01 5.025000000000e+01 4.990565019922e-09 3.660794088596e-01
     2.713873982430e-06 9.771208977327e-03 9.486451745033e-06 5.153754528046e+03
     4.464000000000e+05 2.235174179077e-08 2.364006504920e+00 1.862645149231e-07
     9.298555174032e-01 1.799375000000e+02 5.991817425989e-01-8.233200088688e-09
    -3.553719455251e-10 1.000000000000e+00 2.346000000000e+03 0.000000000000e+00
     2.000000000000e+00 0.000000000000e+00 6.519258022308e-09 7.700000000000e+01
     4.392180000000e+05 4.000000000000e+00                                      
```
To compute the satellite `G26`'s position at `2024-12-27 02:43:48.590000`, I use linear interpolation to generate the ephemeris data at `2024-12-27 02:43:48.590000` from the ephemeris data at `2024-12-27 01:59:44` and `2024-12-27 04:00:00`. Then, I can use it to compute the satellite position at `2024-12-27 02:43:48.590000`.

- **About the corrdinate:** Both the receiver position and satellite position are provoded in the Earth-centered, Earth-fixed coordinate system (ECEF coordinates). Receiver position is computed by converting the receiver `latitude, longitude, and altitude` to ECEF coordinates. Satellite position is computed by  broadcast ephemeris file to ECEF coordinates.

## Reference
- GNSS-SDR: https://gnss-sdr.org/
- USRP X310: https://www.ettus.com/products/boards/usrp-x310 
- Calculation of Satellite Position from Ephemeris Data: https://ascelibrary.org/doi/pdf/10.1061/9780784411506.ap03
- Broadcast ephemeris data: https://cddis.nasa.gov/archive/gnss/data/daily/2024/brdc/
- TLE data for GPS: https://celestrak.org/GPS/
- GPS Outage: https://gpsoutage.com/gpsoutages/
- sgp packet: https://pypi.org/project/sgp4/
- skyfield packet: https://rhodesmill.org/skyfield/