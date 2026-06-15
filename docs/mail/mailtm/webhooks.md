# Real-time Events

> Listen for new emails in real-time using SSE (Server-Sent Events) via Mercure.

Instead of webhooks, we use [Mercure](https://mercure.rocks/) to push real-time SSE events. This lets you receive emails instantly without polling.

## Listen to messages

To listen for incoming emails, connect to the Mercure hub.

**Base url:** `https://mercure.mail.tm/.well-known/mercure`

**Topic:** `/accounts/{id}`

<note>

Remember! You must use the `Bearer TOKEN` authorization in the headers!

</note>

For each listened message, there will be an `Account` event.
That Account is the Account resource that received the message, with updated `"used"` property.
