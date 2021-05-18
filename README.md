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
**pip3** command.

The following commands will clone the **CxQueryReplicate** source code
repository and install **CxQueryReplicate** for the current user:

```
git clone https://github.com/checkmarx-ts/CxQueryReplicate.git
pip3 install --user CxQueryReplicate
```

It is also possible to use the **pipenv** command to create a virtual
environment with **CxQueryReplicate**'s dependencies and then use the
**pip3** command to install **CxQueryReplicate** itself.

If the **pipenv** command is not present in the installation
environment, it can be installed with the following command:

```
$ pip3 install pipenv
```

Clone the **CxQueryReplicate** repository:

```
$ git clone https://github.com/checkmarx-ts/CxQueryReplicate.git
```

Change directory to the `CxQueryReplicate` directory and initialize a virtual environment:

```
$ cd CxQueryReplicate
$ pipenv --python 3
```

Install **CxReplicateQuery**’s dependencies and start a new shell in
the virtual environment:

```
$ pipenv install
$ pipenv shell
```

Install **CxQueryReplicate** itself:

```
$ pip3 install .
```

This will add the **cxqueryreplicate** command to the command search path:

```
$ which cxqueryreplicate
~/.local/share/virtualenvs/CxQueryReplicate-jQx2tljc/bin/cxqueryreplicate
```

Of course, it is not required that **CxQueryReplicate** be installed
in a virtual environment. **CxQueryReplicate** can be installed for
the current user with the following commands:

```
git clone https://github.com/checkmarx-ts/CxQueryReplicate.git
pip3 install --user CxQueryReplicate
```

# Configuration and Usage

The **CxQueryReplicate** utility is invoked via the
**cxqueryreplicate** command (which the installation process should
have added to the user’s command search path).

The **CxQueryReplicate** utility can be configured via a configuration
file, via the command line or by a mixture of both.

Due to its use of the Checkmarx Python SDK, the **cxqueryreplicate**
command expects that the details of a CxSAST instance are specified
either in a configuration file or via environment variables.

## Command Line Options

The **cxqueryreplicate** command accepts the following command line
options:

* `--config-file=FILE`: specify the location of the configuration
  file.
* `--dry-run`: list the actions that would be performed but do not
  perform them.
* `--dst-base-url=URL`: specify the base URL of the destination CxSAST
  instance.
* `--dst-password=PASSWORD`: specify the password of the user to be
  used to connect to the destination CxSAST instance.
* `--dst-username=USERNAME`: specify the username of the user to be
  used to connect to the destination CxSAST instance.
* `-h` or `--help`: print a usage message and exit.
* `--log-level=LEVEL`: specify the level of logging. By default, only
  informational, warning and error messages are logged.
* `--src-base-url=URL`: specify the base URL of the source CxSAST
  instance.
* `--src-password=PASSWORD`: specify the password of the user to be
  used to connect to the source CxSAST instance.
* `--src-username=USERNAME`: specify the username of the user to be
  used to connect to the source CxSAST instance.


## Configuration File

The `--config-file` command line option can be used to specify a file
containing the **CxQueryReplicate** utility’s configuration. This file
must be a Windows-style “.ini” file. This file can contain any of the
the following sections (enclosed in square brackets):

- `main`: this section contains general configuration items.
   The following configuration items are recognized in this section:
   - `dry_run`: if set to true, list the actions that would be
     performed but do not perform them.
- `source`: this section contains details of the source CxSAST
  instance.
  The following configuration items are recognized in this section:
  - `base_url`: the base URL of the source CxSAST instance.
  - `password`: the password of the user to be used to connect to the
    source CxSAST instance.
  - `username`: the username of the user to be used to connect to the
    source CxSAST instance.
- `destination`: this section contains details of the destination
  CxSAST instance.
  - `base_url`: the base URL of the destination CxSAST instance.
  - `password`: the password of the user to be used to connect to the
    destination CxSAST instance.
  - `username`: the username of the user to be used to connect to the
    destination CxSAST instance.

### Sample Configuration file
Here is a sample configuration file.

```
[main] dry_run = False

[destination]
base_url = https://dst.example.com
username = dstuser
password = dstpassword

[source]
base_url = https://src.example.com
username = srcuser
password = srcpassword

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

To activate this project's virtualenv, run pipenv shell.

Alternatively, run a command inside the virtualenv with pipenv run.
