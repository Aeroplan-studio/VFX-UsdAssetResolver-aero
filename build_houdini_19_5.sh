# Clear current session log 
clear
# Source environment (Uncomment lines starting with "export" if you current env does not have these defined.)
export HFS=$SMESHARIKI_ROOT/sidefx/hfs19.5
# Define Resolver > Has to be one of 'fileResolver'/'pythonResolver'/'cachedResolver'/'httpResolver'
export AR_RESOLVER_NAME=cachedResolver
# Define App
export AR_DCC_NAME=HOUDINI
export AR_DCC_VERSION=19.5
# Clear existing build data and invoke cmake
# rm -R build
# rm -R dist
set -e # Exit on error
cmake . -B build
cmake --build build --clean-first              # make clean all
cmake --install build                          # make install
# ctest -VV --test-dir build