#!/usr/bin/python
import sys
import os
import yaml
import requests

yamlname = sys.argv[1]
with open(yamlname) as f:
 js = yaml.safe_load(f)
jsonname=yamlname.split('.')[0] + '.json'

if ('kind' in js.keys()):
 pass
else:
 print ('kind is not spcified in yaml')
 sys.exit(31)

kind = js["kind"]

if (kind == "virtual-network"):
  name = js["name"]
  subnet = js["subnet"]
  prefix = js["prefix"]
  project = js["project"]
  
  json = """
  {"virtual-network":
   {
      "fq_name": [
          "default-domain",
          "%s",
          "%s"
      ],
      "network_ipam_refs": [
          {
              "attr": {
                  "ipam_subnets": [
                      {
                          "subnet": {
                              "ip_prefix": "%s",
                              "ip_prefix_len": %s
                          }
                      }
                  ]
              },
              "to": [
                  "default-domain",
                  "default-project",
                  "default-network-ipam"
              ]
          }
      ],
      "parent_type": "project"
   }
  }
  """ % (project, name, subnet, prefix)

with open (jsonname, 'w') as f:
 f.write (json)

## it's not the correct way to do so :(
controller_ip = os.popen ("ip -o route get 8.8.8.8 | awk '{print $7}'").read ().rstrip()

headers= {"Content-Type": "application/json", "charset": "UTF-8"}
r = requests.post ("http://{}:8082/{}s".format(controller_ip, kind), data=json, headers=headers)
print (r.text)
