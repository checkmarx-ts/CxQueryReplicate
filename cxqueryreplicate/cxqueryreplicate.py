"""Utility that replicates teams and custom queries from one CxSAST instance to another."""

# Copyright 2021-2023 Checkmarx
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from CheckmarxPythonSDK.CxRestAPISDK import config as _global_config
from CheckmarxPythonSDK.CxPortalSoapApiSDK import get_query_collection, upload_queries
from CheckmarxPythonSDK.CxRestAPISDK import TeamAPI, ProjectsAPI
from CheckmarxPythonSDK.CxRestAPISDK.team.dto import CxTeam

import argparse
import configparser
import datetime
import logging
import logging.config
import os.path
import pprint
import sys

# Constants
CFG_BASE_URL = 'base_url'
CFG_DESTINATION = 'destination'
CFG_DRY_RUN = 'dry_run'
CFG_MAIN = 'main'
CFG_PASSWORD = 'password'
CFG_SCOPE = 'scope'
CFG_USERNAME = 'username'

CORPORATE = 'Corporate'
DESCRIPTION = 'Description'
ERROR_MESSAGE = 'ErrorMessage'
IS_SUCCESSFUL = 'IsSuccesfull'
LANGUAGE_STATE_DATE = 'LanguageStateDate'
LOG_FORMAT = '%(asctime)s | %(levelname)8s | %(funcName)25s | %(message)s'
NAME = 'Name'
OWNING_TEAM = 'OwningTeam'
PACKAGE_FULL_NAME = 'PackageFullName'
PACKAGE_ID = 'PackageId'
PACKAGE_TYPE = 'PackageType'
PACKAGE_TYPE_NAME = 'PackageTypeName'
PROJECT_ID = 'ProjectId'
PROJECT = 'Project'
QUERIES = 'Queries'
QUERY_ID = 'QueryId'
QUERY_GROUPS = 'QueryGroups'
QUERY_VERSION_CODE = 'QueryVersionCode'
SOURCE = 'Source'
STATUS = 'Status'
TEAM = 'Team'
TYPE = 'Type'
USERNAME = 'username'

logger = logging.getLogger(__name__)


class ConfigOverride:
    """A context manager that allows the use of multiple CxSAST instances."""

    keys = [CFG_BASE_URL, CFG_USERNAME, CFG_PASSWORD, CFG_SCOPE]

    def __init__(self, new_config):

        self.new_config = new_config
        self.old_config = {}

    def __enter__(self):

        for key in self.keys:
            self.old_config[key] = _global_config.config[key]
            _global_config.config[key] = self.new_config[key]

    def __exit__(self, exc_type, exc_value, traceback):

        for key in self.keys:
            _global_config.config[key] = self.old_config[key]


class QueryReplicateException(Exception):
    """Application-specific exception calss."""
    pass


def load_config(args):
    """Load the program's configuration."""
    logger.debug('Starting')

    config = configparser.ConfigParser()
    if args.config_file:
        logger.debug(f'Loading configuration from {args.config_file}')
        if os.path.isfile(args.config_file):
            config.read(args.config_file)
        else:
            raise QueryReplicateException(f'{args.config_file}: file does not exist')
    else:
        config[CFG_MAIN] = {}
        config[CFG_DESTINATION] = {}

    config[CFG_MAIN][CFG_BASE_URL] = _global_config.config["base_url"]
    config[CFG_MAIN][CFG_USERNAME] = _global_config.config["username"]
    config[CFG_MAIN][CFG_PASSWORD] = _global_config.config["password"]
    config[CFG_MAIN][CFG_SCOPE] = 'access_control_api sast_rest_api'

    # Allow command-line override
    if args.dst_base_url:
        config[CFG_DESTINATION][CFG_BASE_URL] = args.dst_base_url
    if args.dst_username:
        config[CFG_DESTINATION][CFG_USERNAME] = args.dst_username
    if args.dst_password:
        config[CFG_DESTINATION][CFG_PASSWORD] = args.dst_password
    config[CFG_MAIN][CFG_DRY_RUN] = str(args.dry_run)

    if CFG_BASE_URL not in config[CFG_DESTINATION]:
        raise QueryReplicateException('Base URL of destination instance not specified')
    if CFG_USERNAME not in config[CFG_DESTINATION]:
        raise QueryReplicateException('Username of user for destination instance not specified')
    if CFG_PASSWORD not in config[CFG_DESTINATION]:
        raise QueryReplicateException('Password of user for destination instance not specified')

    config[CFG_DESTINATION][CFG_SCOPE] = 'access_control_api sast_rest_api'

    return config


def replicate_teams(config):
    """Replicate the team hierarchy from one CxSAST instance to another.

    Returns a mapping of source team identifiers to destination team
    identifiers.

    """
    logger.debug('Starting')

    team_api = TeamAPI()
    team_map = {}
    src_teams = {}
    for team in team_api.get_all_teams():
        src_teams[team.full_name] = team
    logger.debug(f'Source teams: {src_teams}')

    with ConfigOverride(config[CFG_DESTINATION]):
        dst_teams = {}
        # Query twice to work around bug in SDK
        team_api.get_all_teams()
        for team in team_api.get_all_teams():
            dst_teams[team.full_name] = team
        logger.debug(f'Destination teams: {dst_teams}')

        for team_full_name in sorted(src_teams):
            if team_full_name not in dst_teams:
                logger.debug(f'{team_full_name}: not in dst_teams')
                parts = team_full_name.split('/')
                team_name = parts[-1]
                parent_team = '/'.join(parts[0:-1])
                if not parent_team:
                    raise QueryReplicateException('Root destination team not visible to this user')
                logger.debug(f'parent_team: {parent_team}')
                if config[CFG_MAIN].getboolean(CFG_DRY_RUN):
                    logger.info(f'Dry run: {team_full_name}: would create team with name {team_name}')
                else:
                    parent_id = dst_teams[parent_team].team_id
                    logger.info(f'{team_full_name}: creating team with name {team_name} and parent {parent_id}')
                    team_id = team_api.create_team(team_name, parent_id)
                    logger.debug(f'Id of new team is {team_id}')
                    dst_teams[team_full_name] = CxTeam(team_id, team_name, team_full_name, parent_id)

            if not config[CFG_MAIN].getboolean(CFG_DRY_RUN):
                team_map[src_teams[team_full_name].team_id] = dst_teams[team_full_name].team_id

    logger.info('Teams replicated successfully')
    logger.debug(f'team_map: {team_map}')

    return team_map


def replicate_queries(config, team_map, args):
    """Replicate custom queries from one CxSAST instance to another."""
    logger.debug('Starting')

    src_query_groups = retrieve_query_groups(args)
    if not src_query_groups:
        logger.info('No source queries found.')
        return 0

    with ConfigOverride(config[CFG_DESTINATION]):
        dst_query_groups = retrieve_query_groups(args)
        update_src_query_groups(src_query_groups, dst_query_groups, team_map, config)
        if logger.getEffectiveLevel() == logging.DEBUG:
            pp = pprint.PrettyPrinter(indent=2)
            logger.debug(f'src_query_groups: {pp.pformat(src_query_groups)}')
        if config[CFG_MAIN].getboolean(CFG_DRY_RUN):
            logger.debug('Dry run: not uploading queries')
            return 0
        resp = upload_queries(src_query_groups)
        if resp[IS_SUCCESSFUL]:
            logger.info('Queries loaded successfully')
        else:
            logger.error(f'Error loading queries: {resp[ERROR_MESSAGE]}')

        # Re-retrieve the destination query groups to validate that
        # the upload has really been successful.
        dst_query_groups = retrieve_query_groups(args)
        return validate_query_groups(src_query_groups, dst_query_groups)


def retrieve_query_groups(args):
    """Retrieve custom queries from the current CxSAST instance."""
    logger.debug(f'Retrieving queries from {_global_config.config[CFG_BASE_URL]}')
    resp = get_query_collection()
    if not resp[IS_SUCCESSFUL]:
        raise Exception(f'Unable to retrieve queries from source instance: {resp["ErrorMessage"]}')

    query_groups = resp[QUERY_GROUPS]

    query_groups_levels = []
    query_groups_dict = {'corp': CORPORATE, 'team': TEAM, 'project': PROJECT}

    for level in args.query_levels:
        query_groups_levels.append(query_groups_dict[level])

    query_groups = [qg for qg in query_groups
                    if qg[PACKAGE_TYPE] in query_groups_levels]

    return query_groups


def find_project_names(src_query_group, dst_query_groups, config):
    """Perform a search to see if the project name of the source query exists in the destination instance

    An API call to the source instance is called using source query group which contains a project ID.  This name is
    then matched to a call to the destination instance using the destination query groups, which contains a project ID.
    If no names in the destination match the source query, none is returned.

    """
    with ConfigOverride(config[CFG_MAIN]):
        query_group_data = ProjectsAPI.get_project_details_by_id(src_query_group[PROJECT_ID])
        for qg in dst_query_groups:
            with ConfigOverride(config[CFG_DESTINATION]):
                if qg['PackageType'] == 'Project':
                    qg_data = ProjectsAPI.get_project_details_by_id(qg[PROJECT_ID])
                    if query_group_data.name == qg_data.name:
                        return qg

    return None


def find_destination_project(src_query_group, config):
    """Find the project details in the destination

    An API call to the source instance is called using source query group which contains a project ID.  This name is
    then matched to a call to the destination instance to retrieve all project details.  The project details with a
    name matching that of the source query is then returned.  If no names in the destination match the source query,
    none is returned.

    """
    with ConfigOverride(config[CFG_MAIN]):
        query_group_data = ProjectsAPI.get_project_details_by_id(src_query_group[PROJECT_ID])
        with ConfigOverride(config[CFG_DESTINATION]):
            destination_projects = ProjectsAPI.get_all_project_details()
            for project in destination_projects:
                if query_group_data.name == project.name:
                    return project

    return None


def update_src_query_groups(src_query_groups, dst_query_groups, team_map, config):
    """Update a list of query groups with information from the destination

    Given a list of query groups from a source CxSAST instance, update
    each query group, and the queries it contains, with appropriate
    values from either the corresponding query group in the
    destination CxSAST instance or from the mapping of teams in the
    source CxSASt instance to teams in the destination CxSAST
    instance.

    """

    for src_query_group in src_query_groups:
        if src_query_group[PACKAGE_TYPE] == PROJECT:
            dst_query_group_project = find_project_names(src_query_group, dst_query_groups, config)
            if dst_query_group_project:
                set_query_group_parameters(dst_query_group_project, src_query_group)
            else:
                set_query_group_parameters(config, src_query_group)
        else:
            logger.debug(f'Updating query_group: {src_query_group[PACKAGE_FULL_NAME]}')
            dst_query_group = find_query_group(src_query_group,
                                               dst_query_groups)  # match this src query group to particular dst one
            if dst_query_group:
                logger.debug('Query group found in destination instance')
                logger.debug(f'Setting query group package id to {dst_query_group[PACKAGE_ID]}')
                src_query_group[PACKAGE_ID] = dst_query_group[PACKAGE_ID]
            else:
                logger.debug('Query group not found in destination instance')
                logger.debug('Setting query group package id to 0')
                src_query_group[PACKAGE_ID] = 0
                logger.debug('Setting status to "New"')
                src_query_group[STATUS] = 'New'
                # Set the LanguageStateDte to 0001-01-01T00:00:00 (as CxAudit does)
                src_query_group[LANGUAGE_STATE_DATE] = datetime.datetime(1, 1, 1, 0, 0, 0)

            if src_query_group[OWNING_TEAM] in team_map:
                src_query_group[OWNING_TEAM] = team_map[src_query_group[OWNING_TEAM]]
            src_query_group[DESCRIPTION] = ''
            for src_query in src_query_group[QUERIES]:
                logger.debug(f'Updating query: {src_query[NAME]}')
                if dst_query_group:
                    dst_query = find_query(src_query, dst_query_group)
                else:
                    dst_query = None
                if dst_query:
                    logger.debug('Query found in destination instance')
                    logger.debug(f'Setting query id to {dst_query[QUERY_ID]}')
                    src_query[QUERY_ID] = dst_query[QUERY_ID]
                    logger.debug(f'Setting query package id to {dst_query_group[PACKAGE_ID]}')
                    src_query[PACKAGE_ID] = dst_query_group[PACKAGE_ID]
                    logger.debug('Setting status to "Edited"')
                    src_query[STATUS] = 'Edited'
                else:
                    logger.debug('Query not found in destination instance')
                    logger.debug('Setting query id to 0')
                    src_query[QUERY_ID] = 0
                    if dst_query_group:
                        logger.debug(f'Setting query package id to {dst_query_group[PACKAGE_ID]}')
                        src_query[PACKAGE_ID] = dst_query_group[PACKAGE_ID]
                    else:
                        logger.debug('Setting query package id to -1')
                        src_query[PACKAGE_ID] = -1
                    logger.debug(f'Setting query version code to 0')
                    src_query[QUERY_VERSION_CODE] = 0
                    logger.debug('Setting status to "New"')
                    src_query[STATUS] = 'New'
                logger.debug('Setting type to "Draft"')
                src_query[TYPE] = 'Draft'


def set_query_group_parameters(config, src_query_group):
    """Sets the parameters of the src_query_group, which will be written to the destination

    This scenario is if the project in the destination instance does not contain any custom queries yet, but
    the same project in the source destination has custom queries.
    """
    logger.debug('Destination project does not have custom project queries')
    dst_project = find_destination_project(src_query_group, config)
    src_query_group[PROJECT_ID] = dst_project.project_id
    src_query_group[PACKAGE_ID] = 0
    src_query_group[PACKAGE_TYPE_NAME] = 'CxProject_' + str(dst_project.project_id)
    package_name = src_query_group[PACKAGE_FULL_NAME].split(':')
    src_query_group[PACKAGE_FULL_NAME] = package_name[0] + ':' + src_query_group[PACKAGE_TYPE_NAME] + ':' + \
                                         package_name[2]
    src_query_group[STATUS] = 'New'
    src_query_group[DESCRIPTION] = ''


def set_query_group_parameters(dst_query_group_project, src_query_group):
    """Sets the parameters of the src_query_group, which will be written to the destination

    This scenario is if the project in the destination instance has custom queries, and
    the same project in the source destination has custom queries.
    """

    logger.debug('Destination project has custom project queries')
    src_query_group[PROJECT_ID] = dst_query_group_project[PROJECT_ID]
    src_query_group[PACKAGE_ID] = 0
    src_query_group[PACKAGE_TYPE_NAME] = 'CxProject_' + str(src_query_group[PROJECT_ID])
    package_name = src_query_group[PACKAGE_FULL_NAME].split(':')
    src_query_group[PACKAGE_FULL_NAME] = package_name[0] + ':' + src_query_group[PACKAGE_TYPE_NAME] + ':' + \
                                         package_name[2]
    src_query_group[STATUS] = 'New'
    src_query_group[DESCRIPTION] = ''


def find_query_group(query_group, query_groups):
    """Find a query group in a list of query groups.

    Searches a list of query groups for a given query group, matching
    on the fully qualified query group name. Returns the query group,
    if found, or ``None``.

    """

    for qg in query_groups:
        if query_group[PACKAGE_FULL_NAME] == qg[PACKAGE_FULL_NAME] and \
                query_group[OWNING_TEAM] == qg[OWNING_TEAM]:
            return qg

    return None


def find_query(query, query_group):
    """Find a query in a query group.

    Searches a query group for a given query, matching by query
    name. Returns the query, if found, or ``None``.
    """

    for q in query_group[QUERIES]:
        if query[NAME] == q[NAME]:
            return q

    return None


def validate_query_groups(src_query_groups, dst_query_groups):
    """Validate that the source query groups have been replicated.

    This function loops over the query groups retrieved from the
    source CxSAST instance and, for each query group, checks that it
    is present in the query groups retrieved from the destination
    CxSAST instance and, for each query in the query group, checks
    that it, too, is present in the corresponding destination query
    group and that in both instances the source of the query is the
    same.

    """
    logger.debug('Validating query groups')

    status = 0
    for src_query_group in src_query_groups:
        qg_full_name = src_query_group[PACKAGE_FULL_NAME]
        dst_query_group = find_query_group(src_query_group, dst_query_groups)
        if dst_query_group:
            logger.debug(f'{qg_full_name} matched')
            for src_query in src_query_group[QUERIES]:
                q_name = src_query[NAME]
                dst_query = find_query(src_query, dst_query_group)
                if dst_query:
                    logger.debug(f'{q_name} matched')
                    if src_query[SOURCE] != dst_query[SOURCE]:
                        logger.error('Query source does not match')
                        status = 1
                else:
                    logger.error(f'{q_name} not found in destination query group')
                    status = 1
        else:
            logger.error(f'{qg_full_name} not found in destination instance')
            status = 1

    logger.info(f'Queries validated (status = {status})')

    return status


def setup_logger(logger_name, log_level):
    """Set up the logger configuration"""
    formatter = logging.Formatter(LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    global logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.addHandler(handler)


def replicate_teams_and_queries(config, args):
    team_map = replicate_teams(config)
    status = replicate_queries(config, team_map, args)
    return status


# Main entry point


def main():
    parser = argparse.ArgumentParser(description='Replicate CxSAST custom queries')
    parser.add_argument('--config_file', metavar='FILE',
                        help='The configuration file')
    parser.add_argument('--dst_base_url', metavar='BASE_URL',
                        help='The base URL of the destination CxSAST instance')
    parser.add_argument('--dst_username', metavar='USERNAME',
                        help='The username for the destination CxSAST instance')
    parser.add_argument('--dst_password', metavar='PASSWORD',
                        help='The password for the destination CxSAST instance')
    parser.add_argument('--log_level', metavar='LEVEL', default='INFO',
                        help='The log level')
    parser.add_argument('--dry_run', action='store_true', default=False,
                        help='Dry run')
    parser.add_argument('--query_levels', nargs='+', default='corp',
                        help='The query levels to be migrated')

    args = parser.parse_args()

    setup_logger(__name__, args.log_level.upper())
    try:
        logger.info('Starting')
        config = load_config(args)
        status = replicate_teams_and_queries(config, args)
        logger.info(f'Completed with exit status {status}')
        sys.exit(status)
    except Exception as e:
        logger.exception(f'Caught an exception: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
