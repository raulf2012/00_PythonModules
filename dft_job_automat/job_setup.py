"""Job automation class."""

#| - Import Modules
import itertools
import os
import pickle
import json
import shutil
import pandas as pd
import ast

# My Modules
from dft_job_automat.compute_env import ComputerCluster
#__|


class Job:
    """
    Encapsolates data and method related to single jobs.

    Still a work in progress
    """

    #| - Job ******************************************************************

    def __init__(self):
        """COMBAK Flesh this out later.

        Still a lot of work todo here
        """
        #| - __init__
        tmp = 42
        print(tmp)
        #__|

    #__| **********************************************************************

class DFT_Jobs_Setup:
    """
    Useful class to set up multiple DFT job in a directory structure.

    Must be initialized with tree_level and level_entries inputs
    """

    #| - DFT_Jobs_Setup *******************************************************

    def __init__(self,
        system="aws",
        tree_level=None,
        level_entries=None,
        skip_dirs_lst=None,
        working_dir=".",
        ):
        """Initialize DFT_Jobs_Setup Instance.

        Args:
            system:
            tree_level:
            level_entries:
            skip_dirs_lst:
            working_dir:
        """
        #| - __init__

        #| - Setting Path Variables
        if working_dir == ".":
            self.root_dir = os.getcwd()
        else:
            self.root_dir = working_dir
        try:
            self.aws_dir = os.environ["TRI_PATH"]
            self.job_queue_dir = self.aws_dir + "/bin/job_queues"
        except:
            pass
        #__|

        self.cluster = ComputerCluster()

        self.jobs_att = self.__load_jobs_attributes__()

        # TEMP
        self.__tmp_create_jobs_bin__()
        self.folders_exist = self.__folders_exist__()
        self.system = system
        self.sep = "-"
        self.tree_level_labels = tree_level
        self.level_entries_list = level_entries
        self.level_entries = level_entries

        # TEMP
        self.skip_dirs_lst = skip_dirs_lst
        self.load_dir_struct()
        self.num_jobs = self.__number_of_jobs__()

        if self.folders_exist is True:
            self.data_frame = self.__generate_data_table__()
        #__|

    def __tmp_create_jobs_bin__(self):
        """Create /jobs_bin folder if it doesn't exist."""
        #| - __tmp_create_jobs_bin__
        folder_dir = self.root_dir + "/jobs_bin"
        if not os.path.exists(folder_dir):
            os.makedirs(folder_dir)
        #__|

    def __folders_exist__(self):
        """Check whether directory structure exists."""
        #| - __folders_exist__
        folders_exist = False

        #| - Folders Exist Criteria
        crit_0 = False
        if os.path.isfile(self.root_dir + "/jobs_bin/.folders_exist"):
            crit_0 = True

        crit_1 = False
        if os.path.isdir(self.root_dir + "/data"):
            crit_1 = True
        #__|

        #| - Deciding whether folders exist or not
        if crit_0 is True:
            pass
            if crit_1 is True:
                folders_exist = True
            else:
                folders_exist = False
        else:
            folders_exist = False
        #__|

        return(folders_exist)
        #__|

    def load_dir_struct(self):
        """Attempt to load dir structure from file in root dir if none given.

        TEMP TEMP
        """
        #| - load_dir_struct
        if self.tree_level_labels is None and self.level_entries is None:

            #| - __old__
            # with open(self.root_dir + "/jobs_bin/dir_structure.json", "r")
            # as dir_struct_f:
            #     data = json.load(dir_struct_f)
            #     tree_level = data["tree_level_labels"]
            #     level_entries = data["level_entries_dict"]
            #
            #     if "skip_dirs" in data.keys():
            #         skip_dirs_lst = data["skip_dirs"]
            #         self.skip_dirs_lst = skip_dirs_lst
            #
            #     self.tree_level_labels = tree_level
            #
            #     self.level_entries = level_entries
            #__|

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
                except:
                    try:
                        #| - __old__
                        print("old - Reading dir_structure.json file \
                            from root_dir")

                        fle_name = self.root_dir + "/dir_structure.json"
                        with open(fle_name, "r") as dir_struct_f:
                            data = json.load(dir_struct_f)
                            tree_level = data["tree_level_labels"]
                            level_entries = data["level_entries_dict"]

                            if "skip_dirs" in data.keys():
                                skip_dirs_lst = data["skip_dirs"]
                                self.skip_dirs_lst = skip_dirs_lst

                            self.tree_level_labels = tree_level
                            self.level_entries = level_entries
                        #__|

                    except:
                        pass

            except:
                mess = "Error opening 'dir_structure.json' file"
                raise IOError(mess)


        # self.__check_input__()  # TEMP had to comment out because of switching
        # to new format of input files

        # FIXME
        if not type(self.level_entries) == list:
            self.level_entries_list = self.__level_entries_list__()


        if type(self.level_entries) == dict:
            #| - OLD way
            self.order_dict = self.__order_dict__(
                self.tree_level_labels,
                self.level_entries)

            self.job_var_lst = self.__job_variable_list__(
                self.level_entries_list,
                self.order_dict)
            #__|

        elif type(self.level_entries) == list:
            #| - New Way of Inputing Structure Files
            tmp = self.__create_level_entries_dict__(
                self.tree_level_labels,
                self.level_entries,
                )
            self.level_entries = tmp

            self.order_dict = self.__order_dict__(
                self.tree_level_labels,
                self.level_entries)

            self.job_var_lst = self.__job_variable_list__(
                # self.level_entries,
                self.level_entries_list,
                self.order_dict)
            #__|

        self.level_entries_list = self.__level_entries_list__()

        #__|

    def __level_entries_list__(self):
        """
        Construct level entries list.

        Construct level_entries_list from level_entries_dict and level_labels
        """
        #| - level_entries_list
        level_entries_dict = self.level_entries
        level_labels = self.tree_level_labels

        level_entries_list = []
        for param_i in level_labels:
            for name, params_list in level_entries_dict.iteritems():
                if param_i == name:
                    level_entries_list.append(params_list)

        return(level_entries_list)
        #__|

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
        #| - create_level_entries_dict
        level_entries_dict = {}
        for index, variable in enumerate(tree_level_labels):
            level_entries_dict[variable] = tree_level_values[index]

        return(level_entries_dict)
        #__|

    def __check_input__(self):
        """Check that tree_level and level_entries are of matching length."""
        #| - __check_input__
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
        #__|

    def create_dir_structure_file(self):
        """
        Create directory structure file.

        Creates dir structure file from which the parameter list & dict can be
        loaded from.
        """
        #| - create_dir_structure_file
        dir_structure_data = {}
        dir_structure_data["tree_level_labels"] = self.tree_level_labels
        dir_structure_data["level_entries_dict"] = self.level_entries
        # TEMP
        dir_structure_data["skip_dirs"] = self.skip_dirs_lst

        with open(self.root_dir + "/jobs_bin/dir_structure.json", "w") as f:
            json.dump(dir_structure_data, f, indent=2)
        #__|

    def __load_jobs_attributes__(self):
        """Load jobs attributes data from file."""
        #| - __load_jobs_attributes__
        job_att_file = self.root_dir + "/jobs_bin/job_attributes.csv"

        if os.path.exists(job_att_file):
            with open(job_att_file, "rb") as fle:
                jobs_att = pickle.load(fle)

        else:
            jobs_att = {}

        return(jobs_att)
        #__|

    def append_jobs_attributes(self, attribute):
        """
        Append to jobs attributes file.

        Append dictionary key value pair to the jobs_attributes dict.
        To be pickled and saved
        """
        #| - append_jobs_attributes
        att_new = attribute

        self.jobs_att.update(att_new)

        job_att_file = self.root_dir + "/jobs_bin/job_attributes.csv"
        pickle.dump(self.jobs_att, open(job_att_file, "wb"))
        #__|

    def replace_p_for_per(self, text):
        """Replace p in variable with "." character."""
        #| - replace_p_for_per
        lst = [pos for pos, char in enumerate(text) if char == "p"]

        for lett in lst:

            # if text[lett - 1].isdigit() is True and \
            #     text[lett + 1].isdigit() is True:

            cond_1 = text[lett - 1].isdigit()
            cond_2 = text[lett + 1].isdigit()
            if cond_1 is True and cond_2 is True:
                text = text[:lett] + "." + text[lett + 1:]

        return(text)
        #__|

    def replace_negative_for_n(self, text):
        """Replace variable quantities that are negative with an "n"."""
        #| - replace_negative_for_n
        lst = [pos for pos, char in enumerate(text) if char == "n"]

        for lett in lst:
            if text[lett + 1].isdigit() is True:
                text = text[:lett] + "-" + text[lett + 1:]

        return(text)
        #__|

    def create_dir_struct(self, create_first_rev_folder="True"):
        """
        Create directory structure according to job variable list & dict.

        Args:
            create_first_rev_folder:
        """
        #| - create_dir_struct
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

        #| - Creating Variable Text Files Through Directoy Structure
        for job in self.job_var_lst:
            path = self.var_lst_to_path(job)
            path = self.root_dir + "/" + path

            f = open(path + "job_dir_level", "w")
            f.close()

        for root, dirs, files in os.walk("./data/"):
            if "job_dir_level" in files:
                continue

            else:
                prop_lst = []
                for folder in dirs:
                    tmp = self.sep.join(folder.split(self.sep)[1:])
                    prop = self.replace_p_for_per(tmp)
                    prop = self.replace_negative_for_n(prop)
                    prop_lst.append(prop)

                for key, value in self.level_entries.items():

                    if set(prop_lst) == set(map(str, value)):
                        f = open(root + "/properties.txt", "w")
                        f.write(key + "\n")
                        f.close()

        #__|

        #| - Writing Directory Structure File

        self.create_dir_structure_file()

        # dir_structure_data = {}
        # dir_structure_data["tree_level_labels"] = self.tree_level_labels
        # dir_structure_data["level_entries_dict"] = self.level_entries
        # #
        # # with open("dir_structure.json", "w") as f:
        # #     json.dump(dir_structure_data, f)
        # #
        # with open("jobs_bin/dir_structure.json", "w") as f:
        #     json.dump(dir_structure_data, f)
        #__|

        f = open(self.root_dir + "/jobs_bin/.folders_exist", "w")
        f.write("\n")
        f.close()
        #__|

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
        #| - __order_dict__
        order_dict = {}  # <--------------------------------------

        level_cnt = 0
        for level in tree_level_labels:
            level_cnt += 1
            for prop in level_entries[level]:
                order_dict[prop] = level_cnt - 1

        return order_dict

        #__|

    def __job_variable_list__(self, level_entries, order_dict):
        """
        TEMP.

        # TODO  - This messes up when the level entries are  the same (FIX)
        # UPDATE - Tried to fix, check that it works ok

        Args:
            level_entries:
            order_dict:
        """
        #| - __job_variable_list__
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
        #__|

    def __number_of_jobs__(self):
        """
        Count number of jobs in instance.

        Depends on number of unique variable list and number of revisions for
        each job.
        """
        #| - __number_of_jobs__
        num_jobs = len(self.job_var_lst)
        return(num_jobs)
        #__|

    def var_lst_to_path(self,
        variable_lst,
        job_rev="False",
        relative_path=True,
        ):
        """
        Construct path string from variable list.

        Args:
            variable_lst: <type 'list'>
                Produced from DFT_Jobs_Setup.job_var_lst.
            job_rev: <type 'str'>
                False:
                Auto:
        """
        #| - var_lst_to_path
        # if type(variable_lst) == type("str"):
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

            #| - REPLACING PERIODS WITH "p" and NEGATIVE SIGNS WITH "n"
            # if type(level["value"]) == type(1.23):
            if isinstance(level["value"], float):
                prop_value = str(level["value"]).replace(".", "p")

                if "-" in str(level["value"]):
                    prop_value = prop_value.replace("-", "n")

            else:
                prop_value = str(level["value"])
            #__|

            dir_name += index + self.sep + prop_value + "/"

        if job_rev == "Auto":
            rev = self.job_revision_number(variable_lst)
            dir_name += "_" + str(rev)

        if relative_path is False:
            dir_name = self.root_dir + "/" + dir_name

        return(dir_name)
        #__|

    def extract_prop_from_var_lst(self, variable_lst, property):
        """Extract the property from the variable list.

        Args:
            variable_lst:
            property:
        """
        #| - extract_prop_from_var_lst
        # result = {}
        for i in variable_lst:
            if i["property"] == property:
                return i["value"]
        #__|

    def __generate_data_table__(self):
        """
        Initialze data table from the properties of the jobs directory.

        Appends unique row for every job revision
        """
        #| - __generate_data_table__
        rows_list = []
        for job in self.job_var_lst:
            revisions = self.job_revision_number(job)
            for revision in range(revisions + 1)[1:]:
                #| - FOR LOOP BODY
                entry_param_dict = {}
                for prop in job:
                    entry_param_dict[prop["property"]] = prop["value"]

                entry_param_dict["variable_list"] = job
                entry_param_dict["path"] = self.var_lst_to_path(job)

                # matrio_ind = self.root_dir.split("/").index("matr.io")
                # path = "/".join(self.root_dir.split("/")[matrio_ind + 2:])
                # entry_param_dict["root_dir"] = path

                entry_param_dict["max_revision"] = revisions
                entry_param_dict["revision_number"] = revision

                rows_list.append(entry_param_dict)
                #__|

        data_frame = pd.DataFrame(rows_list)

        return(data_frame)
        #__|

    def job_revision_number(self, variable_lst):
        """
        Return the largest revision number for the given variable_lst -> job.

        If there are no revision folders or the directory structure hasn't been
        created yet 1 will be returned.

        Args:
            variable_lst:
        """
        #| - job_revision_number
        if self.folders_exist:
            path = self.var_lst_to_path(variable_lst)
            orig_dir = os.getcwd()
            os.chdir(self.root_dir + "/" + path)

            dirs = filter(os.path.isdir, os.listdir(os.getcwd()))

            # system = self.cluster.cluster_sys

            #| - __old__
            # if system == "sherlock":
            #     num_jobs = len([dir for dir in dirs if dir[0] == "_"
            # and dir[1].isdigit() and " " not in dir])
            # elif system == "aws":
            #     num_jobs = len([dir for dir in dirs if dir[0] == "_"
            # and dir[1].isdigit() and " " not in dir])
            #__|

            # COMBAK Does this line break work?
            num_jobs = len([dir for dir in dirs if dir[0] == "_" and
                dir[1].isdigit() and " " not in dir])
            os.chdir(orig_dir)

            return(num_jobs)
        else:
            return(1)

        #| - __old__
        # path = self.var_lst_to_path(variable_lst)
        #
        # path = "/".join(path.split("/")[0:-1]) + "/"
        # # Attempting to remove duplicate job folders (usually have spaces)
        # dir_list = [x for x in os.walk(path).next()[1] if " " not in x]
        #
        # return(len(dir_list))
        #
        #__|

        #__|

    def copy_files_jd(self, file_list, variable_lst, revision="Auto"):
        """
        Copy files to job directory.

        Args:
            file_list:
            variable_lst:
            revision:
        """
        #| - copy_files_jd
        path = self.var_lst_to_path(variable_lst)
        path += "_" + str(self.job_revision_number(variable_lst))

        for file in file_list:
            shutil.copyfile(self.root_dir + "/" + file, path + "/" + file)

        #__|

    #__| **********************************************************************
