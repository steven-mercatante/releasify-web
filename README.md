# Releasify - API Interface

## What is this?
A RESTful API interface to the [releasify](https://github.com/steven-mercatante/releasify) library.

Releasify lets you quickly and easily automate the creation of [semantic version](https://semver.org/) releases for GitHub repos.

## How do I use it?
`POST` a JSON payload to `<your-API-URL>/releases`

### Authentication
Releasify uses pass-through authentication via [Basic access authentication](https://en.wikipedia.org/wiki/Basic_access_authentication). You just need to provide the username and password of an account that has access to create releases on the repo. You can use a [Personal Access Token](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) instead of a password.

**Releasify does not store these credentials - it just passes them to the GitHub API.**

### API Parameters
| Name | Description | Type | Required? |
| --- | --- | --- | --- |
| `owner` | The owner of the repo you want to create a release for | `string` | **Yes** |
| `repo` | The name of the repo you want to create a release for | `string` | **Yes** |
| `type` | The type of release to create. Must be one of `major`, `minor` or `patch`. | `string` | **Yes**
| `dry_run` | Perform a dry run to see what the new version will be. Releasify won't actually create the release if this argument is true. | `boolean` | No
| `force` | Create the release even if there haven't been any merge commits since the last release | `boolean` | No
| `draft` | Indicates if the release is a draft | `boolean` | No
| `prerelease` | Indicates if this is a prerelease | `boolean` | No

**Note** The above `boolean` parameters treat the following values as `true`: `"true"`, `"yes"`, `"y"`, `"1"`.

Here's an example using the excellent [HTTPie](https://httpie.org/) library:
```bash
http POST https://releasify.example.com/releases -a username:password owner=steven-mercatante repo=some-repo type=minor dry_run=y
```
