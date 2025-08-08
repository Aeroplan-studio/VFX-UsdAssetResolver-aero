
REM Sample bash script to launch Houdini with HtoA enabled

REM edit these to suit your environment
REM set HOUDINI_PATH="d:\Program Files\Side Effects Software\Houdini 20.0.751"
REM set HTOA="d:\houdini\htoa\htoa-6.3.6.0_rdb9241e_houdini-20.0.896.py39"

REM source houdini environment
REM cd ${HOUDINI_ROOT}
REM source houdini_setup
REM cd - &> /dev/null

REM View docs in the default browser
REM export HOUDINI_EXTERNAL_HELP_BROWSER=xdg-open
 
REM set HOUDINI_PATH
REM set HOUDINI_PATH=%HOUDINI_PATH%;${HTOA}


set RESOLVER_NAME=cachedResolver
set REPO_ROOT=C:\projects\VFX-UsdAssetResolver-aero\dist\HOUDINI
# Windows
set PYTHONPATH=%REPO_ROOT%\%RESOLVER_NAME%\lib\python;%PYTHONPATH%
set PXR_PLUGINPATH_NAME=%REPO_ROOT%\%RESOLVER_NAME%\resources;%PXR_PLUGINPATH_NAME%
set PATH=%REPO_ROOT%\%RESOLVER_NAME%\lib;%PATH%
rem set AR_EXPOSE_RELATIVE_PATH_IDENTIFIERS=0

set TF_DEBUG=AR_RESOLVER_INIT # Debug Logs

 
REM launch houdini
"C:\Program Files\Side Effects Software\Houdini 20.5.278\bin\houdini"