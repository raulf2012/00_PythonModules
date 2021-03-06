#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Job automation class.

Author: Raul A. Flores
"""

# | - Import Modules
import os
import shutil
import copy

import itertools
import pickle
import json

import numpy as np
import pandas as pd

import ast

# My Modules
from dft_job_automat.compute_env import ComputerCluster
# __|


class Job:
    """Encapsulates data and method related to single jobs.

    Still a work in progress
    """

    # | - Job ******************************************************************
    def __init__(self,
        path_i=None,
        job_params_dict=None,
        max_revision=None,

        root_dir=None,
        ):
        """COMBAK Flesh this out later.

        Args:
            path_i:
                Path to job folder
            job_params_dict:
                Job parameter dictionary
            max_revision:
                Max revisions for unique job, defined by the set of job params
        """
        # | - __init__

        # | - Setting class attributes
        self.full_path = path_i
        self.job_params_dict = job_params_dict
        self.max_revision = max_revision
        self.root_dir = root_dir
        # __|

        # if job_params_dict is None:

        self.job_params = self.__set_job_parameters__(job_params_dict)

        # print(self.job_params)
        # print("____-d-sfs")
        # print("")

        # else:
        #     self.__write_job_parameters__()

        self.revision_number = self.__revision_number__()
        # __|

    def write_job_parameters(self):
        """
        """
        # | - __write_job_parameters__
        leaf_dir = self.full_path.split("/")[-1]

        if "_" in leaf_dir:
            # if leaf_dir[1:].isnumeric():
            if leaf_dir[1:].isdigit():
                leaf_dir = self.full_path.split("/")[-1]
                ind_i = self.full_path.rfind(leaf_dir)
                path_i = self.full_path[:ind_i - 1]


        # | - NEW | Trying to remove keys which aren't JSON serializable
        def is_jsonable(x):
            """
            """
            # | - is_jsonable
            try:
                json.dumps(x)
                return True
            except:
                return False
            # __|

        job_params_dict_cpy = copy.deepcopy(self.job_params_dict)

        keys_to_delete = []
        for key, value in job_params_dict_cpy.items():
            if not is_jsonable(value):
                keys_to_delete.append(key)

        if len(keys_to_delete) > 0:
            print(
                "The following job properties couldn't be JSON serialized",
                ", and will be ignored"
                )
            print(keys_to_delete)

        for k in keys_to_delete:
            job_params_dict_cpy.pop(k, None)

        print(job_params_dict_cpy)
        # __|


        file_path_i = os.path.join(path_i, "job_params.json")
        with open(file_path_i, 'w') as outfile:
            json.dump(
                job_params_dict_cpy,
                # self.job_params_dict,
                outfile,
                indent=2,
                )
        # __|

    def __set_job_parameters__(self, job_params_dict):
        """

        Args:
            job_params_dict:
        """
        # | - __set_job_parameters__
        job_params_from_file = self.__read_job_params_file__()

        if job_params_dict is not None:
            # job_params_dict.update(job_params_from_file)
            job_params_from_file.update(job_params_dict)

        return(job_params_from_file)
        # __|

    def __read_job_params_file__(self):
        """Read "job_parameters.json" file from job direcory.

        Development Notes:
            Search in the job root dir (one level up from "_" dirs)

        Args:
        """
        # | - __read_job_params_file__
        job_params = {}

        # file_path = self.full_path + "/" + "job_parameters.json"

        file_exists = False

        file_path = os.path.join(
            self.full_path,
            "job_parameters.json")
        if os.path.exists(file_path):
            file_exists = True
            with open(file_path, "r") as fle:
                job_params = json.load(fle)


        ind_i = self.full_path.rfind(self.full_path.split("/")[-1])
        path_i_rt = self.full_path[:ind_i - 1]

        file_path = os.path.join(
            # self.full_path[0:-2],
            path_i_rt,
            "job_parameters.json",
            )
        if os.path.exists(file_path):
            file_exists = True
            with open(file_path, "r") as fle:
                job_params = json.load(fle)


        file_path = os.path.join(
            # self.full_path[0:-2],
            path_i_rt,
            "job_params.json",
            )
        if os.path.exists(file_path):
            file_exists = True
            with open(file_path, "r") as fle:
                job_params = json.load(fle)

        if not file_exists:
            print("No job_params file found for following job:")
            print(self.full_path)

        return(job_params)
        # __|

    def __revision_number__(self):
        """
        """
        # | - __revision_number__
        # print(self.full_path)
        revision_i = int(self.full_path.split("/")[-1].split("_")[-1])

        return(revision_i)
        # __|

    # __| **********************************************************************


class DFT_Jobs_Setup:
    """Useful class to set up multiple DFT job in a directory structure.

    Must be initialized with tree_level and level_entries inputs (Not really)
    """

    # | - DFT_Jobs_Setup *******************************************************

    def __init__(self,
        tree_level=None,
        level_entries=None,
        indiv_dir_lst=None,
        indiv_job_lst=None,
        indiv_job_dict_lst=None,
        skip_dirs_lst=None,
        root_dir=".",
        working_dir=".",
        folders_exist=None,
        parse_all_revisions=True,
        ):
        """Initialize DFT_Jobs_Setup Instance.

        Args:
            tree_level:
            level_entries:
            indiv_dir_lst:
            indiv_job_lst:
                List of dictionaries representing jobs
            skip_dirs_lst:
            working_dir:
            folders_exist:
        """
        # | - __init__

        # | - Initializing Some Class Attributes
        self.order_dict = None
        self.job_var_lst = None
        self.Job_list = []
        self.sep = "-"
        self.level_entries = level_entries
        self.tree_level_labels = tree_level
        self.level_entries_list = level_entries
        self.skip_dirs_lst = skip_dirs_lst
        self.indiv_dir_lst = indiv_dir_lst
        self.indiv_job_lst = indiv_job_lst

        self.indiv_job_dict_lst = indiv_job_dict_lst
        self.parse_all_revisions = parse_all_revisions
        # __|

        self.root_dir = self.__set_root_dir__(root_dir)

        self.working_dir = self.__set_working_dir__(working_dir)

        self.cluster = ComputerCluster()
        self.jobs_att = self.__load_jobs_attributes__()
        self.__create_jobs_bin__()
        self.folders_exist = self.__folders_exist__(folders_exist)

        self.load_dir_struct()
        self.__create_dir_structure_file__()
        self.num_jobs = self.__number_of_jobs__()
        self.__Job_list__()

        self.data_frame = self.__gen_datatable__()

        # if self.folders_exist:
        #     # self.data_frame = self.__generate_data_table__()

        self.check_inputs()
        # __|

    def __job_i_param_dict_to_job_var_lst__(self, params_dict):
        """Constructs a job_variable list from a dictionary of parameters.

        Args:
            params_dict:
        """
        # | - __job_i_param_dict_to_job_var_lst__
        assert self.tree_level_labels is not None

        job_var_lst_i = []
        for level_prop in self.tree_level_labels:
            level_var_dict = {}
            for key_i, value_i in params_dict.items():
                if key_i == level_prop:
                    level_var_dict["property"] = key_i
                    level_var_dict["value"] = value_i

                    job_var_lst_i.append(level_var_dict)
                    break

        return(job_var_lst_i)
        # __|


    def write_job_params_json_file(self):
        """
        """
        # | - write_job_params_json_file
        for Job in self.Job_list:
            Job.write_job_parameters()

        # __|

    def create_Jobs_from_dicts_and_paths(self,
        jobs_list,
        ):
        """Populate Job_list attribute manually.

        Args:
            jobs_list
                List of dictionaries with 'properties' and 'path' keys

        """
        # | - create_Jobs_from_dicts_and_paths
        for job_i in jobs_list:

            path_i = job_i["path"]
            job_params_dict = job_i["properties"]

            rev_dirs, max_rev = self.__revision_list_and_max__(
                path_i,
                )

            for rev_i in rev_dirs:
                path_i = os.path.join(path_i, rev_i)
                path_i = os.path.normpath(path_i)

                Job_i = Job(
                    path_i=path_i,
                    job_params_dict=job_params_dict,
                    max_revision=max_rev,
                    root_dir=None,
                    )

                self.Job_list.append(Job_i)
        # __|

    def __Job_list__(self):
        """Create Job list from various input sources."""
        # | - __Job_list__

        # | - Adding Jobs From Individual Directory List
        if self.indiv_dir_lst is not None:
            for job_i_dir in self.indiv_dir_lst:

                rev_dirs, max_rev = self.__revision_list_and_max__(job_i_dir)

                print(job_i_dir)
                if rev_dirs:

                    print("rev_dirs:", rev_dirs)

                    if self.parse_all_revisions is False:

                        last_rev_int = np.sort(
                                    [int(i.split("_")[-1]) for i in rev_dirs])[-1]
                        rev_dirs = ["_" + str(last_rev_int), ]
                        # rev_dirs = [rev_dirs[-1]]

                        print("rev_dirs:", rev_dirs)
                        print("IOPSDFJOKIDSIJFIJDSF")

                    for rev_i in rev_dirs:
                        path_i = os.path.join(job_i_dir, rev_i)
                        path_i = os.path.normpath(path_i)

                        Job_i = Job(
                            path_i=path_i,
                            job_params_dict=None,
                            max_revision=max_rev,
                            root_dir=None,
                            )

                        self.Job_list.append(Job_i)
                else:
                    print("Didn't find any job dirs here:")
                    print(job_i_dir)
                    pass
        # __|

        # | - Adding Jobs From Enumerated Job Properties Tree
        if self.job_var_lst is not None:
            for job_i in self.job_var_lst:
                job_var_dict = self.__job_i_vars_to_dict__(job_i)

                if self.folders_exist:
                    path_i = self.var_lst_to_path(
                        job_i,
                        job_rev="Auto",
                        relative_path=False,
                        )

                # | - __old__
                # else:
                #     print("else *s8fs*sdf")
                #     path_i = os.path.join(
                #
                #         self.var_lst_to_path(
                #             job_i,
                #             job_rev="Auto",
                #             relative_path=False,
                #             ),
                #
                #         # self.var_lst_to_path(
                #         #     job_i,
                #         #     ),
                #
                #         "_1",
                #         )
                # __|

                rev_dirs, max_rev = self.__revision_list_and_max__(
                    # path_i
                    self.var_lst_to_path(
                        job_i,
                        job_rev="None",
                        relative_path=False,
                        )
                    )

                Job_i = Job(
                    path_i=path_i,
                    job_params_dict=job_var_dict,
                    max_revision=max_rev,
                    root_dir=self.root_dir,
                    )

                self.Job_list.append(Job_i)
        # __|

        # | - TEMP | I don't remember why this is here
        indiv_job = self.indiv_job_lst is not None
        level_labels = self.tree_level_labels is not None
        if indiv_job and level_labels:
            print("LSKDJFKLDS_-09sdfsdfs9dfas")
            for job_params_i in self.indiv_job_lst:

                job_var_lst_i = self.__job_i_param_dict_to_job_var_lst__(
                    job_params_i,
                    )

                path_i = os.path.join(
                    self.new_var_lst_to_path(job_var_lst_i),
                    "_1",
                    )

                Job_i = Job(
                    path_i=path_i,
                    job_params_dict=job_params_i,
                    max_revision=None,
                    root_dir=self.root_dir,
                    )

                self.Job_list.append(Job_i)
        # __|

        if self.indiv_job_dict_lst is not None:
            self.create_Jobs_from_dicts_and_paths(
                self.indiv_job_dict_lst,
                )
        # __|


    # | - Misc Methods

    def __job_i_vars_to_dict__(self, job_i_vars):
        """

        Args:
            job_i_vars:
        """
        # | - __job_i_vars_to_dict__
        job_vars_dict = {}
        for prop in job_i_vars:
            prop_key = prop["property"]
            prop_value = prop["value"]

            job_vars_dict[prop_key] = prop_value

        return(job_vars_dict)
        # __|

    def __create_jobs_bin__(self):
        """Create /jobs_bin folder if it doesn't exist."""
        # | - __create_jobs_bin__
        folder_dir = os.path.join(self.root_dir, self.working_dir, "jobs_bin")
        # folder_dir = self.root_dir + "/jobs_bin"

        if not os.path.exists(folder_dir):
            # print("KDJFDI__")
            # print(folder_dir)
            os.makedirs(folder_dir)
        # __|

    def __folders_exist__(self, folders_exist):
        """Check whether directory structure exists.

        The alternative is to be creating an instance from a location where
        the original job files don't exist but the job dataframe does
        """
        # | - __folders_exist__
        # User override
        if folders_exist is not None:
            return(folders_exist)

        folders_exist = False

        # | - Folders Exist Criteria
        crit_0 = False
        if os.path.isfile(self.root_dir + "/jobs_bin/.folders_exist"):
            crit_0 = True

        crit_1 = False
        if os.path.isdir(self.root_dir + "/data"):
            crit_1 = True
        # __|

        # | - Deciding whether folders exist or not
        if crit_0 is True:
            pass
            if crit_1 is True:
                folders_exist = True
            else:
                folders_exist = False
        else:
            folders_exist = False
        # __|

        return(folders_exist)
        # __|

    def __set_root_dir__(self, root_dir_in):
        """Returns root directory."""
        # | - __set_root_dir__
        if root_dir_in == ".":
            root_dir = os.getcwd()
        else:
            root_dir = root_dir_in

        return(root_dir)
        # __|

    def __set_working_dir__(self, working_dir_in):
        """
        """
        # | - __set_working_dir__
        if working_dir_in == ".":
            working_dir = ""
        else:
            working_dir = working_dir_in

        return(working_dir)
        # __|


    def __check_input__(self):
        """Check that tree_level and level_entries are of matching length."""
        # | - __check_input__
        tmp = set(self.tree_level_labels)
        input_diff = tmp.symmetric_difference(self.level_entries.keys())
        if not input_diff == set():
            undefined_labels = []
            for i in input_diff:
                undefined_labels.append(i)

            print("\n")
            message = "Did not fill out level entries dict properly" + "\n"
            message += "The following properties need to be defined" + "\n"
            message += str(undefined_labels)
            raise ValueError(message)
        # __|


    def __number_of_jobs__(self):
        """Count number of jobs in instance.

        # TODO Should count jobs in job_var_lst and the indiv_dir jobs
        # TODO Make distinction between total jobs (including number of
        revisions) and just the before revision number

        Depends on number of unique variable list and number of revisions for
        each job.
        """
        # | - __number_of_jobs__
        num_jobs = 0

        # Regular jobs
        if self.job_var_lst is not None:
            num_jobs = len(self.job_var_lst)

        # Individual dir jobs
        if self.indiv_dir_lst is not None:
            num_jobs += len(self.indiv_dir_lst)


        return(num_jobs)
        # __|


    def new_var_lst_to_path(self,
        variable_lst,
        job_rev="False",
        relative_path=True,
        ):
        """
        """
        # | - new_var_lst_to_path
        if isinstance(variable_lst, str):
            variable_lst = ast.literal_eval(variable_lst)
        else:
            pass

        level_cnt = 0
        dir_name = "data/"
        for level in variable_lst:
            level_cnt += 1

            if self.level_entries is not None:
                tmp = self.tree_level_labels[level_cnt - 1]
                index = self.level_entries[tmp].index(level["value"]) + 1
                if index < 10:
                    index = "0" + str(index)
                else:
                    index = str(index)

                beggining = index + self.sep

            else:
                index = ""
                beggining = index

            # | - REPLACING PERIODS WITH "p" and NEGATIVE SIGNS WITH "n"
            # if type(level["value"]) == type(1.23):
            if isinstance(level["value"], float):

                # TODO
                # NOTE
                # Replace the line with the commented out line such that floats
                # are rounded in their path representation

                # prop_value = str(round(level["value"], 4)).replace(".", "p")
                prop_value = str(level["value"]).replace(".", "p")

                if "-" in str(level["value"]):
                    prop_value = prop_value.replace("-", "n")

            else:
                prop_value = str(level["value"])
            # __|

            dir_name += beggining + prop_value + "/"

        if job_rev == "Auto":

            revision_dirs, highest_rev = self.__revision_list_and_max__(
                self.var_lst_to_path(variable_lst),
                )

            dir_name += "_" + str(highest_rev)

        if relative_path is False:
            dir_name = os.path.join(
                self.root_dir,
                self.working_dir,
                dir_name,
                )
        else:
            dir_name = os.path.join(
                self.working_dir,
                dir_name,
                )

        return(dir_name)
        # __|

    def var_lst_to_path(self,
        variable_lst,
        job_rev="False",
        relative_path=True,
        ):
        """Construct path string from variable list.

        Args:
            variable_lst: <type 'list'>
                Produced from DFT_Jobs_Setup.job_var_lst.
            job_rev: <type 'str'>
                False:
                Auto:
        """
        # | - var_lst_to_path
        if isinstance(variable_lst, str):
            variable_lst = ast.literal_eval(variable_lst)
        else:
            pass

        level_cnt = 0
        dir_name = "data/"
        for level in variable_lst:
            level_cnt += 1
            tmp = self.tree_level_labels[level_cnt - 1]
            index = self.level_entries[tmp].index(level["value"]) + 1
            if index < 10: index = "0" + str(index)
            else: index = str(index)

            # | - REPLACING PERIODS WITH "p" and NEGATIVE SIGNS WITH "n"
            # if type(level["value"]) == type(1.23):
            if isinstance(level["value"], float):
                prop_value = str(level["value"]).replace(".", "p")

                if "-" in str(level["value"]):
                    prop_value = prop_value.replace("-", "n")

            else:
                prop_value = str(level["value"])
            # __|

            dir_name += index + self.sep + prop_value + "/"

        # Removing the trailing '/' character
        dir_name = dir_name[:-1]

        if job_rev == "Auto":

            revision_dirs, highest_rev = self.__revision_list_and_max__(
                self.var_lst_to_path(
                    variable_lst,
                    job_rev="False",
                    relative_path=False,
                    ),
                )

            # dir_name += "_" + str(highest_rev)
            dir_name += "/_" + str(highest_rev)

        if relative_path is False:
            dir_name = os.path.join(
                self.root_dir,
                self.working_dir,
                dir_name,
                )

        return(dir_name)
        # __|

    def extract_prop_from_var_lst(self, variable_lst, property):
        """Extract the property from the variable list.

        Args:
            variable_lst:
            property:
        """
        # | - extract_prop_from_var_lst
        # result = {}
        for i in variable_lst:
            if i["property"] == property:
                return i["value"]
        # __|


    # __|


    # | - Job Variable Tree Methods

    def load_dir_struct(self):
        """Attempt to load dir structure from file in root dir if none given.

        job_var_lst is constructed
        level_entries_list is constructed
        level_entries is constructed
        order_dict is constructed

        """
        # | - load_dir_struct
        if self.tree_level_labels is None and self.level_entries is None:
            self.__load_dir_structure_file__()

        # self.__check_input__()  # TEMP had to comment out because of switching
        # to new format of input files

        # | - If tree_level_labels and level_entries couldn't be parsed
        if self.tree_level_labels is None and self.level_entries is None:
            return(None)
        # __|

        # FIXME
        # if not type(self.level_entries) == list:
        #     # self.level_entries_list = self.__level_entries_list__()
        #     level_entries_list = self.__level_entries_list__()

        if type(self.level_entries) == dict:
            # | - OLD way
            self.order_dict = self.__order_dict__(
                self.tree_level_labels,
                self.level_entries)

            self.job_var_lst = self.__job_variable_list__(
                # self.level_entries_list,
                level_entries_list,
                self.order_dict)
            # __|

        elif type(self.level_entries) == list:
            # | - New Way of Inputing Structure Files
            tmp = self.__create_level_entries_dict__(
                self.tree_level_labels,
                self.level_entries,
                )
            self.level_entries = tmp


            self.level_entries_list = self.__level_entries_list__()


            self.order_dict = self.__order_dict__(
                self.tree_level_labels,
                self.level_entries)

            self.job_var_lst = self.__job_variable_list__(
                # self.level_entries,
                self.level_entries_list,
                # level_entries_list,
                self.order_dict,
                )
            # __|

        # __|

    def __load_dir_structure_file__(self):
        """Attempt o load dir_structure.json from file."""
        # | - __load_dir_structure_file__
        try:
            try:
                fle_name = self.root_dir + "/jobs_bin/dir_structure.json"

                with open(fle_name, "r") as dir_struct_f:
                    data = json.load(dir_struct_f)

                    tree_level = data["tree_level_labels"]
                    level_entries = data["level_entries_dict"]

                    if "skip_dirs" in data.keys():
                        skip_dirs_lst = data["skip_dirs"]
                        self.skip_dirs_lst = skip_dirs_lst

                    self.tree_level_labels = tree_level
                    self.level_entries = level_entries
                    self.level_entries_list = level_entries

            except:
                print("Couldn't read /jobs_bin/dir_structure.json")

                try:

                    # | - __old__
                    tmp = 42
                    # print("old - Reading dir_structure.json file \
                    #     from root_dir")
                    #
                    # fle_name = self.root_dir + "/dir_structure.json"
                    # with open(fle_name, "r") as dir_struct_f:
                    #     data = json.load(dir_struct_f)
                    #     tree_level = data["tree_level_labels"]
                    #     level_entries = data["level_entries_dict"]
                    #
                    #     if "skip_dirs" in data.keys():
                    #         skip_dirs_lst = data["skip_dirs"]
                    #         self.skip_dirs_lst = skip_dirs_lst
                    #
                    #     self.tree_level_labels = tree_level
                    #     self.level_entries = level_entries
                    # __|

                except:
                    print("Couldn't read /dir_structure.json")

                    pass

        except:
            mess = "Error opening 'dir_structure.json' file"
            raise IOError(mess)

        # __|

    def __create_level_entries_dict__(self,
        tree_level_labels,
        tree_level_values,
        ):
        """
        Create level_entries_dict from labels and values lists.

        Args:
            tree_level_labels:
            tree_level_values:
        """
        # | - create_level_entries_dict
        level_entries_dict = {}
        for index, variable in enumerate(tree_level_labels):
            level_entries_dict[variable] = tree_level_values[index]

        return(level_entries_dict)
        # __|

    def __level_entries_list__(self):
        """Construct level entries list.

        Construct level_entries_list from level_entries_dict and level_labels
        """
        # | - __level_entries_list__
        level_entries_dict = self.level_entries
        level_labels = self.tree_level_labels

        level_entries_list = []
        for param_i in level_labels:
            # for name, params_list in level_entries_dict.iteritems():
            for name, params_list in level_entries_dict.items():
                if param_i == name:
                    level_entries_list.append(params_list)

        return(level_entries_list)
        # __|

    def __order_dict__(self, tree_level_labels, level_entries):
        """Order of properties to correspond to order of tree.

        Creates "order_dict", which contains the depth level for each
        descriptor. Each job directory will have a unique descriptor list.
        The "order_dict" variable is used to make sure that the ordering of the
        descriptors in this list matches the "dir_tree_level" structure.

        Args:
            tree_level_labels:
            level_entries:
        """
        # | - __order_dict__
        order_dict = {}  # <--------------------------------------

        level_cnt = 0
        for level in tree_level_labels:
            level_cnt += 1
            for prop in level_entries[level]:
                order_dict[prop] = level_cnt - 1

        return order_dict

        # __|

    def __job_variable_list__(self, level_entries, order_dict):
        """Return the job variable list.

        Args:
            level_entries:
            order_dict:
        """
        # | - __job_variable_list__
        all_comb = itertools.product(*level_entries)

        job_dir_lst = []
        for job_dir in all_comb:
            final_lst_2 = []
            param_names = self.tree_level_labels

            for ind, prop in enumerate(job_dir):
                new_entry = {}
                new_entry["property"] = param_names[ind]
                new_entry["value"] = job_dir[ind]
                final_lst_2.append(new_entry)

            job_dir_lst.append(final_lst_2)

        if self.skip_dirs_lst is not None:
            for skip in self.skip_dirs_lst:
                job_dir_lst.remove(skip)

        return(job_dir_lst)
        # __|

    # __|


    # | - Create Directory Tree

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    # NEW
    def create_dir_struct(self, create_first_rev_folder="True"):
        """Create directory structure according to job variable list & dict.

        Development Notes:
            This should really be looping over the jobs_list I think

        Args:
            create_first_rev_folder:
        """
        # | - create_dir_struct
        for Job_i in self.Job_list:

            # | - FOR LOOP BODY
            # if create_first_rev_folder == "True":
            #     path = os.path.join(Job_i.full_path, "_1")
            # elif create_first_rev_folder == "False":
            #     path = Job_i.full_path

            path = Job_i.full_path

            if os.path.exists(path):
                # mess = "Path already exists: " + str(path)
                # print(mess)
                pass

            elif not os.path.exists(path):
                os.makedirs(path)
            # __|

        # | - folders_exist attribute should be True from now on
        # file_name = self.root_dir + "/jobs_bin/.folders_exist"
        file_name = os.path.join(
            self.root_dir,
            self.working_dir,
            "jobs_bin/.folders_exist"
            )

        with open(file_name, "w") as fle:
            fle.write("\n")

        self.folders_exist = self.__folders_exist__(True)
        # __|

        # __|

    def old_create_dir_struct(self, create_first_rev_folder="True"):
        """Create directory structure according to job variable list & dict.

        Development Notes:
            This should really be looping over the jobs_list I think

        Args:
            create_first_rev_folder:
        """
        # | - create_dir_struct
        for job in self.job_var_lst:
            if create_first_rev_folder == "True":
                path = self.var_lst_to_path(job) + "_1"
            elif create_first_rev_folder == "False":
                path = self.var_lst_to_path(job)

            path = self.root_dir + "/" + path

            if os.path.exists(path):
                mess = "Path already exists: " + str(path)
                print(mess)

            elif not os.path.exists(path):
                os.makedirs(path)

        # | - Creating Variable Text Files Through Directoy Structure
        for job in self.job_var_lst:
            path = self.var_lst_to_path(job)
            path = self.root_dir + "/" + path

            file_name = path + "job_dir_level"
            with open(file_name, "w") as fle:
                fle.write("\n")

        for root, dirs, files in os.walk(self.root_dir + "/data/"):
            if "job_dir_level" in files:
                continue

            else:
                prop_lst = []
                for folder in dirs:
                    tmp = self.sep.join(folder.split(self.sep)[1:])

                    prop = self.__replace_p_for_per__(tmp)
                    prop = self.__replace_negative_for_n__(prop)
                    prop_lst.append(prop)

                for key, value in self.level_entries.items():
                    if set(prop_lst) == set(map(str, value)):

                        file_name = root + "/properties.txt"
                        with open(file_name, "w") as fle:
                            fle.write(key + "\n")

                        # f = open(root + "/properties.txt", "w")
                        # f.write(key + "\n")
                        # f.close()
        # __|

        # self.__create_dir_structure_file__()

        # | - folders_exist attribute should be True from now on
        file_name = self.root_dir + "/jobs_bin/.folders_exist"
        with open(file_name, "w") as fle:
            fle.write("\n")

        self.folders_exist = self.__folders_exist__(True)
        # __|

        # __|











    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!







    def check_inputs(self):
        """
        """
        # | - check_inputs
        if self.tree_level_labels is not None:
            assert isinstance(self.tree_level_labels[0], np.ndarray) is False, \
                "Please don't use numpy array types, can't be json serialized"

        if self.level_entries_list is not None:
            assert isinstance(self.level_entries_list[0], np.ndarray) is False, \
                "Please don't use numpy array types, can't be json serialized"
        # __|

    def __create_dir_structure_file__(self):
        """
        Create directory structure file.

        Creates dir structure file from which the parameter list & dict can be
        loaded from.
        """
        # | - __create_dir_structure_file__

        dir_structure_data = {}
        dir_structure_data["tree_level_labels"] = self.tree_level_labels
        dir_structure_data["level_entries_dict"] = self.level_entries_list
        # TEMP
        dir_structure_data["skip_dirs"] = self.skip_dirs_lst

        fle_name = os.path.join(
            self.root_dir,
            self.working_dir,
            "jobs_bin/dir_structure.json",
            )

        with open(fle_name, "w") as fle:
            json.dump(dir_structure_data, fle, indent=2)
        # __|

    def __replace_p_for_per__(self, text):
        """Replace p in variable with "." character.

        TODO Fails if last letter is a "p"

        Variables with "." character had them previously replaced with a "p"
        character to avoid periods in a folder name.
        """
        # | - __replace_p_for_per__
        lst = [pos for pos, char in enumerate(text) if char == "p"]

        # Replaces character at lett with a period if both the previous
        # and next character are numeric
        for lett in lst:

            # COMBAK
            # Skip entries which have p at end of text
            # Ignores possibility of variables like the following:
            # 2. --> 2p (will not go back to 2.)
            if lett == len(text) - 1:
                continue

            cond_1 = text[lett - 1].isdigit()
            cond_2 = text[lett + 1].isdigit()
            if cond_1 is True and cond_2 is True:
                text = text[:lett] + "." + text[lett + 1:]

        return(text)
        # __|

    def __replace_negative_for_n__(self, text):
        """Replace variable quantities that are negative with an "n".

        Args:
            text:
        """
        # | - __replace_negative_for_n__
        lst = [pos for pos, char in enumerate(text) if char == "n"]

        for lett in lst:
            if text[lett + 1].isdigit() is True:
                text = text[:lett] + "-" + text[lett + 1:]

        return(text)
        # __|

    # __|


    # | - Job Attributes

    def __load_jobs_attributes__(self):
        """Load jobs attributes data from file."""
        # | - __load_jobs_attributes__
        job_att_file = self.root_dir + "/jobs_bin/job_attributes.csv"

        if os.path.exists(job_att_file):
            with open(job_att_file, "rb") as fle:
                jobs_att = pickle.load(fle)

        else:
            jobs_att = {}

        return(jobs_att)
        # __|

    def append_jobs_attributes(self, attribute):
        """
        Append to jobs attributes file.

        Append dictionary key value pair to the jobs_attributes dict.
        To be pickled and saved
        """
        # | - append_jobs_attributes
        att_new = attribute

        self.jobs_att.update(att_new)

        job_att_file = self.root_dir + "/jobs_bin/job_attributes.csv"
        pickle.dump(self.jobs_att, open(job_att_file, "wb"))
        # __|

    # __|

    def __gen_datatable__(self):
        """Initialze data table from the properties of the jobs directory.

        New methods iterates through Job instances
        """
        # | - __generate_data_table
        rows_list = []
        for Job_i in self.Job_list:
            # | - FOR LOOP BODY
            entry_param_dict = {}
            for prop, value in Job_i.job_params.items():
                entry_param_dict[prop] = value

            entry_param_dict["Job"] = Job_i
            entry_param_dict["path"] = Job_i.full_path
            entry_param_dict["max_revision"] = Job_i.max_revision
            entry_param_dict["revision_number"] = Job_i.revision_number

            rows_list.append(entry_param_dict)
            # __|

        data_frame = pd.DataFrame(rows_list)

        return(data_frame)
        # __|

    def __revision_list_and_max__(self, path_i):
        """Return list of revisions for given job path and highest revision.

        If there are no revision folders or the directory structure hasn't been
        created yet the following dummy values will be returned:
            (
                ["_1"],
                1,
                )

        Args:
            path_i:
        """
        # | - __revision_list_and_max__
        if self.folders_exist:

            # dirs = os.listdir(os.path.join(self.working_dir, path_i))
            dirs = os.listdir(path_i)

            revision_dirs = [dir for dir in dirs if dir[0] == "_" and
                dir[-1].isdigit() and " " not in dir]

            # dir[1].isdigit() and " " not in dir]

            revision_dirs.sort()

            if len(revision_dirs) == 0:
                highest_rev = None
            else:
                highest_rev = max(
                    [int(i.split("_")[-1]) for i in revision_dirs],
                    )

            return(revision_dirs, highest_rev)
        else:
            dummy_return = (
                ["_1"],
                1,
                )

            return(dummy_return)
        # __|

    def copy_files_jd(self, file_list, variable_lst, revision="Auto"):
        """
        Copy files to job directory.

        Args:
            file_list:
            variable_lst:
            revision:
        """
        # | - copy_files_jd
        path = self.var_lst_to_path(variable_lst)
        path += "_" + str(self.job_revision_number(variable_lst))

        for file in file_list:
            shutil.copyfile(self.root_dir + "/" + file, path + "/" + file)
        # __|


    # __| **********************************************************************



    # | - __old__
    # DEPR
    def __generate_data_table__(self):
        """Initialze data table from the properties of the jobs directory.

        Appends unique row for every job revision
        """
        # | - __generate_data_table__
        rows_list = []
        for job in self.job_var_lst:
            revisions = self.job_revision_number(job)
            for revision in range(revisions + 1)[1:]:
                # | - FOR LOOP BODY
                entry_param_dict = {}
                for prop in job:
                    entry_param_dict[prop["property"]] = prop["value"]

                entry_param_dict["variable_list"] = job
                entry_param_dict["path"] = self.var_lst_to_path(job)

                entry_param_dict["max_revision"] = revisions
                entry_param_dict["revision_number"] = revision

                rows_list.append(entry_param_dict)
                # __|

        data_frame = pd.DataFrame(rows_list)

        return(data_frame)
        # __|

    # DEPR
    def job_revision_number_old(self, variable_lst):
        """
        Return the largest revision number for the given variable_lst -> job.

        If there are no revision folders or the directory structure hasn't been
        created yet 1 will be returned.

        Args:
            variable_lst:
        """
        # | - job_revision_number
        if self.folders_exist:
            path = self.var_lst_to_path(variable_lst)
            orig_dir = os.getcwd()
            os.chdir(self.root_dir + "/" + path)

            dirs = filter(os.path.isdir, os.listdir(os.getcwd()))


            # COMBAK Does this line break work?
            num_jobs = len([dir for dir in dirs if dir[0] == "_" and
                dir[1].isdigit() and " " not in dir])
            os.chdir(orig_dir)

            return(num_jobs)
        else:
            return(1)

        # | - __old__
        # path = self.var_lst_to_path(variable_lst)
        #
        # path = "/".join(path.split("/")[0:-1]) + "/"
        # # Attempting to remove duplicate job folders (usually have spaces)
        # dir_list = [x for x in os.walk(path).next()[1] if " " not in x]
        #
        # return(len(dir_list))
        #
        # __|

        # __|


    # __|
