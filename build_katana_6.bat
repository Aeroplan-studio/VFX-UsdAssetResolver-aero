REM Clear current session log 
cls
REM Source environment (Uncomment lines starting with "set" if you current env does not have these defined.)
REM set HFS=C:\Program Files\Side Effects Software\Houdini 19.5.435
REM Define Resolver > Has to be one of 'fileResolver'/'pythonResolver'/'cachedResolver'/'httpResolver'
set AR_RESOLVER_NAME=cachedResolver
REM Define App: MAYA
set AR_DCC_NAME=KATANA
set KATANA_ROOT=c:/Program Files/Katana6.0v1
set PYTHON_ROOT=C:/Users/user/AppData/Local/Programs/Python/Python39

REM Clear existing build data and invoke cmake
rmdir /S /Q build
REM rmdir /S /Q dist
REM Make sure to match the correct VS version the DCC was built with
cmake . -B build -G "Visual Studio 17 2022" -A x64 -T v143
cmake --build build  --clean-first --config Release
cmake --install build