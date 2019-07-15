# Hosting ENDPOINT
Hosting endpoint is used to store and view Hosting data specification

### Hosting ALL
- path: /api/hosting
- method: get
- response: application/json
- body: no
- roles: user
- usage: Get all available hosting data

### Hosting ADD
- path: /api/hosting
- method: post
- response: application/json
- body: raw
- roles: user
- relation: 
- usage: Add new hosting data for an company product

raw:
```
{
    "insert": {
        "fields": {
            "id_company_product": dt_company_product::id_company_product
            'spec_price': string::spec_price
            "spec_storage": string::spec_storage
            'spec_database': string::spec_database
            "spec_free_domain": string::spec_free_domain
            "spec_hosting_domain": string::spec_hosting_domain
            'spec_subdomain': string::spec_subdomain
            "spec_ftp_user": string::spec_ftp_user
            "spec_control_panel": string::spec_control_panel
            'spec_email_account': string::spec_email_account
            "spec_spam_filter": string::spec_spam_filter
            "date_time": string::date_time
        }
    }
}
```

### Hosting WHERE

- path: /api/hosting
- method: post
- response: application/json
- body: raw
- roles: user
- usage: Find hosting data by one or combination of tags for filtering. 

raw:
```
{
    "where": {
        "tags":{
           "id_hosting": hosting::id_hosting,
            "id_company_product": dt_company_product::id_company_product
            'spec_price': string::spec_price
            "spec_storage": string::spec_storage
            'spec_database': string::spec_database
            "spec_free_domain": string::spec_free_domain
            "spec_hosting_domain": string::spec_hosting_domain
            'spec_subdomain': string::spec_subdomain
            "spec_ftp_user": string::spec_ftp_user
            "spec_control_panel": string::spec_control_panel
            'spec_email_account': string::spec_email_account
            "spec_spam_filter": string::spec_spam_filter
            "date_time": string::date_time        }
    }
}
```


### Hosting REMOVE
- path: /api/hosting
- method: post
- response: application/json
- body: raw
- roles: user
- usage: remove hosting data

raw:
```
{
   "remove": {
      "tags": {
      	"id_hosting": hosting::id_hosting
      }
      	
   }
}
```

### HOSTING VIEW
- path: /api/hosting
- method: post
- response: application/json
- body: raw
- roles: user
- usage: View hosting and its related data

raw:
```
{
   "view": {
      "tags": {
      	"id_hosting": hosting::id_hosting
      }
      	
   }
}
```
tags:
- id_hosting: id of hosting data that will be removed

To see all related data, the following json in body

raw
```
{
   "view": {
      "tags": {
      	"id_hosting": ""
      }
      	
   }
}
```
