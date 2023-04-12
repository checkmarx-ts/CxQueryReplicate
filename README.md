<!-- -*- coding: utf-8-dos; -*- -->
# Introduction

**CxQueryReplicate** is a utility that replicates customized CxSAST
queries from one CxSAST instance to another. The current version of
**CxQueryReplicate** only supports replication of queries customized
at the corporate and team levels. Replication of queries customized at
the project level is an enhancement that is planned for the future.

# Installation

The simplest way to install **CxQueryReplicate** is to use the
**pip3** command (Linux) or the **pip** command (Windows). The
following instructions assume a Linux environment and so use the
**pip3** command and show a Linux shell prompt.

Download the release wheel file from the [releases
page](https://github.com/checkmarx-ts/CxQueryReplicate/releases) of
the **CxQueryReplicate** GitHub repository. Running the following
comman in the directory to which the wheel file has been saved will
install **CxQueryReplicate** for the current user. To install it for
system-wide use, omit the `--user` command line option.

```
$ pip3 install --user cxqueryreplicate-1.0.0-py3-none-any.whl
```

After installation, the **cxqueryreplicate** command will have been
added to the command search path.

For further isolation, the above can be performed in a virtual
environment created by the **pipenv** command:

```
$ pipenv --python 3
$ pip3 install --user cxqueryreplicate-1.0.0-py3-none-any.whl
```

If the **pipenv** command is not present in the installation
environment, it can be installed with the following command:

```
$ pip3 install --user pipenv
```

# Configuration and Usage

The **CxQueryReplicate** utility is invoked via the
**cxqueryreplicate** command (which the installation process should
have added to the user’s command search path).

The **CxQueryReplicate** utility can be configured via a configuration
file, via the command line or by a mixture of both.

## Step 1 : Configuration of Source Settings

The **CxQueryReplicate** utility uses the [Checkmarx Python SDK]()
and, specifically, uses the SDK’s configuration to access the source CxSAST instance. The SDK configuration can be specified in any, or a mixture of, the following ways:

- Via a configuration file
- Via environment variables
- Via command line arguments

The default SDK configuration file is named `config.ini` and can be
found in the `.Checkmarx` subdirectory of the user’s home
directory. The location of the SDK configuration file can be
overridden using the `checkmarx_config_path` environment variable or
the `--checkmarx_config_path` command line option.

The SDK configuration file is a Windows-style “.ini” file, with the
CXSAST details contained in the `checkmarx` section. The following
parameters *must* be configured:

- `base_url`: The base URL of the source CxSAST instance.
- `client_id`: The clint identifier sent in the authorization token
  request. This must always be “resource_owner_client”.
- `client_secret`: The client secret sent in the authorization token
  request. This must always be “014DF517-39D1-4453-B7B3-9930C563627C”.
- `grant_type`: The grant type sent in the authorization token
  request. This must always be “password”.
- `max_try`: Te maximum number of times to retry an API operation
  which has failed.
- `password`: The password of the user with which to connect to the
  source CxSAST instance.
- `scope`: The scope sent in the authorization token request. This
  must always include “sast_rest_api”.
- `username`: The username of the user with which to connect to the
  source CxSAST instance.

When specifying the configuration parameters via environment
variables, “cxsast_” should be prepended to the parameter name. For
example, the `cxsast_base_url` environment variable could be used to
specify the base URL of the source CxSAST instance.

When specifying the configuration parameters via command line options,
“--cxsast_” should be prepended to the parameter name. For example,
the `--cxsast_base_url` command line option could be used to specify
the base URL of the source CxSAST instance.

## Step 2 : Configuration of Destination Settings

In addition to the SDK configuration parameters, the
**CxQueryReplicate** has its own configuration parameters which
specify the details of the destination CxSAST instance. These
parameters can be specified either via a configuration file or via
command line options. Configuration via environment variables is not
supported.

There is no default location for the configuration file: if a
configuration file is to be used, its location must be specified via
the `--config_file` command line option.

The **CxQueryReplicate** configuration file is also a Windows-style
“.ini” file.  The following configuration parameters must be
configured in the `destination` section:

- `base_url`: The base URL of the destination CxSAST instance.
- `password`: The password of the user used to connect to the
  destination CxSAST instance.
- `username`: The username of the user used to connect to the
  destination CxSAST instance.

When specifying the above configuration parameters via the command
line options, “--dst_” should be prepended to the parameter name. For
example. the `--dst_base_url` command line option could be used to
specify the base URL of the destination CxSAST instance.

The following parameter may be configured in the `main` section of the
configuration file:

- `dry_run`: Specifies whether to run in “dry run” mode.

When specifying the above configuration parameter via the command
line, `--dry_run` should be used (to enable “dry run” mode).

### Sample Configuration Files
Here is a sample SDK configuration file:

```
[checkmarx]
base_url = https://src.example.com
username = srcuser
password = dstpassword
grant_type = password
scope = sast_rest_api
client_id = resource_owner_client
client_secret = 014DF517-39D1-4453-B7B3-9930C563627C
max_try = 3
```

Here is a sample **CxQueryReplicate** configuration file.

```
[main]
dry_run = False

[destination]
base_url = https://dst.example.com
username = dstuser
password = dstpassword
```

# User Role Requirements

The user for the source instance must have the *SAST Auditor* role.

The user for the destination system must have the *Access Control
Manager* and *SAST Auditor* roles.

Both users must be members of the root team in their respective
instances (i.e., the `/CxServer` team).

# Development

The easiest way to set up an environment for developing
**CxQueryReplicate** is to clone this repository and then use the
**pipenv** command to create a virtual environment that includes the
relevant dependencies.
