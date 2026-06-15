# Accounts

> Create and manage temporary email accounts.

## POST `/accounts`

Create a new temporary email account.

**Body**

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
      address
    </td>
    
    <td>
      string
    </td>
    
    <td>
      Account's address. Example: <a href="mailto:user@example.com">
        user@example.com
      </a>
    </td>
  </tr>
  
  <tr>
    <td>
      password
    </td>
    
    <td>
      string
    </td>
    
    <td>
      Account's password.
    </td>
  </tr>
</tbody>
</table>

**Params**

*None*

**Response**

```json
{
  "@context": "string",
  "@id": "string",
  "@type": "string",
  "id": "string",
  "address": "user@example.com",
  "quota": 0,
  "used": 0,
  "isDisabled": true,
  "isDeleted": true,
  "createdAt": "2022-04-01T00:00:00.000Z",
  "updatedAt": "2022-04-01T00:00:00.000Z"
}
```

At this point, you could now [get the token](/getting-started/authentication) and do all the cool stuff you want to do.

## GET `/accounts/{id}`

Get an Account resource by its id (Obviously, the Bearer token needs to be the one of the account you are trying to retrieve)

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
      The message you want to gets id
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
  "address": "user@example.com",
  "quota": 0,
  "used": 0,
  "isDisabled": true,
  "isDeleted": true,
  "createdAt": "2022-04-01T00:00:00.000Z",
  "updatedAt": "2022-04-01T00:00:00.000Z"
}
```

## DELETE `/accounts/{id}`

Deletes the Account resource.

<caution>

Be careful! We can't restore your account, if you use this method, bye bye dear account <c>



</c>
</caution>

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
      The account you want to delete by id
    </td>
  </tr>
</tbody>
</table>

**Response**

*None* *(Returns status code 204 if successful.)*

## GET `/me`

Returns the Account resource that matches the Bearer token that sent the request.

**Body**

*None*

**Params**

*None*

**Response**

```json
{
  "@context": "string",
  "@id": "string",
  "@type": "string",
  "id": "string",
  "address": "user@example.com",
  "quota": 0,
  "used": 0,
  "isDisabled": true,
  "isDeleted": true,
  "createdAt": "2022-04-01T00:00:00.000Z",
  "updatedAt": "2022-04-01T00:00:00.000Z"
}
```
