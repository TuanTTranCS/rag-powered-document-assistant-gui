REM This batch file is used to activate a Python virtual environment and run the Python application (GUI mode).
ECHO OFF

REM Activate the virtual environment
call C:\Users\tuant\AppData\Local\pypoetry\Cache\virtualenvs\rag-HlQWJi8S-py3.12\Scripts\activate.bat

REM Run the application
python app.py

@REM REM Optional: Add a pause to keep the command prompt open after execution
@REM PAUSE