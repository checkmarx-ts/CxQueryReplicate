<!-- -*- coding: utf-8-dos; -*- -->
# Introduction

**CxQueryReplicate** is a utility that replicates customized CxSAST
queries from one CxSAST instance to another. 

# Installation

The simplest way to install **CxQueryReplicate** is to use the
**pip3** command (Linux) or the **pip** command (Windows). The
following instructions assume a Linux environment and so use the
**pip3** command and show a Linux shell prompt.

Download the release wheel file from the [releases
page](https://github.com/checkmarx-ts/CxQueryReplicate/releases) of
the **CxQueryReplicate** GitHub repository. 

Download command example (unix) :
```
wget https://github.com/checkmarx-ts/CxQueryReplicate/releases/download/v1.0.1rc6/cxqueryreplicate-1.0.1rc6-py3-none-any.whl
```

Running the following
command in the directory to which the wheel file has been saved will
install **CxQueryReplicate** for the current user.  To install it for
system-wide use, omit the `--user` command line option.

Installation example : 
```
$ pip3 install --user cxqueryreplicate-1.0.0-py3-none-any.whl
```

After installation, the **cxqueryreplicate** command will have been
added to the command search path.

### (Optional) Installation in pipenv

For further isolation, the installation command above can be performed in a virtual
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

# Before you Start : User Role Requirements

The user for the source instance must have the *SAST Auditor* role.

The user for the destination system must have the *Access Control
Manager* and *SAST Auditor* roles.

Both users must be members of the root team in their respective
instances (i.e., the `/CxServer` team).

# Configuration and Usage

The **CxQueryReplicate** utility is invoked via the
**cxqueryreplicate** command (which the installation process should
have added to the user’s command search path).  

The **CxQueryReplicate** utility can be configured via a configuration
file, via the command line or by a mixture of both, which will be detailed in the section below

## Step 1 : Configuration of Source Settings

The **CxQueryReplicate** utility uses the [Checkmarx Python SDK]()
and, specifically, uses the SDK’s configuration to access the source CxSAST instance. The SDK configuration can be specified in any, or a mixture of, the following ways:

- Via a configuration file (Reccomended)
- Via environment variables

In Windows 10, this configuration file is placed in the folder `C:\Users\{username}\.Checkmarx`

Unless you are using the Checkmarx Python SDK for development (very unlikely for first time users), you will have to create this folder, and a file in this folder named 'config.ini'

The code block below is a template for the config file which already has the correct attributes, except for the base_url, username and password for the source instance

```
[checkmarx]
base_url =your_sast_instance_url
username =username
password =password
grant_type = password
scope = sast_rest_api
client_id = resource_owner_client
client_secret = 014DF517-39D1-4453-B7B3-9930C563627C
max_try = 3
```

### (Optional) More About Source Customization 

The default SDK configuration file is named `config.ini` and can be
found in the `.Checkmarx` subdirectory of the user’s home
directory. The location of the SDK configuration file can be
overridden using the `checkmarx_config_path` environment variable.

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

## Step 2 : Configuration of Destination Settings

In addition to the SDK configuration parameters, the
**CxQueryReplicate** has its own configuration parameters which
specify the details of the destination CxSAST instance. These
parameters can be specified either via a configuration file or via
command line options. Configuration via environment variables is not
supported.

For the sake of simplicity, it is reccomended to use a configuration file placed in the same folder as the default source configuration, which is again
`C:\Users\{username}\.Checkmarx`.  

If a configuration file for the destination instance is used, the full path to it must be specified via
the `--config_file` command line. This config file can be named anything as long as the file type is `.ini`

Example : `--config_file C:\Users\{username}\.Checkmarx\dstconfig.ini`

Here is an example of the config file below, the base_url, username and password will need to be replaced with the values for the destination SAST instance

```
[main]
dry_run = False

[destination]
base_url =your_sast_instance_url
username =username
password =password
```

### (Optional) More About Destination Customization 

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

## (Optional) Step 3 : Additional Parameters 

`--query_levels` specifies which query levels will be copied to the destination instance.  By default this is set to `corp team`.  Multiple levels can be specified, and in any order, separated by space.  The available values are `corp`, `team` and `project`

Example usage : 
```
--query_levels corp
--query_levels team corp
--query_levels corp project team
--query_levels team corp project
```

`--override_project_queries` is an optional flag.  If used, customized source instance queries will override customized destination instance queries for the same type.   If not used, no changes will occur when both the source and destination instances have customizations for the same query.  

`--export_file` is an optional flag.  If used, this will place a file called `queryfile.json` which contains a json of all queries from the source instance.  This file will be placed in the desktop.

`--import_file` is an optional flag.  This is used to read the json file which is made from the export feature above.  CxQueryReplicate will search for `queryfile.json` in the desktop.

## Step 4 : Running the script 

As mentioned above, the command `cxqueryreplicate` invokes the script.  However it needs additional parameters to run.  Here are a few examples : 

### Run with destination file configured as ini :

```
cxqueryreplicate --config_file C:\Users\{username}\.Checkmarx\dstconfig.ini
```

### Run with destination file configured as ini and import all query levels :

```
cxqueryreplicate --config_file C:\Users\{username}\.Checkmarx\dstconfig.ini --query_levels corp team project
```

### Run with destination file configured as ini and import all query levels, with a file export :

```
cxqueryreplicate --config_file C:\Users\{username}\.Checkmarx\dstconfig.ini --query_levels corp team project --export_file
```

### Run with destination file configured as ini and import team + project queries, with a file import :

```
cxqueryreplicate --config_file C:\Users\{username}\.Checkmarx\dstconfig.ini --query_levels team project --import_file
```

### Run with destination file configured as ini and import team + project queries, but destination username is specified on the command line (and all other destination credentials are inside the .ini) :

```
--config_file C:\Users\cxadmin\.Checkmarx\dstconfig.ini --query_levels team project --dst_username admin@cx
```

# Development

The easiest way to set up an environment for developing
**CxQueryReplicate** is to clone this repository and then use the
**pipenv** command to create a virtual environment that includes the
relevant dependencies.
