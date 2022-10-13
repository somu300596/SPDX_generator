#!/bin/python3
import csv
import json
import argparse
import requests
import datetime
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Convert csv to json file')
parser.add_argument("-i","--iput", help="Path to a input csv file.")
parser.add_argument("-o","--oput", help="Path to output json file.")
args = parser.parse_args()

def csv_to_json(csvFilePath, jsonFilePath):
	jsonArray = []

	#read csv file
	with open(csvFilePath, encoding='utf-8') as csvf:
		#load csv file data using csv library's dictionary reader
		csvReader = csv.DictReader(csvf)

		#convert each csv row into python dict
		for row in csvReader:
			#add this python dict to json array
			jsonArray.append(row)

	#convert python jsonArray to JSON String and write to file
	with open(jsonFilePath, 'w', encoding='utf-8') as jsonf:
		jsonString = json.dumps(jsonArray, indent=4)
		jsonf.write(jsonString)

def spdx_format_json(jsonFilePath, spdx_json_file):

	spdx_dict= {}
	package_data = []
	file_data = []
	package_name_list = []

	with open(jsonFilePath, 'r') as f:

		data=json.load(f)
		for row in data:

			if row['ARCHITECTURE'] != "":

				# It is a package

				print("Extracting details for the package : ",row['NAME'])
				copyrightText_list=""
				URL=row['OSS_LINK']
				page = requests.get(f'{URL}')
				soup = BeautifulSoup(page.content, "lxml")
				for i in soup.get_text().split('\n'):
					if i.startswith("Copyright"):
						copyrightText_list += i + " "
				if row['OSS'] == "None" or row['OSS'] == "" :
					row['OSS'] = "NOASSERTION"
				else:
					licenseInfoFromFiles = row['OSS'].replace(',','","')

				if row['BASENAME'] not in package_name_list:

					package_data.append({"SPDXID": "SPDXRef-" + row['BASENAME'],
					"name": row['BASENAME'],
					"licenseInfoFromFiles": [licenseInfoFromFiles],
					"licenseConcluded": row['OSS'].replace(", ", " AND "),
					"licenseDeclared": row['OSS'].replace(", ", " AND "),
					"checksums": [{"algorithm": "SHA512", "checksumValue": row['DIGESTSHA512HEX']}],
					"packageVerificationCode": {
						"packageVerificationCodeExcludedFiles" : [],
						"packageVerificationCodeValue" : ""
					},
					"copyrightText":copyrightText_list,
					"downloadLocation":row['PACKAGE'],
					"supplier":"Organization: " + row['PRODUCT'],
					"versionInfo":row['PACKAGEINVERSION'],
					"hasFiles": []})

					package_name_list.append(row['BASENAME'])

			else:

				# It is a file

				print("Extracting details for the file : ",row['NAME'])

				file_data.append({"SPDXID": "SPDXRef-" + row['BASENAME'],
				"fileName": row['NAME'],
				"checksums": [{"algorithm": "SHA512", "checksumValue": row['DIGESTSHA512HEX']}],
				"licenseConcluded": "NOASSERTION",
				"licenseInfoFromFiles": [""],
				"copyrightText":""
				})

	# Adding some static information
	spdx_dict['SPDXID'] = "SPDXRef-DOCUMENT"
	spdx_dict['spdxVersion'] = "SPDX-2.2"
	spdx_dict['dataLicense'] = "CC0-1.0"

	# Name of the SPDX file
	spdx_dict['name'] = "SPDX-QNX-target"

	# Document URI
	spdx_dict['documentNamespace'] = " "
	spdx_dict['documentDescribes'] = "SPDXRef-" + package_name_list[0],

	# Time when it is created
	spdx_dict['creationInfo'] = {
		"creators": ["Organization: ESMP"],
		"created": datetime.datetime.utcnow().isoformat() + "Z"
	}

	spdx_dict['packages'] = package_data
	spdx_dict['files'] = file_data


	#convert python jsonArray to JSON String and write to file
	with open(spdx_json_file, 'w', encoding='utf-8') as jsonf:
		jsonString = json.dumps(spdx_dict, indent=4)
		jsonf.write(jsonString.replace('\\",\\" ','","'))


# Gather arguments
csvFilePath = args.iput
spdx_json_file = args.oput

#Convert csv to json
jsonFilePath = "intermediate.json"
csv_to_json(csvFilePath, jsonFilePath)

#Convert to to SPDX format
spdx_format_json(jsonFilePath, spdx_json_file)