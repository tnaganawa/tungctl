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

if (not sys.argv[1]=='create' or not sys.argv[2]=='-f'):
 sys.exit(32)

yamlname = sys.argv[3]
with open(yamlname) as f:
 yamls = yaml.safe_load_all(f.read())
jsonname=yamlname.split('.')[0] + '.json'

## it's not the correct way to do so :(
controller_ip = os.popen ("ip -o route get 8.8.8.8 | awk '{print $7}'").read ().rstrip()
vnc_api_headers= {"Content-Type": "application/json", "charset": "UTF-8"}

def empty_func():
 pass

do_finally=empty_func

for js in yamls:
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
    if ("apply_service_list" in np_rule.keys()):
      jsondict["network-policy"]["network_policy_entries"]["policy_rule"][0]["action_list"]["apply_service"]=np_rule["apply_service_list"]
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
    if ("connected_interfaces" in js.keys()):
      jsondict["logical-router"]["virtual_machine_interface_refs"]=[]
      for uuid in js["connected_interfaces"]:
        r = requests.post ("http://{}:8082/id-to-fqname".format(controller_ip), data='{"uuid": "%s"}' % uuid, headers=vnc_api_headers)
        #print (r.text)
        fqname = json.loads(r.text)["fq_name"]
        jsondict["logical-router"]["virtual_machine_interface_refs"].append ({"uuid": uuid, "to": fqname})
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
          "interface_list": [
            {
              "virtual_network": "%s"
            }, 
            {
              "virtual_network": "%s"
            }
          ],
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
    }""" % (project, name, left_virtual_network, right_virtual_network, left_virtual_network, right_virtual_network, service_template)
    jsondict = json.loads(jsonstring)
  elif (kind == "virtual-machine-interface"):
    name=js["name"]
    project=js["project"]
    virtual_network=js["virtual-network"]
    jsonstring = """
    {"virtual-machine-interface":
      {
        "fq_name": [
          "default-domain", 
          "%s", 
          "%s"
        ], 
        "parent_type": "project",
        "virtual_network_refs": [
          {
            "to": [
              "default-domain", 
              "%s", 
              "%s"
            ] 
          }
        ]
      }
    }
    """ % (project, name, project, virtual_network)
    jsondict = json.loads(jsonstring)
    if ("uuid" in js.keys()):
      jsondict["virtual-machine-interface"]["uuid"]=js["uuid"]
    if ("mac-address" in js.keys()):
      jsondict["virtual-machine-interface"]["virtual_machine_interface_mac_addresses"]={"mac_address": [js["mac-address"]]}
    if ("virtual_machine_refs" in js.keys()):
      jsondict["virtual-machine-interface"]["virtual_machine_refs"]=[{"to": [js["virtual_machine_refs"]]}]
  
  elif (kind == "port-tuple"):
    name=js["name"]
    project=js["project"]
    jsonstring = """
    {"port-tuple":
      {
        "fq_name": [
          "default-domain", 
          "%s", 
          "%s", 
          "%s"
        ], 
        "parent_type": "service-instance"
      }
    }
    """ % (project, name, name)
    jsondict = json.loads(jsonstring)
    if ("connected_vmis" in js.keys()):
      def update_vmis_to_attach_to_port_tuple():
        port_tuple_refs=[{"to": ["default-domain", project, name, name]}]
        for uuid in js["connected_vmis"]:
          r = requests.get ("http://{}:8082/virtual-machine-interface/{}".format(controller_ip, uuid))
          #print (r.text)
          tmp_js = json.loads(r.text)
          tmp_js["virtual-machine-interface"]["port_tuple_refs"]=port_tuple_refs
          print (json.dumps(tmp_js))
          r = requests.put ("http://{}:8082/virtual-machine-interface/{}".format(controller_ip, uuid), data=json.dumps(tmp_js), headers=vnc_api_headers)
          print (r.text)
      do_finally = update_vmis_to_attach_to_port_tuple
  elif (kind == "virtual-machine"):
    name=js["name"]
    jsonstring = """
    {"virtual-machine":
      {
        "fq_name": [
          "%s"
        ]
      }
    }
    """ % (name)
    jsondict = json.loads(jsonstring)
    if ("uuid" in js.keys()):
      uuid=js["uuid"]
      jsondict["virtual-machine"]["uuid"]=js["uuid"]
    if ("virtual-machine-interface" in js.keys()):
      def update_vmis_to_attach_to_virtual_machine():
        virtual_machine_refs=[{"to": [name]}]
        uuid = js["virtual-machine-interface"]
        r = requests.get ("http://{}:8082/virtual-machine-interface/{}".format(controller_ip, uuid))
        tmp_js = json.loads(r.text)
        tmp_js["virtual-machine-interface"]["virtual_machine_refs"]=virtual_machine_refs
        print (json.dumps(tmp_js))
        r = requests.put ("http://{}:8082/virtual-machine-interface/{}".format(controller_ip, uuid), data=json.dumps(tmp_js), headers=vnc_api_headers)
        print (r.text)
      do_finally = update_vmis_to_attach_to_virtual_machine
  elif (kind == "instance-ip"):
    name=js["name"]
    project=js["project"]
    instance_ip_address=js["instance_ip_address"]
    virtual_machine_interface=js["virtual_machine_interface"]
    virtual_network=js["virtual_network"]
    jsonstring = """
    {"instance-ip":
      {
        "fq_name": [
          "%s"
        ], 
        "instance_ip_address": "%s", 
        "virtual_machine_interface_refs": [
          {
            "to": [
              "default-domain", 
              "%s", 
              "%s"
            ] 
          }
        ], 
        "virtual_network_refs": [
          {
            "to": [
              "default-domain", 
              "%s", 
              "%s"
            ] 
          }
        ]
      }
    }
    """ % (name, instance_ip_address, project, virtual_machine_interface, project, virtual_network)
    jsondict = json.loads(jsonstring)
  
  
  jsonstring = json.dumps(jsondict)
  print (jsonstring)
  
  #with open (jsonname, 'w') as f:
  # f.write (json)
  
  r = requests.post ("http://{}:8082/{}s".format(controller_ip, kind), data=jsonstring, headers=vnc_api_headers)
  print (r.text)
  
  do_finally()
