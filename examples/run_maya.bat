
set REPO_ROOT=C:\projects\VFX-UsdAssetResolver-aero
set RESOLVER_NAME=cachedResolver
set PYTHONPATH=%REPO_ROOT%\dist\MAYA\%RESOLVER_NAME%\lib\python;%PYTHONPATH%
set PXR_PLUGINPATH_NAME=%REPO_ROOT%\dist\MAYA\%RESOLVER_NAME%\resources;%PXR_PLUGINPATH_NAME%
set PATH=%REPO_ROOT%\dist\MAYA\%RESOLVER_NAME%\lib;%PATH%
set AR_EXPOSE_RELATIVE_PATH_IDENTIFIERS=0
set TF_DEBUG=1

"C:\Program Files\Autodesk\Maya2025\bin\maya.exe"