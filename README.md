# mendeley_cli
CLI for Mendeley

# Install

```
pip install mendeley_cli
```

# How to get Mendeley API token

To create, update and delete resources in your Mendeley library via Mendeley API, OAUTH2 flow is required.
We have to register and mark this mendeley_cli as a trusted application in your mendeley (Elsevier) account by yourself.

## 1. Register mendeley_cli as a trusted app

https://dev.mendeley.com/myapps.html

Register a new app (if not exists)

### Example

All fields are required.

* **Application name** MendeleyCLI
* **Description** MendeleyCLI
* **RegirectURL** http://localhost:8888
  * Port number is a variable; >1024 is recommended.
* Generate secret, and save it securely.
* Submit

You got Client ID, Client Secret and Redirect URL.

## 2. Generate OAUTH2 token

In terminal, with setting the parameters by environment variables, get token by `mendeley get token`:

```
MENDELEY_CLIENT_ID=<...> MENDELEY_CLIENT_SECRET=<...> MENDELEY_REDIRECT_URI=<...> mendeley get token
```

Automatically open web browser, shows Mendeley login page, and login.

Then, following messages will show:

```
Login succeeded. You can close this window or tab.
Please follow messages in terminal to save your token.
```

Also, following messages shows in terminal:

```
Login succeeded.
Please set a environment variable MENDELEY_OAUTH2_TOKEN_BASE64, or add it to config file:

MENDELEY_OAUTH2_TOKEN_BASE64=<...>
```

Now, all parameters to run mendeley_cli is retrived.

## 3. Configure mendeley_cli

Save them to configuration file:

```
MENDELEY_CLIENT_ID=<...>
MENDELEY_REDIRECT_URI=<...>
MENDELEY_CLIENT_SECRET=<...>
MENDELEY_OAUTH2_TOKEN_BASE64=<...>
```

The configuration file must be `~/.mendeley_cli/config` or `<pwd>/.mendeley_cli/config`.
Alternatively, they can be specified by environment varialbes directly.

## 4. All set!

Run

```
mendeley get documents
```
