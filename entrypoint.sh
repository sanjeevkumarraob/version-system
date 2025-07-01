#!/bin/bash

set -eu

echo "
 █████╗ ██████╗ ██╗███╗   ███╗    ██╗   ██╗███████╗██████╗ ███████╗██╗ ██████╗ ███╗   ██╗    ███████╗██╗   ██╗███████╗████████╗███████╗███╗   ███╗
██╔══██╗██╔══██╗██║████╗ ████║    ██║   ██║██╔════╝██╔══██╗██╔════╝██║██╔═══██╗████╗  ██║    ██╔════╝╚██╗ ██╔╝██╔════╝╚══██╔══╝██╔════╝████╗ ████║
███████║██████╔╝██║██╔████╔██║    ██║   ██║█████╗  ██████╔╝███████╗██║██║   ██║██╔██╗ ██║    ███████╗ ╚████╔╝ ███████╗   ██║   █████╗  ██╔████╔██║
██╔══██║██╔═══╝ ██║██║╚██╔╝██║    ╚██╗ ██╔╝██╔══╝  ██╔══██╗╚════██║██║██║   ██║██║╚██╗██║    ╚════██║  ╚██╔╝  ╚════██║   ██║   ██╔══╝  ██║╚██╔╝██║
██║  ██║██║     ██║██║ ╚═╝ ██║     ╚████╔╝ ███████╗██║  ██║███████║██║╚██████╔╝██║ ╚████║    ███████║   ██║   ███████║   ██║   ███████╗██║ ╚═╝ ██║
╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝      ╚═══╝  ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝     ╚═╝
                                                                                                                                                                                                                                                                                                                                                       
"

command="get-version.py"

echo ${@}

# # run the python script with the variables
python3 /usr/src/version_system/get-version.py ${@}

# if [ -z "${VERSION_FILE:-}" ]; then
#     echo "Version file is not present in environment variable"
#     exit 1
# else
#     command="${command} -f ${VERSION_FILE}"    
# fi


# if [ ! -z "${PREFIX:-}" ]; then
#     echo "Prefix present in environment variable"
#     command="${command} -p ${PREFIX} -f ${VERSION_FILE}"
# fi

# if [ ! -z "${SUFFIX:-}" ]; then
#     echo "Suffix present in environment variable"
#     command="${command} -s ${SUFFIX} -f ${VERSION_FILE}"
# fi

# if [ ! -z "${MODULE:-}" ]; then
#     echo "Module present in environment variable"
#     command="${command} -m ${MODULE} -f ${VERSION_FILE}"
# fi

# echo $command

# # run the python script with the variables
# python3 $command