#!/bin/python3
import csv
import json
import argparse
import requests
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

	op_data = []

	with open(jsonFilePath, 'r') as f:

		data=json.load(f)
		for row in data:

			if row['ARCHITECTURE'] != "":

				copyrightText_list=[]
				URL=row['OSS_LINK']
				page = requests.get(f'{URL}')
				soup = BeautifulSoup(page.content, "lxml")
				for i in soup.get_text().split('\n'):
					if i.startswith("Copyright"):
						copyrightText_list.append(i)

				op_data.append({"packageFileName": row['BASENAME'],
				"attributionTexts": [row['OSS']],
				"checksums": [{"algorithm": "SHA512", "checksumValue": row['DIGESTSHA512']}],
				"copyrightText":copyrightText_list,
				"downloadLocation":row['PACKAGE'],
				"supplier":row['PRODUCT'],
				"versioninfo":row['PACKAGEINVERSION']})

	#convert python jsonArray to JSON String and write to file
	with open(spdx_json_file, 'w', encoding='utf-8') as jsonf:
		jsonString = json.dumps(op_data, indent=4)
		jsonf.write(jsonString)


# Gather arguments
csvFilePath = args.iput
spdx_json_file = args.oput

#Convert csv to json
jsonFilePath = "intermediate.json"
csv_to_json(csvFilePath, jsonFilePath)

#Convert to to SPDX format
spdx_format_json(jsonFilePath, spdx_json_file)