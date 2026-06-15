# Messages

> Fetch, read, and manage emails received by your temporary account.

## GET `/messages`

Get all messages for your account. Returns a paginated list.

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
      "accountId": "string",
      "msgid": "string",
      "from": {
        "name": "string",
        "address": "string"
      },
      "to": [
        {
          "name": "string",
          "address": "string"
        }
      ],
      "subject": "string",
      "intro": "string",
      "seen": true,
      "isDeleted": true,
      "hasAttachments": true,
      "size": 0,
      "downloadUrl": "string",
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

There are up to 30 messages per page, to check the total number, retrieve it from `"hydra:totalItems"`

## GET `/messages/{id}`

Retrieves a Message resource with a specific id (It has way more information than a message retrieved with [GET /messages](#get-messages) but it hasn't the "intro" member)

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
      The message you want to get by id
    </td>
  </tr>
</tbody>
</table>

**Response**

```json
{
  "@context": "string",
  "@id": "string",
  "@type": "string",
  "id": "string",
  "accountId": "string",
  "msgid": "string",
  "from": {
    "name": "string",
    "address": "string"
  },
  "to": [
    {
      "name": "string",
      "address": "string"
    }
  ],
  "cc": [
    "string"
  ],
  "bcc": [
    "string"
  ],
  "subject": "string",
  "seen": true,
  "flagged": true,
  "isDeleted": true,
  "verifications": [
    "string"
  ],
  "retention": true,
  "retentionDate": "2022-04-01T00:00:00.000Z",
  "text": "string",
  "html": [
    "string"
  ],
  "hasAttachments": true,
  "attachments": [
    {
      "id": "string",
      "filename": "string",
      "contentType": "string",
      "disposition": "string",
      "transferEncoding": "string",
      "related": true,
      "size": 0,
      "downloadUrl": "string"
    }
  ],
  "size": 0,
  "downloadUrl": "string",
  "createdAt": "2022-04-01T00:00:00.000Z",
  "updatedAt": "2022-04-01T00:00:00.000Z"
}
```

## DELETE `/messages/{id}`

Deletes the `Message` resource.

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
      The message you want to delete's id
    </td>
  </tr>
</tbody>
</table>

**Response**

*None* *(Returns status code 204 if successful.)*

## PATCH `/messages/{id}`

Marks a Message resource as read!

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
      The message you want to read's id
    </td>
  </tr>
</tbody>
</table>

**Response**

```json
{
  "seen": true
}
```

To check if the message has been read, you could also check if the status code is 200!

## GET `/sources/{id}`

Gets a Message's Source resource (If you don't know what this is, you either don't really want to use it or you should read [this](https://en.wikipedia.org/wiki/Email#Plain_text_and_HTML)!)

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
      The source you want to get by id
    </td>
  </tr>
</tbody>
</table>

**Response**

```json
{
  "@context": "string",
  "@id": "string",
  "@type": "string",
  "id": "string",
  "downloadUrl": "string",
  "data": "string"
}
```

You don't really need the `downloadUrl` if you already have the "data" String.
It will simply download that data.

## Attachments

Message's attachments need to be handled in a certain way. When you download them, be sure to download them in the right encoding (For example, a .exe file will need to be downloaded as an array of integers, but a json will need to be downloaded as String! Also, remember: APIs are your friends. contentType member can help you know how to decode the file)
