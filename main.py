import logging
from typing import Union
from pathlib import Path
from Plus4Data import Node
from Plus4Data import RemoteFolderManager

def main(base_folder_path: Union[str, Path], checkpath: Union[str, Path],
         logger: Union[None, logging.Logger], create_file: bool, check_path_existance:bool):

    '''
            Description:
                main function to choose which operation to make either task1 or task2
                task1: create folders recursively.
                task2: check existance of folder in the give path.
            
            Args:
                base_folder_path: The path in which the created folder has to exist.
                checkpath: The path in which the existance of a folder operation (task2) has to be performed.
                logger: Logger for logging purposes, or None if not needed.
                create_file: set True if task 1 has to be done or False
                check_path_existance: set True if task 2 has to be done or False
    '''

    sftp_client = RemoteFolderManager.connect_to_sftp(
        logger=logger
    )
    #check instances of datatyes of parametres and raise TypeError if there is a mismatch
    if not isinstance(base_folder_path, (str, Path)):
            raise TypeError("The 'base_folder_path' parameter must be either a string or a Path object.")  

    if not isinstance(checkpath, (str, Path)):
            raise TypeError("The 'checkpath' parameter must be either a string or a Path object.") 
    if logger is not None:
                    logger.info(f"Folder structure of \n {str(RemoteFolderManager.hierarchy_of_folders_to_be_created_inside_root_folder_path)} \n to be created")
    
    #if create_file is true the task of creating folders inside remote host using recusrsion gets executed
    if create_file:
        total_number_of_files = RemoteFolderManager.create_folder_path_recursively(
            base_folder_path=base_folder_path,
            sftp=sftp_client,
            logger=logger)
        print("Total number of folders and files created", total_number_of_files)
    
    #if check_path_existance is true the task of checking the existance of regular folder gets executed
    if check_path_existance:
        path_exists = RemoteFolderManager.is_path_a_regular_folder(
            folder_path=checkpath,
            sftp=sftp_client,
            logger=logger,
            description_str="Check_functionality"
        )
        if path_exists:
            print(f"{str(checkpath)} exists in remote server")
        else:
            print(f"{str(checkpath)} does not exists in remote server")
    sftp_client.close()

if __name__ == "__main__":   
    
    logging.basicConfig(level=logging.INFO, filename="log.log", filemode="w", format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    hierarchy_of_folders_to_be_created_inside_root_folder_path = Node('fauna', [
        Node('domestic', [
            Node('pet', [
                Node('cat', [
                    Node('persian'),Node('tabby', [Node('white',[Node('white.py',is_file=True)])])
                ]),
                Node('dog')
            ]),
            Node('notpet')
        ]),
        Node('wild')
    ])
    host_path='/home/antony/Music/Codingtask'
    hostname = 'antony'
    username = 'antony'
    password = 'Antonio@12'
    RemoteFolderManager.set_defaults(host_path=host_path,
                                     hierarchy_of_folders_to_be_created_inside_root_folder_path=hierarchy_of_folders_to_be_created_inside_root_folder_path,\
                                        hostname= hostname, username= username, password= password)
    base_folder_path = str(RemoteFolderManager.default_host_path)+"/"+"datas"
    base_folder_path= Path(base_folder_path)
    checkpath = Path('datas/fauna3')
    main(base_folder_path= base_folder_path, checkpath= checkpath,
            logger=logger, create_file= True, check_path_existance=True)