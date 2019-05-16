#!/usr/bin/python
import sys
import os
import json
import yaml
import requests

def usage():
 print ("Usage: ./tungctl.py create -f xxx.yaml")

if (not len(sys.argv)==4):
 usage()
 sys.exit(30)

yamlname = sys.argv[3]
with open(yamlname) as f:
 js = yaml.safe_load(f)
jsonname=yamlname.split('.')[0] + '.json'

if ('kind' in js.keys()):
 pass
else:
 print ('kind is not spcified in yaml')
 sys.exit(31)

if (not sys.argv[1]=='create' or not sys.argv[2]=='-f'):
 sys.exit(32)

kind = js["kind"]

if (kind == "virtual-network"):
  name = js["name"]
  subnet = js["subnet"]
  prefix = js["prefix"]
  project = js["project"]
  
  jsonstring = """
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

  jsondict = json.loads(jsonstring)
  if ("gatewayless" in js.keys()):
    jsondict["virtual-network"]["virtual_network_refs"]=[{"to": ["default-domain", "default-project", "ip-fabric"]}]
  if ("route-target-list" in js.keys()):
    jsondict["virtual-network"]["route_target_list"]={"route_target": js["route-target-list"]}
  if ("external" in js.keys()):
    jsondict["virtual-network"]["router_external"]=True
  if ("network_policy_refs" in js.keys()):
    jsondict["virtual-network"]["network_policy_refs"]=[{"attr":{}, "to": policy_fqname.split(":")} for policy_fqname in js["network_policy_refs"]]
elif (kind == "network-policy"):
  name=js["name"]
  project=js["project"]
  np_rule=js["network_policy_rule"]
  action=np_rule["action"]
  src_addr=np_rule["src_addresses"]
  dst_addr=np_rule["dst_addresses"]
  protocol=np_rule["protocol"]
  jsonstring = """
    {"network-policy":
     {
       "fq_name": [
         "default-domain", 
         "%s", 
         "%s"
       ], 
       "network_policy_entries": {
         "policy_rule": [
           {
             "action_list": {
               "simple_action": "%s"
             }, 
             "dst_addresses": [
               {
                 "virtual_network": "%s"
               }
             ], 
             "src_addresses": [
               {
                 "virtual_network": "%s"
               }
             ],
             "protocol": "%s"
           }
         ]
       }, 
       "parent_type": "project"
     }
    }
  """ % (project, name, action, src_addr, dst_addr, protocol)
  jsondict = json.loads(jsonstring)
elif (kind == "logical-router"):
  name=js["name"]
  project=js["project"]
  jsonstring = """
  {"logical-router":
    {
      "fq_name": [
        "default-domain", 
        "%s", 
        "%s"
      ], 
      "parent_type": "project"
    }
  }
  """ % (project, name)
  jsondict = json.loads(jsonstring)
elif (kind == "bgp-router"):
  name=js["name"]
  neighbor_address=js["neighbor-address"]
  autonomous_system=js["autonomous-system"]
  router_id=js["router-id"]
  vendor=js["vendor"]
  jsonstring = """
  {"bgp-router":
    {
      "bgp_router_parameters": {
        "address": "%s", 
        "autonomous_system": %s, 
        "identifier": "%s", 
        "vendor": "%s"
      }, 
      "fq_name": [
        "default-domain", 
        "default-project", 
        "ip-fabric", 
        "__default__", 
        "%s"
      ], 
      "parent_type": "routing-instance"
    }
  }
  """ % (neighbor_address, autonomous_system, router_id, vendor, name)
  jsondict = json.loads(jsonstring)
elif (kind == "service-instance"):
  name=js["name"]
  project=js["project"]
  left_virtual_network=js["left_virtual_network"]
  right_virtual_network=js["right_virtual_network"]
  service_template=js["service_template"]
  jsonstring = """
  {"service-instance":
    {
      "fq_name": [
        "default-domain", 
        "%s", 
        "%s"
      ], 
      "parent_type": "project",
      "service_instance_properties": {
        "left_virtual_network": "%s",
        "right_virtual_network": "%s"
      }, 
      "service_template_refs": [
        {
          "to": [
            "default-domain", 
            "%s"
          ]
        }
      ]
    }
  }""" % (project, name, left_virtual_network, right_virtual_network, service_template)
  jsondict = json.loads(jsonstring)


print (jsondict)
jsonstring = json.dumps(jsondict)

#with open (jsonname, 'w') as f:
# f.write (json)

## it's not the correct way to do so :(
controller_ip = os.popen ("ip -o route get 8.8.8.8 | awk '{print $7}'").read ().rstrip()

headers= {"Content-Type": "application/json", "charset": "UTF-8"}
r = requests.post ("http://{}:8082/{}s".format(controller_ip, kind), data=jsonstring, headers=headers)
print (r.text)
