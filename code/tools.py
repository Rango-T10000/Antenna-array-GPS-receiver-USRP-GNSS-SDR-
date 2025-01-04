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
        elevation_angles = {}    
        azimuth_angles = {}     
        
        for line in group:
            if line.startswith('$GPGSV'):
                gsv_parts = line.split(',')
                # Process satellite info from GSV message
                for j in range(4, len(gsv_parts)-1, 4):
                    if j+3 < len(gsv_parts):
                        prn = gsv_parts[j]
                        if prn:
                            sat_id = f"G{prn}"
                            satellites.append(sat_id)
                            # Add ele, azi, rss
                            try:
                                elevation_angles[sat_id] = float(gsv_parts[j+1])
                                azimuth_angles[sat_id] = float(gsv_parts[j+2])
                                signal_strength[sat_id] = float(gsv_parts[j+3])
                            except (ValueError, IndexError):
                                continue
        
        # Build timestamp
        timestamp = datetime.strptime(f"{date_str}{time_str}", "%d%m%y%H%M%S.%f")
        
        return {
            'timestamp': timestamp,
            'lat': lat_dec,
            'lon': lon_dec,
            'alt': alt,
            'satellites': satellites,
            'signal_strength': signal_strength,
            'elevation_angles': elevation_angles,    
            'azimuth_angles': azimuth_angles        
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
    Find satellite data blocks before and after target time
    
    Args:
        broadcast_file: Path to broadcast ephemeris file
        target_time: Target timestamp
        target_prn: Target satellite PRN (e.g., 'G26')
    
    Returns:
        tuple: (before_epoch, before_block, after_epoch, after_block)
    """
    # Stores all ephemeris data for the PRN
    all_epochs = []
    all_blocks = []
    
    try:
        with open(broadcast_file, 'r') as f:
            # Skip header
            for line in f:
                if "END OF HEADER" in line:
                    break
            
            # Read and process the data
            line_count = 0
            current_block = []
            
            for line in f:
                if line[0] == 'G' and line[1:3].isdigit():
                    current_block = [line]
                    line_count = 1
                elif line_count > 0:
                    current_block.append(line)
                    line_count += 1
                    
                    if line_count == 8:
                        prn = current_block[0][0:3]
                        if prn == target_prn:
                            try:
                                first_line = current_block[0]
                                year = int(first_line[3:8])
                                month = int(first_line[9:11])
                                day = int(first_line[12:14])
                                hour = int(first_line[15:17])
                                minute = int(first_line[18:20])
                                second = int(first_line[21:23])
                                
                                epoch = datetime(year, month, day, hour, minute, second)
                                
                                # Collect data for all the PRN
                                all_epochs.append(epoch)
                                all_blocks.append(current_block.copy())
                                        
                            except ValueError as e:
                                print(f"Error parsing time for {prn}: {e}")
                        
                        line_count = 0
                        current_block = []
        
        # if find data
        if all_epochs:
            # sort according to time
            sorted_data = sorted(zip(all_epochs, all_blocks))
            all_epochs, all_blocks = zip(*sorted_data)
            
            # Find the position of the target time in the sorted time series
            for i in range(len(all_epochs)-1):
                if all_epochs[i] <= target_time < all_epochs[i+1]:
                    before_epoch = all_epochs[i]
                    before_block = all_blocks[i]
                    after_epoch = all_epochs[i+1]
                    after_block = all_blocks[i+1]
                    
                    print(f"Found bracketing epochs for {target_prn}:")
                    print(f"Before: {before_epoch} (diff: {(target_time - before_epoch).total_seconds()}s)")
                    print(f"After: {after_epoch} (diff: {(after_epoch - target_time).total_seconds()}s)")
                    
                    return before_epoch, before_block, after_epoch, after_block
    
    except FileNotFoundError:
        print(f"Error: Could not find broadcast file")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    
    print(f"Could not find bracketing epochs for {target_prn}")
    return None, None, None, None

def parse_broadcast_ephemeris(broadcast_file, target_time, available_sats):
    """
    Parse broadcast ephemeris file and find satellite positions using interpolation
    
    Args:
        broadcast_file: Path to broadcast ephemeris file
        target_time: Target timestamp (datetime object)
        available_sats: List of available satellite PRNs
    
    Returns:
        dict: Dictionary of satellite positions {PRN: {'x': x, 'y': y, 'z': z}}
    """
    satellite_data = {}
    
    try:
        print(f"Parsing broadcast file for time: {target_time}")
        print(f"Looking for satellites: {available_sats}")
        
        # Process each satellite
        for prn in available_sats:
            print(f"\nProcessing satellite {prn}")
            
            # Find bracketing ephemeris data（before and after target_time in ephemeris）
            before_epoch, before_block, after_epoch, after_block = find_satellite_data(broadcast_file, target_time, prn)
            
            if not all([before_epoch, before_block, after_epoch, after_block]):
                print(f"Could not find bracketing ephemeris data for {prn}")
                continue
                
            try:
                # Interpolate ephemeris data(before and after target_time) to get the ephemeris data at target_time
                interpolated_eph = interpolate_ephemeris(before_block, after_block, target_time)
                
                if interpolated_eph:
                    # Compute precise satellite position using Keplerian orbital parameters at the target_time
                    x, y, z = compute_satellite_position(interpolated_eph, target_time.timestamp())
                    
                    satellite_data[prn] = {
                        'x': x,
                        'y': y,
                        'z': z
                    }
                    print(f"Successfully computed position for {prn} at {target_time}")
                else:
                    print(f"Failed to interpolate ephemeris data for {prn}")
                    
            except Exception as e:
                print(f"Error processing satellite {prn}: {str(e)}")
                continue
    
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

def interpolate_ephemeris(before_block, after_block, target_time):
    """
    Interpolate ephemeris parameters for target time
    
    Args:
        before_block: Ephemeris data block before target time
        after_block: Ephemeris data block after target time
        target_time: Target timestamp
    
    Returns:
        dict: Interpolated ephemeris parameters
    """
    # Process ephemeris blocks into dict 
    before_eph = process_ephemeris_block(before_block)
    after_eph = process_ephemeris_block(after_block)
    
    # Convert time strings to datetime objects
    before_time = datetime(
        int(before_block[0][3:8]),
        int(before_block[0][9:11]),
        int(before_block[0][12:14]),
        int(before_block[0][15:17]),
        int(before_block[0][18:20]),
        int(before_block[0][21:23])
    )
    
    after_time = datetime(
        int(after_block[0][3:8]),
        int(after_block[0][9:11]),
        int(after_block[0][12:14]),
        int(after_block[0][15:17]),
        int(after_block[0][18:20]),
        int(after_block[0][21:23])
    )
    
    # Compute interpolation factor
    total_interval = (after_time - before_time).total_seconds()
    target_interval = (target_time - before_time).total_seconds()
    t = target_interval / total_interval
    
    # Interpolate ephemeris parameters
    interpolated_eph = {}
    for key in before_eph.keys():
        interpolated_eph[key] = before_eph[key] + (after_eph[key] - before_eph[key]) * t
    
    return interpolated_eph

def process_ephemeris_block(data_lines):
    """
    Parse ephemeris data block into dictionary
    
    Args:
        data_lines: List of 8 lines containing ephemeris data
    
    Returns:
        dict: Parsed ephemeris parameters
    """
    try:
        eph_data = {
            # Line 1: Clock parameters
            'clock_bias': float(data_lines[0][23:42]),      # -2.522906288505e-05
            'clock_drift': float(data_lines[0][42:61]),     # -1.455191522837e-11
            'clock_drift_rate': float(data_lines[0][61:80]), # 0.000000000000e+00
            
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
            
            # Line 6
            'idot': float(data_lines[5][0:23]),     # -3.396570052205e-10
        }
        
        return eph_data
        
    except (ValueError, IndexError) as e:
        print(f"Error processing ephemeris block: {str(e)}")
        return None

