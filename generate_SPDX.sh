#!/bin/bash

while getopts ":i:c:j:" opt; do
  case "$opt" in
    i) manifest_file=$OPTARG ;;
    c) manifest_report_csv=$OPTARG ;;
    j) manifest_report_json=$OPTARG ;;
  esac
done

# First find the location of qnxsoftwarecentre_clt script

qsc_clt_list=$(find ~ -name qnxsoftwarecenter_clt)
# Grab the first found location of qnxsoftwarecenter CLI
qsc_clt=$(echo ${qsc_clt_list} | awk '{print $1}')

# Generate report using the qnxsoftwarecenter_clt utility.
/${qsc_clt} -reportImportQScan "${manifest_file}" > "${manifest_report_csv}"

# Covert the manifest report csv to json
./report_csv_to_json.py -i "${manifest_report_csv}" -o "${manifest_report_json}"
