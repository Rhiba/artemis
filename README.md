#### Attempt at a discord bot to organise my life.

Create a postgresql database with given schema and manually add first superuser (`is_superuser` and `can_alias` should be `true`).

Need a `creds.json` file in same dir as artemis with Discord token and postgresql databse information. Format:

```json
{
	"token":"TOKEN_STRING_HERE",
	"dbinfo": {
		"dbname":"NAME_HERE",
		"user":"USERNAME_HERE",
		"host":"PROBABLY_LOCALHOST_HERE",
		"password":"HUNTER2_HERE"
	}
}
```
