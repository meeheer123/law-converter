import pandas as pd
import re

# Load the main data CSV file
file_path = 'cleaned_table_data.csv'
data = pd.read_csv(file_path, header=None, names=['BNS', 'IPC'])

# Load the BNS content CSV file
bns_content_path = 'section_data.csv'  # Make sure this file is in the same directory or provide the correct path
bns_content_data = pd.read_csv(bns_content_path)

# Remove rows with NaN values in the columns we're interested in
data = data.dropna(subset=['BNS', 'IPC'])

def find_corresponding_section(data, bns_content_data, code_type, section_number):
    if code_type.lower() == 'ipc to bns':
        # Find rows where IPC starts with the section number
        corresponding_rows = data[data['IPC'].str.startswith(str(section_number) + '.')]

        if not corresponding_rows.empty:
            bns_section = corresponding_rows['BNS'].values[0]

            # Handle <para> tags in bns_section
            if '<para>' in bns_section:
                sec_nums = bns_section.split('<para>')
                sec_nums = [re.findall(r'\d+\(?\d*\)?', section) for section in sec_nums]
                print(sec_nums)

            # Extract the section number
            sec_match = re.match(r'\d+', bns_section)
            if sec_match is None:
                return f"This section has been deleted"
            else:
                sec = sec_match.group(0)

            # Find the corresponding row in bns_content_data
            bns_content_row = bns_content_data[bns_content_data['Section'] == int(sec)]
            if not bns_content_row.empty:
                bns_content = bns_content_row['Content'].values[0]
            else:
                bns_content = "No content available for this BNS section."
            return f"{bns_section}", bns_content
        else:
            # Handle specific cases
            if section_number in ['228A (3)', '376(3)']:
                corresponding_row = data[data['IPC'].str.startswith(str(section_number))]
                if not corresponding_row.empty:
                    bns_section = corresponding_row['BNS'].values[0]
                    sec_match = re.match(r'\d+', bns_section)
                    if sec_match:
                        sec = sec_match.group(0)
                        bns_content_row = bns_content_data[bns_content_data['Section'] == int(sec)]
                        if not bns_content_row.empty:
                            bns_content = bns_content_row['Content'].values[0]
                        else:
                            bns_content = "No content available for this BNS section."
                        return f"{bns_section}", bns_content
            return f"No corresponding BNS section found for IPC section {section_number}.", None

    elif code_type.lower() == 'bns to ipc':
        corresponding_row = data[data['BNS'].str.startswith(str(section_number))]
        if not corresponding_row.empty:
            ipc_section = corresponding_row['IPC'].values[0]
            sec = re.match(r'\d+', section_number).group(0)
            bns_content_row = bns_content_data[bns_content_data['Section'] == int(sec)]
            if not bns_content_row.empty:
                bns_content = bns_content_row['Content'].values[0]
            else:
                bns_content = "No content available for this BNS section."
            return f"{ipc_section}", bns_content
        else:
            return f"No corresponding IPC section found for BNS section {section_number}.", None
    else:
        return "Invalid option selected. Please choose either 'ipc to bns' or 'bns to ipc'.", None

# Test the output for each IPC section
ipc_sections = data['IPC'].unique()
results = []

for ipc in ipc_sections:
    section = str(ipc.split(' ')[0])[:-1]
    print(section)
    result = find_corresponding_section(data, bns_content_data, 'ipc to bns', section)
    results.append((section, result))
# Print the results
with open('output.txt', 'w') as file:
    for ipc, result in results:
        file.write(f"{ipc}, Result: {result}\n")