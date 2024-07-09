#! /usr/bin/env python3

import yaml
import requests
from requests.auth import HTTPBasicAuth
import sys
import json
import os

host = os.environ['DNS_API_HOST_PREFIX']

auth = HTTPBasicAuth('admin', os.environ['DNS_API_PASS'])

headers = {}
headers['X-API-Key'] = os.environ['DNS_API_KEY']

with open('data.yml', 'r') as f:
    data = yaml.safe_load(f)

defaulttl = 3600
for z in data['zones']:

    if 'ttl' in z:
        zonettl = z['ttl']
    else:
        zonettl = defaulttl

    # Check if zone exists
    records = {}
    zone = requests.get('{}/api/v1/servers/localhost/zones/{}'.format(host, z['name']), headers=headers, auth=auth)

    if zone.status_code == 404:
        print('Zone {} does not exist. Creating'.format(z['name']))
        data = {}
        data['name'] = z['name']
        data['kind'] = 'native'
        zonecreation = requests.post('{}/api/v1/servers/localhost/zones'.format(host, z['name']), auth=auth, headers=headers, data=json.dumps(data))
        if zonecreation.status_code == 201:
            print('Zone created')
        else:
            print('Zone Creation failed.')
            sys.exit(1)

    else:
        # Getting all records from the zone for later testing.
        for r in zone.json()['rrsets']:
            records["{}_{}".format(r['name'], r['type'])] = {'content': [], 'ttl': r['ttl']}

            for k in r['records']:
                records["{}_{}".format(r['name'], r['type'])]['content'].append(k['content'])
    
          

    for r in z['records']:

        update = False
        delete = False
        if 'state' not in r or r['state'] != 'DELETE':
            newrecords = []

            ttl = zonettl
            if 'ttl' in r:
                ttl = r['ttl']


            if type(r['dest']) is list:
                for t in r['dest']:
                    newrecords.append({"content":  t,
                                       "disabled": False})
            else:
                newrecords.append({"content":  r['dest'], 
                                   "disabled": False})

            data = {"rrsets": [{"name": "{}".format(r['name']),
                                "type": r['type'],
                                "ttl": ttl,
                                "changetype": "REPLACE", 
                                "records": newrecords,
                                }]}
        else:
            delete = True
            data = {"rrsets": [{"name": "{}".format(r['name']),
                                "type": r['type'],
                                "changetype": "DELETE"
                                }]}

        # Determining if we actually have to change something.
        key    = '{}_{}'.format(r['name'], r['type'])
        if key not in records:
            if not delete:
                update = True
        else:
            if delete:
                update = True
            else:
                record = records[key]
                if type(r['dest']) is list:
                    if sorted(r['dest']) != sorted(record['content']) or record['ttl'] != ttl:
                        update = True
                else:
                    if not (r['dest'] == record['content'][0] and len(record['content']) == 1) or record['ttl'] != ttl:
                        update = True


        if update:
            print("Adding/Modifying record: {}".format(r['name']))
            rcreate = requests.patch('{}/api/v1/servers/localhost/zones/{}'.format(host, z['name']), auth=auth, headers=headers, data=json.dumps(data))
            print(rcreate.status_code)
            try:
                print(rcreate.json())
            except:
                pass
