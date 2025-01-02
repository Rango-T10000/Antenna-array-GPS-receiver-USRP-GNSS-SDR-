import csv
import math
import numpy as np
from datetime import datetime, timedelta

class RinexCache:
    """Cache for RINEX data to avoid multiple file reads"""
    def __init__(self):
        self.data = {}  # Format: {timestamp: {prn: (carrier_phase, rss)}}
        self.is_loaded = False

    def load_data(self, rinex_file):
        """Load RINEX data into cache"""
        rinex_data = parse_rinex_302(rinex_file)
        
        # Organize data by timestamp and PRN
        for prn, carrier_phase, rss, timestamp in rinex_data:
            if timestamp not in self.data:
                self.data[timestamp] = {}
            self.data[timestamp][prn] = (carrier_phase, rss)
        
        self.is_loaded = True

def parse_rinex_302(filename):
    """Parse RINEX 3.02 observation file"""
    data = []  # List to store all observations
    current_timestamp = None
    
    with open(filename) as f:
        # Skip header until data section
        for line in f:
            if "END OF HEADER" in line:
                break
        
        # Parse observation records
        for line in f:
            if line[0] == '>':  # New epoch/timestamp line
                current_timestamp = line[2:29].strip()
                continue
                
            # Parse satellite data line
            try:
                parts = line.split()  # Split line by whitespace
                if not parts:  # Skip empty lines
                    continue
                    
                prn = parts[0]  # First part is PRN
                
                # Extract L1C (carrier phase) - it's the fourth value
                l1c = float(parts[3])
                
                # Extract S1C (signal strength) - it's the last value
                s1c = float(parts[-1])
                
                # Store all values for this observation
                data.append([prn, l1c, s1c, current_timestamp])
                
            except (ValueError, IndexError) as e:
                print(f"Error processing line: {line.strip()} - {str(e)}")
                continue
    
    return data

def parse_nmea_data(nmea_file):
    """Parse NMEA file to extract timestamp, position and satellite information"""
    data_groups = []
    current_group = []
    current_timestamp = None
    
    with open(nmea_file, 'r') as f:
        lines = f.readlines()
        
    for line in lines:
        if not line.strip():
            continue
            
        try:
            # Start of a new group when we see RMC message
            if line.startswith('$GPRMC'):
                if current_group:
                    # Process previous group if exists
                    try:
                        parsed_data = process_nmea_group(current_group)
                        if parsed_data:
                            data_groups.append(parsed_data)
                    except (ValueError, IndexError) as e:
                        print(f"Error processing NMEA group: {e}")
                    
                # Start new group
                current_group = [line]
            else:
                # Add line to current group
                current_group.append(line)
                
        except (ValueError, IndexError) as e:
            print(f"Error parsing NMEA line: {e}")
            continue
            
    # Process last group
    if current_group:
        try:
            parsed_data = process_nmea_group(current_group)
            if parsed_data:
                data_groups.append(parsed_data)
        except (ValueError, IndexError) as e:
            print(f"Error processing final NMEA group: {e}")
            
    return data_groups

def process_nmea_group(group):
    """Process a group of NMEA messages that belong together"""
    if len(group) < 3:  # Need at least RMC, GGA and GSA
        return None
        
    try:
        # Parse RMC line for timestamp and validity
        rmc_parts = group[0].split(',')
        if len(rmc_parts) < 10 or rmc_parts[2] != 'A':
            return None
            
        time_str = rmc_parts[1]
        date_str = rmc_parts[9]
        
        # Parse GGA line for position
        gga_parts = group[1].split(',')
        if len(gga_parts) < 10:
            return None
            
        try:
            lat = float(gga_parts[2])
            lat_dir = gga_parts[3]
            lon = float(gga_parts[4])
            lon_dir = gga_parts[5]
            alt = float(gga_parts[9])
        except ValueError:
            return None
        
        # Convert coordinates
        lat_dec = convert_nmea_to_decimal(lat, lat_dir)
        lon_dec = convert_nmea_to_decimal(lon, lon_dir)
        
        # Process all GSV messages to get complete satellite info
        satellites = []
        signal_strength = {}
        
        for line in group:
            if line.startswith('$GPGSV'):
                gsv_parts = line.split(',')
                # Process satellite info from GSV message
                for j in range(4, len(gsv_parts)-1, 4):
                    if j+3 < len(gsv_parts):
                        prn = gsv_parts[j]
                        if prn:
                            satellites.append(f"G{prn}")
                            signal_strength[f"G{prn}"] = float(gsv_parts[j+3])
        
        # Build timestamp
        timestamp = datetime.strptime(f"{date_str}{time_str}", "%d%m%y%H%M%S.%f")
        
        return {
            'timestamp': timestamp,
            'lat': lat_dec,
            'lon': lon_dec,
            'alt': alt,
            'satellites': satellites,
            'signal_strength': signal_strength
        }
        
    except (ValueError, IndexError) as e:
        raise ValueError(f"Error processing NMEA group: {e}")

def convert_nmea_to_decimal(coord, direction):
    """Convert NMEA coordinate format to decimal degrees"""
    degrees = int(coord / 100)
    minutes = coord - degrees * 100
    decimal = degrees + minutes / 60
    
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

def lla_to_ecef(lat, lon, alt):
    """Convert LLA coordinates to ECEF coordinates"""
    # WGS84 ellipsoid parameters
    a = 6378137.0  # semi-major axis
    f = 1/298.257223563  # flattening
    b = a * (1 - f)  # semi-minor axis
    e = math.sqrt(1 - (b/a)**2)  # eccentricity
    
    # Convert to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    
    # Calculate radius of curvature in prime vertical
    N = a / math.sqrt(1 - e**2 * math.sin(lat_rad)**2)
    
    # Calculate ECEF coordinates
    x = (N + alt) * math.cos(lat_rad) * math.cos(lon_rad)
    y = (N + alt) * math.cos(lat_rad) * math.sin(lon_rad)
    z = (N * (1 - e**2) + alt) * math.sin(lat_rad)
    
    return x, y, z

def find_satellite_data(broadcast_file, target_time, target_prn):
    """
    Find satellite data for specific PRN and closest time
    
    Args:
        broadcast_file: Path to broadcast ephemeris file
        target_time: Target timestamp
        target_prn: Target satellite PRN (e.g., 'G26')
    """
    closest_epoch = None
    min_diff = 3600 # 1h
    satellite_block = None
    current_block = []
    
    try:
        with open(broadcast_file, 'r') as f:
            # Skip header
            for line in f:
                if "END OF HEADER" in line:
                    break
            
            # Read and process the data
            line_count = 0
            for line in f:
                if line[0] == 'G' and line[1:3].isdigit():
                    # Start of a new satellite block
                    current_block = [line]
                    line_count = 1
                elif line_count > 0:
                    # Continue collecting lines for current block
                    current_block.append(line)
                    line_count += 1
                    
                    # When we have collected 8 lines, process the block
                    if line_count == 8:
                        prn = current_block[0][0:3]
                        if prn == target_prn:  # Found matching PRN
                            try:
                                # 正确解析时间字段
                                first_line = current_block[0]
                                year = int(first_line[3:8])      
                                month = int(first_line[9:11])    
                                day = int(first_line[12:14])     
                                hour = int(first_line[15:17])    
                                minute = int(first_line[18:20])  
                                second = int(first_line[21:23])  
                                
                                epoch = datetime(year, month, day, hour, minute, second)
                                time_diff = abs((epoch - target_time).total_seconds())
                                
                                # print(f"Found {prn} data at {epoch}, time difference: {time_diff} seconds")
                                
                                if time_diff < min_diff:
                                    min_diff = time_diff
                                    closest_epoch = epoch
                                    satellite_block = current_block.copy()
                            except ValueError as e:
                                print(f"Error parsing time for {prn}: {e}")
                                print(f"Time string: {current_block[0][3:22]}")  # 打印出时间字符串以便调试
                        
                        # Reset for next block
                        line_count = 0
                        current_block = []
    
    except FileNotFoundError:
        print(f"Error: Could not find broadcast file")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None, None
    
    if satellite_block:
        print(f"Selected epoch {closest_epoch} for {target_prn} (time diff: {min_diff} seconds)")
    else:
        print(f"No data found for {target_prn}")
    
    return closest_epoch, satellite_block

def parse_broadcast_ephemeris(broadcast_file, target_time, available_sats):
    """
    Parse broadcast ephemeris file and find satellite positions
    
    Args:
        broadcast_file: Path to broadcast ephemeris file
        target_time: Target timestamp (datetime object)
        available_sats: List of available satellite PRNs
    """
    satellite_data = {}
    
    try:
        print(f"Parsing broadcast file for time: {target_time}")
        print(f"Looking for satellites: {available_sats}")
        
        # Process each satellite
        for prn in available_sats:
            print(f"\nProcessing satellite {prn}")
            closest_epoch, sat_block = find_satellite_data(broadcast_file, target_time, prn)
            
            if sat_block:
                print(f"Found data for {prn} at epoch {closest_epoch}")
                process_satellite_block(prn, sat_block, target_time, satellite_data)
            else:
                print(f"No data found for satellite {prn}")
    
    except Exception as e:
        print(f"Error parsing broadcast file: {str(e)}")
        return {}
    
    print(f"Found data for {len(satellite_data)} satellites")
    return satellite_data

def compute_satellite_position(eph_data, time):
    """
    Compute precise satellite position using Keplerian orbital parameters
    
    Parameters:
    eph_data: Dictionary containing ephemeris parameters
    time: GPS time for position calculation
    
    Returns:
    tuple: (x, y, z) ECEF coordinates in meters
    """
    # WGS-84 constants
    MU = 3.986005e14  # Earth's gravitational constant (m^3/s^2)
    OMEGA_E = 7.2921151467e-5  # Earth's rotation rate (rad/s)
    
    # Extract orbital parameters
    sqrt_a = eph_data['sqrt_a']
    e = eph_data['e']  # Eccentricity
    i0 = eph_data['i0']  # Inclination
    omega = eph_data['omega']  # Argument of perigee
    OMEGA0 = eph_data['OMEGA0']  # Right ascension
    M0 = eph_data['M0']  # Mean anomaly
    delta_n = eph_data['delta_n']  # Mean motion correction
    OMEGA_dot = eph_data['OMEGA_dot']  # Rate of right ascension
    i_dot = eph_data['idot']  # Rate of inclination
    Cuc = eph_data['Cuc']  # Correction terms
    Cus = eph_data['Cus']
    Crc = eph_data['Crc']
    Crs = eph_data['Crs']
    Cic = eph_data['Cic']
    Cis = eph_data['Cis']
    toe = eph_data['toe']  # Time of ephemeris
    
    # Time from ephemeris reference epoch
    dt = time - toe
    
    # Correct for week crossovers
    if dt > 302400:
        dt -= 604800
    elif dt < -302400:
        dt += 604800
    
    # Calculate mean motion
    a = sqrt_a * sqrt_a
    n0 = math.sqrt(MU / (a * a * a))
    n = n0 + delta_n
    
    # Mean anomaly
    M = M0 + n * dt
    
    # Solve Kepler's equation iteratively
    E = M
    for _ in range(8):
        E_new = M + e * math.sin(E)
        if abs(E_new - E) < 1e-12:
            break
        E = E_new
    
    # True anomaly
    nu = math.atan2(math.sqrt(1 - e*e) * math.sin(E), math.cos(E) - e)
    
    # Argument of latitude
    phi = nu + omega
    
    # Second harmonic perturbations
    du = Cuc * math.cos(2*phi) + Cus * math.sin(2*phi)  # Argument of latitude correction
    dr = Crc * math.cos(2*phi) + Crs * math.sin(2*phi)  # Radius correction
    di = Cic * math.cos(2*phi) + Cis * math.sin(2*phi)  # Inclination correction
    
    # Corrected argument of latitude
    u = phi + du
    
    # Corrected radius
    r = a * (1 - e * math.cos(E)) + dr
    
    # Corrected inclination
    i = i0 + di + i_dot * dt
    
    # Corrected longitude of ascending node
    OMEGA = OMEGA0 + (OMEGA_dot - OMEGA_E) * dt - OMEGA_E * toe
    
    # Positions in orbital plane
    x_prime = r * math.cos(u)
    y_prime = r * math.sin(u)
    
    # Earth-fixed coordinates
    x = x_prime * math.cos(OMEGA) - y_prime * math.cos(i) * math.sin(OMEGA)
    y = x_prime * math.sin(OMEGA) + y_prime * math.cos(i) * math.cos(OMEGA)
    z = y_prime * math.sin(i)
    
    return x, y, z

def process_satellite_block(prn, data_lines, target_time, satellite_data):
    """Process a complete satellite data block (8 lines) and compute precise position"""
    try:
        # Parse first line for epoch and clock data
        line1 = data_lines[0]
        year = int(line1[3:8])
        month = int(line1[9:11])
        day = int(line1[12:14])
        hour = int(line1[15:17])
        minute = int(line1[18:20])
        second = int(line1[21:23])
        
        epoch = datetime(year, month, day, hour, minute, second)
        
        # Parse orbital parameters according to the actual format
        eph_data = {
            'epoch': epoch,
            # Line 1: Clock parameters
            'clock_bias': float(line1[23:42]),      # -2.522906288505e-05
            'clock_drift': float(line1[42:61]),     # -1.455191522837e-11
            'clock_drift_rate': float(line1[61:80]), # 0.000000000000e+00
            
            # Line 2
            'IODE': float(data_lines[1][0:23]),     # 6.800000000000e+01
            'Crs': float(data_lines[1][23:42]),     # 2.596875000000e+01
            'delta_n': float(data_lines[1][42:61]),  # 5.071639825584e-09
            'M0': float(data_lines[1][61:80]),      # -1.701657829267e+00
            
            # Line 3
            'Cuc': float(data_lines[2][0:23]),      # 1.104548573494e-06
            'e': float(data_lines[2][23:42]),       # 9.773897123523e-03
            'Cus': float(data_lines[2][42:61]),     # 9.480863809586e-06
            'sqrt_a': float(data_lines[2][61:80]),  # 5.153752502441e+03
            
            # Line 4
            'toe': float(data_lines[3][0:23]),      # 5.183840000000e+05
            'Cic': float(data_lines[3][23:42]),     # 6.705522537231e-08
            'OMEGA0': float(data_lines[3][42:61]),  # 2.363421419612e+00
            'Cis': float(data_lines[3][61:80]),     # -1.359730958939e-07
            
            # Line 5
            'i0': float(data_lines[4][0:23]),       # 9.298234122031e-01
            'Crc': float(data_lines[4][23:42]),     # 1.748750000000e+02
            'omega': float(data_lines[4][42:61]),   # 5.995726430872e-01
            'OMEGA_dot': float(data_lines[4][61:80]),# -8.051049644248e-09
            
            # Line 6 (we might need some of these parameters later)
            'idot': float(data_lines[5][0:23]),     # -3.396570052205e-10
            'codes': float(data_lines[5][23:42]),   # 1.000000000000e+00
            'week': float(data_lines[5][42:61]),    # 2.346000000000e+03
            
            # Line 7 (additional parameters if needed)
            'accuracy': float(data_lines[6][0:23]),  # 2.000000000000e+00
            'health': float(data_lines[6][23:42]),  # 0.000000000000e+00
            'Tgd': float(data_lines[6][42:61]),     # 6.519258022308e-09
            'IODC': float(data_lines[6][61:80])     # 6.800000000000e+01
        }
        
        # Compute satellite position
        x, y, z = compute_satellite_position(eph_data, target_time.timestamp())
        
        satellite_data[prn] = {
            'epoch': epoch,
            'x': x,
            'y': y,
            'z': z
        }
        
        print(f"Successfully processed {prn} for epoch {epoch}")
        
    except (ValueError, IndexError) as e:
        print(f"Error processing satellite {prn}: {str(e)}")
        print("Data lines:")
        for i, line in enumerate(data_lines):
            print(f"Line {i+1}: {line.strip()}")
        return


def get_carrier_phase_rss(rinex_cache, timestamp, prn):
    """Get carrier phase and RSS for specific timestamp and PRN"""
    timestamp_str = timestamp.strftime("%Y %m %d %H %M %S.%f")
    
    if timestamp_str in rinex_cache.data.keys():
        if prn in rinex_cache.data[timestamp_str]:
            return rinex_cache.data[timestamp_str][prn]
    
    closest_time = min(rinex_cache.data.keys(), 
                      key=lambda x: abs(datetime.strptime(x[:-1], "%Y %m %d %H %M %S.%f") - timestamp))
    
    if prn in rinex_cache.data[closest_time]:
        return rinex_cache.data[closest_time][prn]
    
    return 0.0, 0.0

