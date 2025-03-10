rem ---------------FILL OUT THE FOLLOWING VARIABLES MANUALLY---------------

rem Name of Inno Setup Script
set INNO_SETUP_SCRIPT_NAME=DUMMY.iss

rem Name of Project
set PROJECT_NAME=DUMMY

rem Are you using miniconda3 or anaconda3?
set CONDA=miniconda3

rem Name of your virtual environment (for main modules)
set VENV_NAME_MAIN=DUMMY

rem Name of your virtual environment (for TRNSYS/python modules)
set VENV_NAME_TRNSYS=DUMMY

rem ---------------DO NOT CHANGE BATCH FILE AFTER THIS LINE----------------

rem Set path variables

for %%i in ("%CD%\..") do set PROJECT_PATH=%%~fi
for %%i in ("%CD%\..") do set PROJECT_NAME=%%~nxi
set MAIN_PATH=%PROJECT_PATH%\%PROJECT_NAME%\main.py
set CONDA_PATH=%USERPROFILE%\%CONDA%
set VENV_PATH_MAIN=%CONDA_PATH%\envs\%VENV_NAME_MAIN%
set VENV_PATH_TRNSYS=%CONDA_PATH%\envs\%VENV_NAME_TRNSYS%
set PYTHON_PATH_MAIN=%VENV_PATH_MAIN%\python.exe
set PYTHON_PATH_TRNSYS=%VENV_PATH_TRNSYS%\python.exe
set PYINSTALLER_PATH=%VENV_PATH_MAIN%\Scripts\pyinstaller.exe
set INNO_SETUP_EXE_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
set INNO_SETUP_SCRIPT_PATH=%CD%\%INNO_SETUP_SCRIPT_NAME%
set TRNSYS_PATH=C:\TRNSYS18