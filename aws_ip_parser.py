from flask import Flask, flash, redirect, render_template, request, session, abort
import urllib.request
import json

app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def awsIPParser():
    # URL to be targeted
    url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

    # Fetch the response from the URL
    response = urllib.request.urlopen(url)

    # Load the response as JSON
    data = json.loads(response.read())

    # Build the list of regions
    regions = fetchRegions(data)

    # Build the list of services
    services = fetchServices(data)

    if request.method == 'GET':
        # Render the main page
        return render_template('aws-ip-parser.html', regions=regions, services=services)
    elif request.method == 'POST':
        # Arguments to send to method
        selected_prefixes = str(request.form.getlist('prefix_filter'))
        selected_regions = str(request.form.getlist('region_filter'))
        selected_services = str(request.form.getlist('service_filter'))

        # Build the list of IPs
        result = retrieveIPInfo(selected_prefixes, selected_regions, selected_services, data)

        # Count prefixes in list
        count = len(result)

        # Render the page with the results
        return render_template('aws-ip-parser.html', selected_prefixes=selected_prefixes, selected_regions=selected_regions, selected_services=selected_services, regions=regions, services=services, result=result, count=count)

def retrieveIPInfo (prefixes, regions, services, json_data):
    # Dictionary to store initial data
    ip_list = {}

    # Integer for the dict key
    key = 0

    # Add IPv4 prefixes to list
    if "ipv4" in prefixes or "both" in prefixes:
        for i in json_data["prefixes"]:
            # If all regions and services are selected
            if "all" in regions and "all" in services:
                ip_list[key] = {"ip_prefix" : i["ip_prefix"], "region" : i["region"], "service" : i["service"]}
                key += 1
            # If all regions and some services are selected
            if "all" in regions and "all" not in services:
                if i["service"] in services:
                    ip_list[key] = {"ip_prefix" : i["ip_prefix"], "region" : i["region"], "service" : i["service"]}
                    key += 1
            # If some regions and some services are selected
            if "all" not in regions and "all" not in services:
                if i["region"] in regions and i["service"] in services:
                    ip_list[key] = {"ip_prefix" : i["ip_prefix"], "region" : i["region"], "service" : i["service"]}
                    key += 1
            # If some regions and all services are selected
            if "all" not in regions and "all" in services:
                if i["region"] in regions:
                    ip_list[key] = {"ip_prefix" : i["ip_prefix"], "region" : i["region"], "service" : i["service"]}
                    key += 1
    
    # Add IPv6 prefixes to list
    if "ipv6" in prefixes or "both" in prefixes:
        for i in json_data["ipv6_prefixes"]:
            # If all regions and services are selected
            if "all" in regions and "all" in services:
                ip_list[key] = {"ip_prefix" : i["ipv6_prefix"], "region" : i["region"], "service" : i["service"]}
                key += 1
            # If all regions and some services are selected
            if "all" in regions and "all" not in services:
                if i["service"] in services:
                    ip_list[key] = {"ip_prefix" : i["ipv6_prefix"], "region" : i["region"], "service" : i["service"]}
                    key += 1
            # If some regions and some services are selected
            if "all" not in regions and "all" not in services:
                if i["region"] in regions and i["service"] in services:
                    ip_list[key] = {"ip_prefix" : i["ipv6_prefix"], "region" : i["region"], "service" : i["service"]}
                    key += 1
            # If some regions and all services are selected
            if "all" not in regions and "all" in services:
                if i["region"] in regions:
                    ip_list[key] = {"ip_prefix" : i["ipv6_prefix"], "region" : i["region"], "service" : i["service"]}
                    key += 1

    # Deduplicate dictionary
    deduped_ip_list = {}
    for key,value in ip_list.items():
        if value not in deduped_ip_list.values():
            deduped_ip_list[key] = value

    # Return deduplicated IP list
    return deduped_ip_list

def fetchRegions(json_data):
    # Build Region List
    region_list = []
    for d in json_data["prefixes"]:
        if d not in region_list:
            region_list.append(d["region"])

    for d in json_data["ipv6_prefixes"]:
        if d not in region_list:
            region_list.append(d["region"])

    # Deduplicate list of regions
    deduped_region_list = []
    for r in region_list:
        if r not in deduped_region_list:
            deduped_region_list.append(r)

    return sorted(deduped_region_list)

def fetchServices(json_data):
    # Build service list
    service_list = []
    for e in json_data["prefixes"]:
        if e not in service_list:
            service_list.append(e["service"])

    for e in json_data["ipv6_prefixes"]:
        if e not in service_list:
            service_list.append(e["service"])

    # Deduplicate list of regions
    deduped_service_list = []
    for s in service_list:
        if s not in deduped_service_list:
            deduped_service_list.append(s)

    return sorted(deduped_service_list)

# If application is being called directly
if __name__ == '__main__':
    # URL to be targeted
    #url = "https://ip-ranges.amazonaws.com/ip-ranges.json"

    # Fetch the response from the URL
    #response = urllib.request.urlopen(url)

    # Load the response as JSON
    #data = json.loads(response.read())
    #test = retrieveIPInfo("both", "all", "all", data)
    #print(test)
    app.run(debug = True)