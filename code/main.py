from tools import parse_nmea_data
from tools import parse_broadcast_ephemeris
from tools import get_carrier_phase_rss
from tools import RinexCache
from tools import lla_to_ecef
import csv
import numpy as np



def main():
    # File paths
    nmea_file = "/Users/wangzhicheng/Desktop/gnss-sdr/12_27_4_ants/12_27_ant3/nmea_pvt.nmea"
    broadcast_file = "/Users/wangzhicheng/Desktop/gnss-sdr/12_27_4_ants/BRDM00DLR_S_20243620000_01D_MN.rnx"
    rinex_obs_file = "/Users/wangzhicheng/Desktop/gnss-sdr/12_27_4_ants/12_27_ant3/GSDR362l10.24O"
    output_file = "/Users/wangzhicheng/Desktop/gnss-sdr/code/data/ant3.csv"
    
    # Initialize RINEX cache
    print("Loading RINEX observation data...")
    rinex_cache = RinexCache()
    rinex_cache.load_data(rinex_obs_file)
    
    # Parse NMEA data
    print("Parsing NMEA data...")
    nmea_data = parse_nmea_data(nmea_file)
    print(f"Found {len(nmea_data)} NMEA data groups")
    
    # Prepare CSV file
    header = ['Timestamp', 'Rx_X', 'Rx_Y', 'Rx_Z', 'PRN', 'Sat_X', 'Sat_Y', 'Sat_Z', 'Carrier_Phase((cycles)', 'RSS((dBHz)']
    
    print("Processing data and writing to CSV...")
    rows_written = 0
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        for data_idx, data in enumerate(nmea_data):
            print(f"\nProcessing NMEA group {data_idx + 1}/{len(nmea_data)}")
            print(f"Timestamp: {data['timestamp']}")
            print(f"Available satellites: {data['satellites']}")
            
            # Convert receiver position to ECEF
            rx_x, rx_y, rx_z = lla_to_ecef(data['lat'], data['lon'], data['alt'])
            
            # Get satellite positions - pass both timestamp and available satellites
            sat_positions = parse_broadcast_ephemeris(broadcast_file, data['timestamp'], data['satellites'])
            
            # Process each satellite
            for prn in data['satellites']:
                if prn in sat_positions:
                    sat_pos = sat_positions[prn]
                    carrier_phase, rss = get_carrier_phase_rss(rinex_cache, data['timestamp'], prn)
                    
                    # Write data row
                    writer.writerow([
                        data['timestamp'].strftime('%Y-%m-%d %H:%M:%S.%f'),
                        rx_x, rx_y, rx_z,
                        prn,
                        sat_pos['x'], sat_pos['y'], sat_pos['z'],
                        carrier_phase,
                        rss
                    ])
                    rows_written += 1
                else:
                    print(f"No position data found for satellite {prn}")
    
    print(f"\nData processing complete. Wrote {rows_written} rows to {output_file}")

if __name__ == "__main__":
    main()