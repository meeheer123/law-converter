from flask import Flask, request, render_template, jsonify
import pandas as pd
import re

app = Flask(__name__)

# Load the main data CSV file
file_path = 'cleaned_table_data.csv'
data = pd.read_csv(file_path, header=None, names=['BNS', 'IPC'])

# Load the BNS content CSV file
bns_content_path = 'section_data.csv'
bns_content_data = pd.read_csv(bns_content_path)

# Remove rows with NaN values in the columns we're interested in
data = data.dropna(subset=['BNS', 'IPC'])
special_cases = [
    '178 (5)', '246', '248', '179', '237', '238', '239', '240', '241', '250', '251', '254',
    '258', '260', '489B', '180', '242', '243', '252', '253', '259', '489C', '181', '233',
    '234', '235', '256', '257', '489D', '231', '255', '489A'
]

def find_corresponding_section(data, bns_content_data, code_type, section_number):
    if code_type.lower() == 'ipc to bns':
        if section_number in special_cases:
            if section_number in ['246', '248']:
                bns_content_row = bns_content_data[bns_content_data['Section'] == 246]
                bns_content = bns_content_row['Content'].values[0]
                return f"178 (5)", bns_content
            elif section_number in ['237', '238', '239', '240', '241', '250', '251', '254', '258', '260', '489B']:
                bns_content_row = bns_content_data[bns_content_data['Section'] == 237]
                bns_content = bns_content_row['Content'].values[0]
                return f"179", bns_content
            elif section_number in ['242', '243', '252', '253', '259', '489C']:
                bns_content_row = bns_content_data[bns_content_data['Section'] == 242]
                bns_content = bns_content_row['Content'].values[0]
                return f"180", bns_content
            elif section_number in ['233', '234', '235', '256', '257', '489D']:
                bns_content_row = bns_content_data[bns_content_data['Section'] == 233]
                bns_content = bns_content_row['Content'].values[0]
                return f"181", bns_content
        # Handle specific cases first
        if section_number == '416':
            bns_content_row = bns_content_data[bns_content_data['Section'] == 319]
            bns_content = bns_content_row['Content'].values[0]
            return f"319(1)", bns_content
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

        # main code part
        # Find rows where IPC starts with the section number
        corresponding_rows = data[data['IPC'].str.startswith(str(section_number) + '.')]
        if not corresponding_rows.empty:
            bns_section = corresponding_rows['BNS'].values[0]
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

@app.route('/', methods=["GET", "POST"])
def home():
    if request.method == "POST":
        code_type = request.form['code_type'].strip()
        section_number = request.form['section'].strip()
        content = find_corresponding_section(data, bns_content_data, code_type, section_number)
        if content == 'This section has been deleted':
            return render_template("index.html", response=content)
        else:
            result, bns_content = content
        response = {'result': result}
        if bns_content:
            response['bns_content'] = bns_content
        return render_template("index.html", response=response)
    else:
        return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
