import paramiko
import logging
import typing
from typing import Union,List
from pathlib import Path
number_of_folders_created_using_recursion = 0

class Node:
    '''
    Node class to provide flexibility in creating folders, subfolders of varying depth and files depending upon the project requirement.
    '''
    def __init__(self, name, subfolders=None, is_file=False):
        self.name = name
        self.is_file = is_file
        self.subfolders = subfolders or []

    def __str__(self, level=0):
        prefix = '  ' * level + ('[FILE] ' if self.is_file else '[DIR] ')
        result = f"{prefix}{self.name}\n"
        for child in self.subfolders:
            result += child.__str__(level + 1)
        return result

class RemoteFolderManager:
    
    default_host_path = ''
    hierarchy_of_folders_to_be_created_inside_root_folder_path = None
    hostname = '' 
    username = ''
    password =''
    port = 22

    @classmethod
    def set_defaults(cls, host_path: typing.Optional[str] = None, hierarchy_of_folders_to_be_created_inside_root_folder_path: Node=None,\
                      hostname:str=None, username:str=None, password:str=None):
        '''
            Function to update the default values inside the class.
            Args:
            host_path: The path of the remote host in which the operations are to be performed.
            hierarchy_of_folders_to_be_created_inside_root_folder_path: The hierarchical structure of folders, subfolders that are 
            to be created inside host_path. which is initialized using Node class. 

            hostname: The hostname or IP address of the remote server.
            username: The username to log in to the remote server.
            password: The password for the remote server.
        '''
        # Update only the provided defaults
        if host_path is not None:
            cls.default_host_path = host_path
        if hierarchy_of_folders_to_be_created_inside_root_folder_path is not None:
            cls.hierarchy_of_folders_to_be_created_inside_root_folder_path = hierarchy_of_folders_to_be_created_inside_root_folder_path
        if hostname is not None:
            cls.hostname = hostname
        if username is not None:
            cls.username = username
        if password is not None:
            cls.password = password
        
    @classmethod
    def connect_to_sftp(
        cls,
        logger: typing.Union[None, logging.Logger] = None
    ) -> paramiko.SFTPClient:
        """
        Establish an SFTP connection to the remote host.
        
        Args:
            logger: Logger for logging purposes, or None if not needed.

        Returns:
            paramiko.SFTPClient: The connected SFTP client.
        
        """
        #check instances of datatyes of parametres and raise TypeError if there is a mismatch
        if not isinstance(cls.hostname, (str)):
            raise TypeError("The 'hostname' parameter must be a string.")   
        
        if not isinstance(cls.username, (str)):
            raise TypeError("The 'username' parameter must be a string.")    
        
        if not isinstance(cls.port, (int)):
            raise TypeError("The 'port' parameter must be a int.") 
        
        if not isinstance(logger, (logging.Logger, type(None))):
            raise TypeError("The 'logger' parameter must be either a logging.Logger or a None.")
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(cls.hostname, username=cls.username, password=cls.password, port=cls.port)
            sftp = ssh.open_sftp()
            if logger:
                logger.info(f"Successfully connected to {cls.hostname}")
            return sftp
        except paramiko.AuthenticationException:
            if logger:
                logger.error(f"Authentication failed when connecting to {cls.hostname}")
            raise
        except paramiko.SSHException as e:
            if logger:
                logger.error(f"Failed to establish an SSH connection: {str(e)}")
            raise


    @classmethod
    def check_whether_base_path_exists_or_not(cls,sftp: paramiko.SFTPClient, path: Union[str, Path])->bool:

        '''
            Description:
                This function is used to check whether the base_path in which the folder has to be created exists or not.
            
            Args:
                sftp: The SFTP client providing connection to the remote host.
                path: The base path in which the folders has to be created.

            Returns:
                bool: True if base_path is present false if base_path is not present.
        '''
        #check instances of datatyes of parametres and raise TypeError if there is a mismatch
        if not isinstance(path, (str, Path)):
            raise TypeError("The 'path' parameter must be either a string or a Path object.")   
        
        if not isinstance(sftp, (paramiko.SFTPClient)):
            raise TypeError("The 'sftp' parameter must be a type paramiko.SFTPClient.") 
        
        try:
            sftp.stat(str(path))
            return True
        except IOError:
            return False
        
    @classmethod
    def check_whether_given_folder_is_symlink(cls,sftp: paramiko.SFTPClient, path:Union[str, Path]) -> bool:

        '''
            Description:
                Check if the given path is a symbolic link.
            Args:
                sftp: The SFTP client providing connection to the remote host.
                path: The path in which the folders has to be checked whether its symlink folder or not.
            Returns:
                bool: True if the folder is symlink false if not.
        '''
        #check instances of datatyes of parametres and raise TypeError if there is a mismatch
        if not isinstance(path, (str, Path)):
            raise TypeError("The 'path' parameter must be either a string or a Path object.")   
        
        if not isinstance(sftp, (paramiko.SFTPClient)):
            raise TypeError("The 'sftp' parameter must be a type paramiko.SFTPClient.") 
        
        try:
            # Try to read the symbolic link; if successful, it means the path is a symlink
            sftp.readlink(path)
            return True
        except IOError:
            # If an IOError is raised, the path is not a symlink
            return False
        except Exception as e:
            # Handle other potential exceptions, like permission errors
            print(f"Error checking symlink: {e}")
            return False
        

    @classmethod
    def create_folders_from_node_tree_recursively(cls, sftp: paramiko.SFTPClient, base_folder_path: Union[str, Path],\
            hierarchy_of_folders_to_be_created_inside_root_folder_path: Node, logger: Union[None, logging.Logger] = None) -> int:
        """
        Recursively creates folders and files based on the hierarchy_of_folders_to_be_created_inside_root_folder_path structure.

        Args:
            sftp: The SFTP client providing connection to the remote host.
            base_folder_path: The base path where folders/files will be created.
            hierarchy_of_folders_to_be_created_inside_root_folder_path: The hierarchical structure of folders, subfolders that are 
            to be created inside base folder path. which is initialized using Node class. 
            logger: Logger for logging purposes, or None if not needed.

        Returns:
            int: The total number of folders and files created.
        """
        #check instances of datatyes of parametres and raise TypeError if there is a mismatch
        if not isinstance(base_folder_path, (str, Path)):
            raise TypeError("The 'path' parameter must be either a string or a Path object.")   
        
        if not isinstance(sftp, (paramiko.SFTPClient)):
            raise TypeError("The 'sftp' parameter must be a type paramiko.SFTPClient.") 
        
        if not isinstance(logger, (logging.Logger, type(None))):
            raise TypeError("The 'logger' parameter must be either a logging.Logger or a None.") 
        
        if not isinstance(hierarchy_of_folders_to_be_created_inside_root_folder_path, (Node)):
            raise TypeError("The 'hierarchy_of_folders_to_be_created_inside_root_folder_path' parameter must be a Node.") 
        number_of_folders_and_files_created = 0

        if hierarchy_of_folders_to_be_created_inside_root_folder_path.is_file:
            # Create the file if it does not exist
            file_path = f"{base_folder_path}/{hierarchy_of_folders_to_be_created_inside_root_folder_path.name}"
            try:
                # Create an empty file
                sftp.file(file_path, 'w').close()
                number_of_folders_and_files_created += 1
                if logger:
                    logger.info(f"Created file: {file_path}")
                print(f"Created file: {file_path}")
            except IOError as e:
                print(f"File cannot be created: {file_path}")
                if logger:
                    logger.error(f"File cannot be created: {file_path} - {e}")
                raise
        else:
            # Create the directory if it does not exist
            folder_path = f"{base_folder_path}/{hierarchy_of_folders_to_be_created_inside_root_folder_path.name}"
            try:
                sftp.mkdir(folder_path)
                number_of_folders_and_files_created += 1
                print(f"Created folder: {folder_path}")
                if logger:
                    logger.info(f"Created folder: {folder_path}")
            except IOError as e:
                print(f"Folder already exists or cannot be created: {folder_path}")
                if logger:
                    logger.error(f"Folder already exists or cannot be created: {folder_path} - {e}")
                raise

            # Recursively create subfolders
            for subfolder in hierarchy_of_folders_to_be_created_inside_root_folder_path.subfolders:
                number_of_folders_and_files_created += cls.create_folders_from_node_tree_recursively(
                    sftp, folder_path, subfolder, logger
                )
        
        return number_of_folders_and_files_created


    @classmethod
    def create_folder_path_recursively(cls,base_folder_path: Union[str, Path],sftp: paramiko.SFTPClient,logger: Union[None, logging.Logger]=None) -> int:

        '''
            Description:
                This function is used to create a hierarchy of folders in the given folder path.
                The instance of class Node are used in order to provide the dynamic allocation 
                of folders, subfolders structure depending on the project requirements.
            
            Args:
                base_folder_path: The path in which the folders has to be created.
                sftp: The SFTP client providing connection to the remote host.
                logger: logging.Logger if logging is wished 'None' otherwise.

            Returns:
                number_of_files_created: Returns the total number of folders created along with the base folder if one is created.
        '''
        #check instances of datatyes of parametres and raise TypeError if there is a mismatch
        if not isinstance(base_folder_path, (str, Path)):
            raise TypeError("The 'path' parameter must be either a string or a Path object.")   
        
        if not isinstance(sftp, (paramiko.SFTPClient)):
            raise TypeError("The 'sftp' parameter must be a type paramiko.SFTPClient.") 
        
        if not isinstance(logger, (logging.Logger, type(None))):
            raise TypeError("The 'logger' parameter must be either a logging.Logger or a None.") 
        
        if not isinstance(cls.hierarchy_of_folders_to_be_created_inside_root_folder_path, (Node)):
            raise TypeError("The 'hierarchy_of_folders_to_be_created_inside_root_folder_path' parameter must be a Node.") 
        
        main_folder_created = 0
        #function initialization logger
        if logger is not None:
                logging.info(f"Function to create folders on the given folder path {base_folder_path} recursively.")
        
        # if base_folder_path not exists create one and create all the required subfolders within it recursively.
        if not cls.check_whether_base_path_exists_or_not(sftp, base_folder_path):
            try:
                main_folder_created += 1
                sftp.mkdir(str(base_folder_path))
                if logger is not None:
                    logging.info(f"Created base folder: {base_folder_path}")
                internal_folders = cls.create_folders_from_node_tree_recursively(sftp, base_folder_path,\
                                        cls.hierarchy_of_folders_to_be_created_inside_root_folder_path,logger)
                number_of_files_created = internal_folders+main_folder_created
                return number_of_files_created
            except IOError as e:
                if logger is not None:
                    logging.error(f"Error creating base folder {base_folder_path}: {e}")
                raise
        # if base_folder_path exists check whether all subfolders and files are present as required if not raise exception.
        else:
            if logger is not None:
                logging.info(f"Base folder {base_folder_path} already exists.")
            stack = [(base_folder_path, cls.hierarchy_of_folders_to_be_created_inside_root_folder_path)]
            while stack:
                current_path, current_node = stack.pop()
                base_folder_path = f"{current_path}/{current_node.name}"

                if not cls.check_whether_base_path_exists_or_not(sftp, base_folder_path):
                    if logger is not None:
                        logging.error(f"item missing: {base_folder_path}")
                    raise FileNotFoundError(f"item missing: {base_folder_path}")
                else:
                    if logger is not None:
                        logging.info(f"Folders present inside the path: {base_folder_path} no further changes required.")
                # Add subfolders to the stack in reverse order for correct hierarchical order
                stack.extend((base_folder_path, subfolder) for subfolder in reversed(current_node.subfolders))
    
    @classmethod
    def is_path_a_regular_folder(cls, folder_path: Union[str, Path],sftp:paramiko.SFTPClient,\
        logger: Union[None, logging.Logger]=None, description_str:str="") -> bool:
        
        '''
            Description:
                wrapper function to check the existance of folder in the given path.
            
            Args:
                base_path: The path in which the folder existance has to be checked.
                sftp: The SFTP client providing connection to the remote host.
                logger: logging.Logger if logging is wished 'None' otherwise.
                description_str: string used as a prefix for logging messages if logger:logging.Logger else none

            Returns:
                bool: True if folder exists and false if folder not exists.
        '''
        #check instances of datatyes of parametres and raise TypeError if there is a mismatch
        if not isinstance(folder_path, (str, Path)):
            raise TypeError("The 'path' parameter must be either a string or a Path object.")   
        
        if not isinstance(sftp, (paramiko.SFTPClient)):
            raise TypeError("The 'sftp' parameter must be a type paramiko.SFTPClient.") 
        
        if not isinstance(logger, (logging.Logger, type(None))):
            raise TypeError("The 'logger' parameter must be either a logging.Logger or a None.") 
        
        if not isinstance(description_str, (str)):
            raise TypeError("The 'description_str' parameter must be a string.") 
             
        if logger is not None:
                logging.info(description_str+f" Function to checking whether {folder_path} exists or not.")
        
        #Function call to check the folder existance in path
        base_path = str(folder_path)
        path_obj = Path(base_path)        
        path_list= [part for part in path_obj.parts if part]
        current_path_in_server= cls.default_host_path
        #check whether the path is folder or symlink or file and returns the bool accordingly
        for folder in path_list:
            current_path_in_server = Path(current_path_in_server) / folder
            try:
                # Attempt to list the contents of the current directory
                sftp.listdir(str(current_path_in_server))
                # Log if the directory exists
                if logger is not None:
                    logger.info(description_str+f" {current_path_in_server} exists")
                # Check if it's a symbolic link
                if cls.check_whether_given_folder_is_symlink(sftp, str(current_path_in_server)):
                    if logger is not None:
                        logger.error(description_str+f" {current_path_in_server} is a symbolic link")
                    return False        
            except IOError:
                # Log error if directory is not found
                if logger is not None:
                    logger.error(description_str+f" {current_path_in_server} neither exists nor a folder")
                return False
        return True