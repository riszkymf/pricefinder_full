# COMPANY ENDPOINT
Company endpoint is used to store and view Company that issued the product

### Company ALL
- path: /api/company
- method: get
- response: application/json
- body: no
- roles: user
- usage: Get all available company data

### company ADD
- path: /api/company
- method: post
- response: application/json
- body: raw
- roles: user
- relation: 
- usage: Add new company data for an company product

raw:
```
{
    "insert": {
        "fields": {
                    "nm_company": string,
                    'url_company': string,
                    "currency_used": string
        }
    }
}
```

### company WHERE

- path: /api/company
- method: post
- response: application/json
- body: raw
- roles: user
- usage: Find company data by one or combination of tags for filtering. 

raw:
```
{
    "where": {
        "tags":{
                    "id_company": company::id_company,
                    "nm_company": string,
       }
    }
}
```


### COMPANY REMOVE
- path: /api/company
- method: post
- response: application/json
- body: raw
- roles: user
- usage: remove company data

raw:
```
{
   "remove": {
      "tags": {
      	"id_company": company::id_company
      }
      	
   }
}
```

