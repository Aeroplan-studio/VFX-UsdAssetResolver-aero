REM Clear current session log 
cls
REM Source environment (Uncomment lines starting with "set" if you current env does not have these defined.)
set HFS=C:\Program Files\Side Effects Software\Houdini 19.5.435
REM Define Resolver > Has to be one of 'fileResolver'/'pythonResolver'/'cachedResolver'/'httpResolver'
set AR_RESOLVER_NAME=cachedResolver
REM Define App
set AR_DCC_NAME=MAYA

## Maya
set AR_DCC_NAME=maya
set MAYA_USD_SDK_ROOT="c:\Program Files\Autodesk\MayaUSD\Maya2025\0.29.0\mayausd\USD"
REM set MAYA_USD_SDK_ROOT="c:\projects\maya-usd"
set MAYA_USD_SDK_DEVKIT_ROOT="C:\Program Files\Autodesk\MayaUSD\Maya2025\0.29.0\mayausd\USD\devkit.zip"
set PYTHON_ROOT="C:\Users\user\AppData\Local\Programs\Python\Python311"
set PYTHON_ROOT="c:\Program Files\Autodesk\Maya2025\Python"

REM Clear existing build data and invoke cmake
rmdir /S /Q build
rmdir /S /Q dist
REM Make sure to match the correct VS version the DCC was built with
cmake . -B build -G "Visual Studio 17 2022" -A x64 -T v143
cmake --build build  --clean-first --config Release
cmake --install build