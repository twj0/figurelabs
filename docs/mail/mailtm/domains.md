# Domains

> List available email domains for creating temporary accounts.

## GET `/domains`

Get the list of available domains. You need a domain before you can [create an account](/api/accounts#post-accounts).
Returns a paginated list of domains.

**Body**

*None*

**Params**

<table>
<thead>
  <tr>
    <th>
      Name
    </th>
    
    <th>
      Type
    </th>
    
    <th>
      Description
    </th>
  </tr>
</thead>

<tbody>
  <tr>
    <td>
      page
    </td>
    
    <td>
      int
    </td>
    
    <td>
      The collection page number
    </td>
  </tr>
</tbody>
</table>

**Response**

```json
{
  "hydra:member": [
    {
      "@id": "string",
      "@type": "string",
      "@context": "string",
      "id": "string",
      "domain": "string",
      "isActive": true,
      "isPrivate": true,
      "createdAt": "2022-04-01T00:00:00.000Z",
      "updatedAt": "2022-04-01T00:00:00.000Z"
    }
  ],
  "hydra:totalItems": 0,
  "hydra:view": {
    "@id": "string",
    "@type": "string",
    "hydra:first": "string",
    "hydra:last": "string",
    "hydra:previous": "string",
    "hydra:next": "string"
  },
  "hydra:search": {
    "@type": "string",
    "hydra:template": "string",
    "hydra:variableRepresentation": "string",
    "hydra:mapping": [
      {
        "@type": "string",
        "variable": "string",
        "property": "string",
        "required": true
      }
    ]
  }
}
```

When you create an email, you have to know first which domain to use.

You'll need to retrieve the domain, and then, do like so:

```javascript
"user@"+domains[0]['domain']
```

There are up to 30 domains per page, to check the total number, retrieve it from `"hydra:totalItems"`

## GET `/domains/{id}`

Retrieve a domain by its id (Useful for deleted/private domains)

**Body**

*None*

**Params**

<table>
<thead>
  <tr>
    <th>
      Name
    </th>
    
    <th>
      Type
    </th>
    
    <th>
      Description
    </th>
  </tr>
</thead>

<tbody>
  <tr>
    <td>
      id
    </td>
    
    <td>
      string
    </td>
    
    <td>
      The domain you want to get with id
    </td>
  </tr>
</tbody>
</table>

**Response**

```json
{
  "@id": "string",
  "@type": "string",
  "@context": "string",
  "id": "string",
  "domain": "string",
  "isActive": true,
  "isPrivate": true,
  "createdAt": "2022-04-01T00:00:00.000Z",
  "updatedAt": "2022-04-01T00:00:00.000Z"
}
```
