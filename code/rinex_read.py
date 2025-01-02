def parse_rinex_302(filename, output_csv):
    # Initialize data structures
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
    
    print(f"Total data points collected: {len(data)}")
    
    # Write to CSV with headers
    import csv
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header with units
        writer.writerow([
            'PRN',              # Satellite PRN code
            'Carrier_Phase_L1C (cycles)', # L1C carrier phase measurement
            'Signal_Strength_S1C (dBHz)', # S1C signal strength
            'Timestamp (YYYY MM DD HH MM SS.SSSSSSS)'  # Observation time
        ])
        # Write data
        writer.writerows(data)
    
    return data

if __name__ == '__main__':
    filename = '/Users/wangzhicheng/Desktop/gnss-sdr/12_27_4_ants/12_27_ant0/GSDR362k49.24O'
    output_csv = './code/data/rinex_302_output.csv'
    parse_rinex_302(filename, output_csv)