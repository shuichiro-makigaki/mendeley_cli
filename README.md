# mendeley_cli
CLI for Mendeley

# How to get Mendeley API token

To create, update and delete resources in your Mendeley library via Mendeley API,  OAUTH2 flow is required.
We have to register and mark this mendeley_cli as a trusted application in your mendeley (Elsevier) account by yourself.
After this registration process, You will get Client ID, Client Secret and Redirect URL.
These parameters will be required.

https://dev.mendeley.com/myapps.html

Sign In

Register a new app (if not exists)

All fields are required.
example

Application name: MendeleyCLI
Description: MendeleyCLI
RegirectURL: http://localhost:8888
Port number is variable; > 1024 is recommended.
Check: "I accept the new Terms and Conditions"
Generate secret, and save it securely
Submit

In terminal,
With setting the parameters by environment variables, get token by command `mendeley get token`
```
MENDELEY_CLIENT_ID=<...> MENDELEY_REDIRECT_URI=<...> MENDELEY_CLIENT_SECRET=<...> mendeley get token
```

Automatically open web browser, and shows Mendeley login page.
Login
Following messages will show:
```
Login succeeded. You can close this window or tab.
Please follow messages in terminal to save your token.
```

And, following messages shows in terminal.

```
Login succeeded.
Please set a environment variable MENDELEY_OAUTH2_TOKEN_BASE64, or add it to config file:

MENDELEY_OAUTH2_TOKEN_BASE64=<...>
```

Now, all parameters to run mendeley_cli is retrived.
Save them to configuration file:

```
MENDELEY_CLIENT_ID=<...>
MENDELEY_REDIRECT_URI=<...>
MENDELEY_CLIENT_SECRET=<...>
MENDELEY_OAUTH2_TOKEN_BASE64=<...>
```

The configuration file must be `~/.mendeley_cli/config` or `<pwd>/.mendeley_cli/config`.
Alternatively, they can be specified by environment varialbes directly.

All set! Run

```
mendeley get documents
```