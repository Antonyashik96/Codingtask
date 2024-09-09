# Task- 1
Create folders in the given folder path on remote host recursively

# Task- 2
Check existance of folder

# Class Node - Task-1
When creating folder structures for different projects the number of folders, subfolders and the hierarchy of subfolders may vary. To handle this
dynamically depending upon the requirement, the concept of **nodes** is implemented in **class Node** in **Plus4Data.py** file.

**contents**
1. **Plus4Data.py**\
   1.1 **class Node**\
   1.2 **class RemoteFolderManager**\
      1.2.1 **def set_defaults**\
      1.2.2 **def connect_to_sftp**\
      1.2.3 **def check_whether_base_path_exists_or_not**\
      1.2.4 **def check_whether_given_folder_is_symlink**\
      1.2.5 **def create_folders_from_node_tree_recursively**\
      1.2.6 **def create_folder_path_recursively (task 1)**\
      1.2.7 **def is_path_a_regular_folder (task 2)**

2. **main.py**



**Architecture**   

The folder tree architecture implemented in this code for Task-1 to create folders recursively is shown below in **folder_tree.png**.

<div style="text-align: center;">
  <img src="./folder_tree.png" alt="Alt text" width="550"/>
</div>

The same **class Node** can be used for any dynamic folder structure creation.

The architecture for task 1 and task 2 that has been implemented is shown  below visually in **task.png**.

<div style="text-align: center;">
  <img src="./task.png" alt="Alt text" width="550"/>
</div>

**Steps to execute**\
1. `git clone repo`
2. `Pip install requirements.txt`
3. python 3 main.py

