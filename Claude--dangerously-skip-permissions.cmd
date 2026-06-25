@echo off
setlocal
set "ORIG_DIR=%CD%"
pushd "%~dp0"
call claude --dangerously-skip-permissions --verbose
popd
endlocal