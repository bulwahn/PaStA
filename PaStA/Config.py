"""
PaStA - Patch Stack Analysis

Copyright (c) OTH Regensburg, 2016

Author:
  Ralf Ramsauer <ralf.ramsauer@othr.de>

This work is licensed under the terms of the GNU GPL, version 2.  See
the COPYING file in the top-level directory.
"""
import configparser
import os

from .Repository import Repository
from .PatchStack import PatchStackDefinition


class Thresholds:
    def __init__(self, autoaccept, interactive, diff_lines_ratio,
                 heading, filename, message_diff_weight):
        """
        :param autoaccept: Auto accept threshold. Ratings with at least this threshold will automatically be accepted.
        :param interactive: Ratings with at least this threshold are presented to the user for interactive rating.
               Ratings below this threshold will automatically be discarded.
        :param diff_lines_ratio: Minimum ratio of shorter diff / longer diff
        :param heading: Minimum similarity rating of the section heading of a diff
        :param filename: Minimum similarity of two filenames for being evaluated (files in a repo may move).
        :param message_diff_weight: heuristic factor of message rating to diff rating
        """

        # t_a
        self.autoaccept = autoaccept
        # t_i
        self.interactive = interactive
        # t_h
        self.heading = heading
        # t_f
        self.filename = filename
        # w
        self.message_diff_weight = message_diff_weight

        self.diff_lines_ratio = diff_lines_ratio


class Config:

    # Configuration file containing default parameters
    DEFAULT_CONFIG = 'PaStA-resources/common/default.cfg'
    BLACKLIST_LOCATION = 'PaStA-resources/common/blacklists'

    def __init__(self, config_file):
        self._project_root = os.path.dirname(os.path.realpath(config_file))
        self._config_file = config_file

        if not os.path.isfile(Config.DEFAULT_CONFIG):
            raise FileNotFoundError('Default config file \'%s\' not found' % Config.DEFAULT_CONFIG)

        if not os.path.isfile(config_file):
            raise FileNotFoundError('Config file \'%s\' not found' % config_file)

        cfg = configparser.ConfigParser()
        cfg.read([Config.DEFAULT_CONFIG, self._config_file])
        pasta = cfg['PaStA']

        # Obligatory values
        self.project_name = pasta.get('PROJECT_NAME')
        if not self.project_name:
            raise RuntimeError('Project name not found')

        self.repo_location = pasta.get('REPO')
        if not self.repo_location:
            raise RuntimeError('Location of repository not found')
        self.repo_location = os.path.join(self._project_root, self.repo_location)
        self.repo = Repository(self.repo_location)

        self.upstream_range = pasta.get('UPSTREAM_MIN'), pasta.get('UPSTREAM_MAX')
        if not all(self.upstream_range):
            raise RuntimeError('Please provide a valid upstream range in your config')

        # Parse locations, those will fallback to default values
        self.patch_stack_definition_filename = os.path.join(self._project_root, pasta.get('PATCH_STACK_DEFINITION'))
        self.stack_hashes = os.path.join(self._project_root, pasta.get('STACK_HASHES'))
        self.upstream_hashes_filename = os.path.join(self.stack_hashes, 'upstream')
        self.mailbox_id_filename = os.path.join(self.stack_hashes, 'mailbox')
        self.similar_patches = os.path.join(self._project_root, pasta.get('SIMILAR_PATCHES'))
        self.similar_upstream = os.path.join(self._project_root, pasta.get('SIMILAR_UPSTREAM'))
        self.similar_mailbox = os.path.join(self._project_root, pasta.get('SIMILAR_MAILBOX'))
        self.false_positives = os.path.join(self._project_root, pasta.get('FALSE_POSTITIVES'))
        self.patch_groups = os.path.join(self._project_root, pasta.get('PATCH_GROUPS'))
        self.commit_description = os.path.join(self._project_root, pasta.get('COMMIT_DESCRIPTION'))
        self.evaluation_result = os.path.join(self._project_root, pasta.get('EVALUATION_RESULT'))
        self.diffs_location = os.path.join(self._project_root, pasta.get('DIFFS'))
        self.R_resources = os.path.join(self._project_root, pasta.get('R_RESOURCES'))
        self.mbox_mindate = pasta.get('MBOX_MINDATE')
        self.mbox_maxdate = pasta.get('MBOX_MAXDATE')
        self.upstream_blacklist = pasta.get('UPSTREAM_BLACKLIST')
        self.commit_cache_stack_filename = os.path.join(self._project_root, pasta.get('COMMIT_CACHE_STACK'))
        self.commit_cache_upstream_filename = os.path.join(self._project_root, pasta.get('COMMIT_CACHE_UPSTREAM'))
        self.commit_cache_mbox_filename = os.path.join(self._project_root, pasta.get('COMMIT_CACHE_MBOX'))
        if self.upstream_blacklist:
            self.upstream_blacklist = os.path.join(Config.BLACKLIST_LOCATION, self.upstream_blacklist)

        self.thresholds = Thresholds(float(pasta.get('AUTOACCEPT_THRESHOLD')),
                                     float(pasta.get('INTERACTIVE_THRESHOLD')),
                                     float(pasta.get('DIFF_LINES_RATIO')),
                                     float(pasta.get('HEADING_THRESHOLD')),
                                     float(pasta.get('FILENAME_THRESHOLD')),
                                     float(pasta.get('MESSAGE_DIFF_WEIGHT')))

        self.patch_stack_definition = PatchStackDefinition.parse_definition_file(self)

    @property
    def psd(self):
        return self.patch_stack_definition
