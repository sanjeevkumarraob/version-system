# Python program to explain os.path.dirname() method 
    
# importing os.path module 
import os.path
import sys
from pathlib import Path
pwd = os.path.dirname(__file__)  
# Path
path = f"{pwd}"
syspath = sys.path
  
# Get the directory name  
# from the specified path
dirname = os.path.dirname(path)
basename = os.path.basename(path)
  
# Print the directory name  
print(dirname)
print(basename)
print("base directory")
print(Path(__file__).resolve().parent)  
  


# def read_version_file():
#     pwd = os.path.dirname(__file__)
#     print(pwd)
#     print(Path(__file__).resolve().parent)
#     test_resources_path = f"{pwd}/test_resources"
#     version_file = "version.txt"
#     version_home_path = f"{test_resources_path}/test_prefix"
#     # result = open(f"{version_home_path}/{version_file}", 'rb').read()
#     # print(result)