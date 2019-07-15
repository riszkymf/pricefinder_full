# COMPANY PRODUCT ENDPOINT
Company endpoint is used to store and view Company that issued the product

### COMPANY PRODUCT ALL
- path: /api/company_product
- method: get
- response: application/json
- body: no
- roles: user
- usage: Get all available company_product data

### COMPANY PRODUCT ADD
- path: /api/company_product
- method: post
- response: application/json
- body: raw
- roles: user
- relation: 
- usage: Add new company_product data

raw:
```
{
    "insert": {
        "fields": {
	        "nm_company_product": string,
	        "id_company": company::id_company,
	        "id_product": product::id_product,
	        "id_worker": worker::id_worker
        }
    }
}
```

### COMPANY PRODUCT WHERE

- path: /api/company_product
- method: post
- response: application/json
- body: raw
- roles: user
- usage: Find company_product data by one or combination of tags for filtering. 

raw:
```
{
    "where": {
        "tags":{
			id_company_product : company_product::id_company_product
			id_product : product::id_product
			id_company : company::id_company
			nm_company_product : string
			id_worker : worker::id_worker
            }
    }
}
```


### COMPANY PRODUCT REMOVE
- path: /api/company_product
- method: post
- response: application/json
- body: raw
- roles: user
- usage: remove company_product data

raw:
```
{
   "remove": {
      "tags": {
			id_company_product : company_product::id_company_product
      }
      	
   }
}
```

