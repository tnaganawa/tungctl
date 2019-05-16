# tungctl
create tungsten fabric objects from YAML

```
# cat vn21.yaml 
kind: virtual-network
name: vn21
subnet: 10.0.21.0
prefix: 24
project: k8s-default

# ./tungctl.py create -f /tmp/vn21.yaml 
{"virtual-network": {"fq_name": ["default-domain", "k8s-default", "vn21"], "parent_uuid": "ee65027b-394d-435f-8843-f6fd7a7fb171", "parent_href": "http://172.31.8.219:8082/project/ee65027b-394d-435f-8843-f6fd7a7fb171", "parent_type": "project", "uuid": "8a612cb2-b279-4c1a-9c12-8cd846ca9b12", "href": "http://172.31.8.219:8082/virtual-network/8a612cb2-b279-4c1a-9c12-8cd846ca9b12", "name": "vn21"}}

(venv) [root@ip-172-31-8-219 ~]# contrail-api-cli --host 172.31.8.219 ls -l virtual-network
virtual-network/bd45ee5e-1a0b-4c23-96a0-3a92cc7646a4  default-domain:default-project:dci-network
virtual-network/42768402-4262-4019-9d51-98ca4a67a44a  default-domain:default-project:ip-fabric
virtual-network/7c15e8b3-056e-4425-8750-085ada93e1a6  default-domain:default-project:default-virtual-network
virtual-network/f715ebd0-c799-49c1-bee0-eea8f6d5c678  default-domain:default-project:__link_local__
virtual-network/6134d719-236a-477d-9cae-c8db3e85e933  default-domain:k8s-default:k8s-default-service-network
virtual-network/723daabe-be10-4324-a83a-4b3d534267b1  default-domain:k8s-default:k8s-default-pod-network
virtual-network/8a612cb2-b279-4c1a-9c12-8cd846ca9b12  default-domain:k8s-default:vn21  <- newly created
(venv) [root@ip-172-31-8-219 ~]# 


(venv) [root@ip-172-31-8-219 ~]# contrail-api-cli --host 172.31.8.219 cat virtual-network/8a612cb2-b279-4c1a-9c12-8cd846ca9b12
{
  "display_name": "vn21", 
  "fq_name": [
    "default-domain", 
    "k8s-default", 
    "vn21"
  ], 
  "href": "http://172.31.8.219:8082/virtual-network/8a612cb2-b279-4c1a-9c12-8cd846ca9b12", 
  "id_perms": {
    "created": "2019-05-12T11:11:42.257756", 
    "creator": null, 
    "description": null, 
    "enable": true, 
    "last_modified": "2019-05-12T11:11:42.257756", 
    "permissions": {
      "group": "cloud-admin-group", 
      "group_access": 7, 
      "other_access": 7, 
      "owner": "cloud-admin", 
      "owner_access": 7
    }, 
    "user_visible": true, 
    "uuid": {
      "uuid_lslong": 11246206080026057490, 
      "uuid_mslong": 9971300195985083418
    }
  }, 
  "name": "vn21", 
  "network_ipam_refs": [
    {
      "attr": {
        "ipam_subnets": [
          {
            "default_gateway": "10.0.21.254", 
            "dns_server_address": "10.0.21.253", 
            "subnet": {
              "ip_prefix": "10.0.21.0", 
              "ip_prefix_len": 24
            }, 
            "subnet_uuid": "d12a3cae-82a7-4fa5-a096-c4a194cd8ac2"
          }
        ]
      }, 
      "href": "http://172.31.8.219:8082/network-ipam/24241755-a4a1-4667-ac48-b8a1074a0f0a", 
      "to": [
        "default-domain", 
        "default-project", 
        "default-network-ipam"
      ], 
      "uuid": "24241755-a4a1-4667-ac48-b8a1074a0f0a"
    }
  ], 
  "parent_href": "http://172.31.8.219:8082/project/ee65027b-394d-435f-8843-f6fd7a7fb171", 
  "parent_type": "project", 
  "parent_uuid": "ee65027b-394d-435f-8843-f6fd7a7fb171", 
  "perms2": {
    "global_access": 0, 
    "owner": "None", 
    "owner_access": 7, 
    "share": []
  }, 
  "routing_instances": [
    {
      "href": "http://172.31.8.219:8082/routing-instance/deb97cf0-70dd-4ec3-ad31-beb82e38b002", 
      "to": [
        "default-domain", 
        "k8s-default", 
        "vn21", 
        "vn21"
      ], 
      "uuid": "deb97cf0-70dd-4ec3-ad31-beb82e38b002"
    }
  ], 
  "uuid": "8a612cb2-b279-4c1a-9c12-8cd846ca9b12", 
  "virtual_network_network_id": 7
}

(venv) [root@ip-172-31-8-219 ~]#
```
