# VM ENDPOINT
VM endpoint is used to store and view VM data specification

### VM ALL
- path: /api/vm
- method: get
- response: application/json
- body: no
- roles: user
- usage: Get all available record data

### VM ADD
- path: /api/vm
- method: post
- response: application/json
- body: raw
- roles: user
- relation: 
- usage: Add new vm data for an company product

raw:
```
{
    "insert": {
        "fields": {
                    "id_company_product: string::id_company_product,
                    "spec_vcpu": string::spec_vcpu,
                    'spec_clock': string::spec_clock,
                    "spec_ram": string::spec_ram,
                    "spec_os": string::spec_os,
                    "spec_storage_volume": string::spec_storage_volume,
                    'spec_ssd_volume': string::spec_ssd_volume,
                    "spec_snapshot_volume": string::spec_snapshot_volume,
                    "spec_template_volume": string::spec_template_volume,
                    'spec_iso_volume': string::spec_iso_volume,
                    "spec_public_ip": string::spec_public_ip,
                    "spec_backup_storage": string::spec_backup_storage,
                    'spec_price': string::spec_price,
                    "spec_notes": string::spec_notes,
                    "date_time": string::date_time
        }
    }
}
```

### VM WHERE

- path: /api/vm
- method: post
- response: application/json
- body: raw
- roles: user
- usage: Find vm data by one or combination of tags for filtering. 

raw:
```
{
    "where": {
        "tags":{
            "id_vm": vm::id_vm
        }
    }
}
```


### RECORD REMOVE
- path: /api/vm
- method: post
- response: application/json
- body: raw
- roles: user
- usage: remove vm data

raw:
```
{
   "remove": {
      "tags": {
      	"id_vm": vm::id_vm
      }
      	
   }
}
```

### RECORD VIEW
- path: /api/vm
- method: post
- response: application/json
- body: raw
- roles: user
- usage: View record and its related data

raw:
```
{
   "view": {
      "tags": {
      	"id_vm": vm::id_vm
      }
      	
   }
}
```
tags:
- id_record: id of record data that will be removed

To see all related data, the following json in body

raw
```
{
   "view": {
      "tags": {
      	"id_vm": ""
      }
      	
   }
}
```
