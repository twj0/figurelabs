# Error Handling

> HTTP status codes and error responses from the Mail.tm API.

## Successful

Generally, the request is successful when the response code is 200, 201 or 204 (You could also check if the code is between 200 and 204)

## Unsuccessful

Usually, when the request has an error the code is between 400 and 430.

**Bad request 400:** Something in your payload is missing! Or, the payload isn't there at all.

**Unauthorized 401:** Your token isn't correct (Or the headers hasn't a token at all!). Remember, every request (Except [POST /accounts](/api/accounts#post-accounts) and [POST /token](/getting-started/authentication)) should be authenticated with a Bearer token!

**Not found 404:** You're trying to access an account that doesn't exist? Or maybe reading a non-existing message? Go check that!

**Method not allowed 405:** Maybe you're trying to *GET* a */token* or *POST* a */messages*. Check the path you're trying to make a request to and check if the method is the correct one.

**I'm a teapot 418:** Who knows? Maybe the server becomes a teapot!

**Unprocessable entity 422:** Some went wrong on your payload. Like, the username of the address while creating the account isn't long enough, or, the account's domain isn't correct. Things like that.

**Too many requests 429:** You exceeded the limit of 8 requests per second! Try delaying the request by one second!
