# mendeley-cli
CLI for Mendeley

# Install

```
pip install mendeley-cli
```

Docker image is also available.

```
docker image pull makisyu/mendeley
```

# How to get Mendeley API token

To create, update, and delete resources in your Mendeley library via Mendeley API, OAUTH2 flow is required.
We have to register and mark this mendeley-cli as a trusted application in your Mendeley (Elsevier) account by yourself.

## 1. Register mendeley-cli as a trusted app

https://dev.mendeley.com/myapps.html

Register a new app (if not exists)

### Example

All fields are required.

* **Application name**: MendeleyCLI
* **Description**: MendeleyCLI
* **RegirectURL**: http://localhost:8888
  * Port number is a variable; >1024 is recommended.
* Generate secret, and save it securely.
* Submit

You got Client ID, Client Secret and Redirect URL.

## 2. Generate OAUTH2 token

In a terminal, with setting the parameters by environment variables, get token by `mendeley get token`:

```
MENDELEY_CLIENT_ID=<...> MENDELEY_CLIENT_SECRET=<...> MENDELEY_REDIRECT_URI=<...> mendeley get token
```

Automatically web browser opens and shows the login page, and please login.

Then, the following messages show:

```
Login succeeded. You can close this window or tab.
Please follow messages in the terminal to save your token.
```

Also, the following messages show in the terminal:

```
Login succeeded.
Please set an environment variable MENDELEY_OAUTH2_TOKEN_BASE64, or add it to a config file:

MENDELEY_OAUTH2_TOKEN_BASE64=<...>
```

Now, all parameters to run mendeley_cli is retrieved.

## 3. Configure mendeley_cli

Save them to configuration file:

```
MENDELEY_CLIENT_ID=<...>
MENDELEY_REDIRECT_URI=<...>
MENDELEY_CLIENT_SECRET=<...>
MENDELEY_OAUTH2_TOKEN_BASE64=<...>
```

The configuration file must be `~/.mendeley_cli/config` or `<pwd>/.mendeley_cli/config`.
Alternatively, they can be specified by environment variables directly.

## 4. All set!

Run

```
mendeley get documents
```
