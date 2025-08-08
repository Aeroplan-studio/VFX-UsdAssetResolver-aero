rem cd  "C:\Program Files\Katana6.0v1\bin"
set REPO_ROOT=C:\projects\VFX-UsdAssetResolver-aero
set RESOLVER_NAME=cachedResolver
set PYTHONPATH=%REPO_ROOT%\files\implementations\CachedResolver\code;%REPO_ROOT%\dist\KATANA\%RESOLVER_NAME%\lib\python;%PYTHONPATH%
rem set PXR_PLUGINPATH_NAME=%REPO_ROOT%\dist\KATANA\%RESOLVER_NAME%\resources
set FNPXR_PLUGINPATH=%REPO_ROOT%\dist\KATANA\%RESOLVER_NAME%\resources;%FNPXR_PLUGINPATH%
set PATH=%REPO_ROOT%\dist\KATANA\%RESOLVER_NAME%\lib;%PATH%
rem set AR_EXPOSE_RELATIVE_PATH_IDENTIFIERS=1
rem set TF_DEBUG=1

"C:\Program Files\Katana6.0v1\bin\katanaBin.exe"

pause