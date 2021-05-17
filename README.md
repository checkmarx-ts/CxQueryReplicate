<!-- -*- coding: utf-8-dos; -*- -->
Introduction
============

**CxQueryReplicate** is a utility that replicates customized CxSAST
queries from one CxSAST instance to another. The current version of
**CxQueryReplicate** only supports replication of queries customized
at the corporate and team levels. Replication of queries customized at
the project level is an enhancement that is planned for the future.
 
Installation
============

Using pip
------------

Usage
=====

The installation process adds the **cxqueryreplicate** command to the
user’s command search path.

The **cxqueryreplicate** command accepts the following command line
arguments:

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
* `--log-level=LEVEL`: specify the level of logging. By default, only
  informational, warning and error messages are logged.
* `--src-base-url=URL`: specify the base URL of the source CxSAST
  instance.
* `--src-password=PASSWORD`: specify the password of the user to be
  used to connect to the source CxSAST instance.
* `--src-username=USERNAME`: specify the username of the user to be
  used to connect to the source CxSAST instance.


Configuration
-------------

The **CxQueryReplicate** utility expects its configuration to be
stored in a Windows “.ini” file.

For example:

```
[main]
dry_run = False

[destination]
base_url = https://dst.example.com
username = dstuser
password = dstpassword

[source]
base_url = https://src.example.com
username = srcuser
password = srcpassword

```

User Role Requirements
======================

The user for the source instance must have the *SAST Auditor* role.

The user for the destination system must have the *Access Control
Manager* and *SAST Auditor* roles.

Both users must be members of the root team in their respective
instances (i.e., the `/CxServer` team).

Development
===========

The easiest way to set up an environment for developing
**CxQueryReplicate** is to clone this repository and then use the
**pipenv** command to create a virtual environment that includes the
relevant dependencies.

To activate this project's virtualenv, run pipenv shell.

Alternatively, run a command inside the virtualenv with pipenv run.
