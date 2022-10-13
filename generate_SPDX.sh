#!/bin/bash

usage="$(basename "$0") [-i] [-c] [-j]

where:
    -i  input path of manifest file. It is the file generated from qscan tool
    -c  output path where the manifest file is converted to CSV format
    -j  output path of the resulting SPDX file"

while getopts ":i:c:j:" opt; do
  case "$opt" in
    i) manifest_file=$OPTARG ;;
    c) manifest_report_csv=$OPTARG ;;
    j) SPDX_file=$OPTARG ;;
    *) echo "$usage"
       exit
       ;;
  esac
done

# First find the location of qnxsoftwarecentre_clt script
qsc_clt_list=$(find ~ -name qnxsoftwarecenter_clt)
if [ -z "$qsc_clt_list" ]
then
    echo "Please Install QNX SOftware centre :( "
fi

# Grab the first found location of qnxsoftwarecenter CLI
qsc_clt=$(echo ${qsc_clt_list} | awk '{print $1}')

# Generate report using the qnxsoftwarecenter_clt utility.
/${qsc_clt} -reportImportQScan "${manifest_file}" > "${manifest_report_csv}"

# Covert the manifest report csv to json
./report_csv_to_json.py -i "${manifest_report_csv}" -o "${SPDX_file}"
