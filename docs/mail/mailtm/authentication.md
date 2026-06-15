# Authentication

> Get a bearer token to authenticate with the Mail.tm API. No API key required.

To make any request (except [account creation](/api/accounts#post-accounts) and [/domains](/api/domains)) you need a bearer token. No API key is needed — just create an account and request a token.

> *How to get it?*

You need to make a *POST* request to the */token* path.

## Request

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

## Response

```json
{
  "id": "string",
  "token":"string"
}
```

Use this token as

```shell
"Authorization":"Bearer TOKEN"
```

In every request!

<note>

Remember: You should first create the account and then get the token!

</note>
