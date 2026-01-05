@echo off

pip install -r requirements.txt
python -m PyInstaller --onefile -n YT2MPEG --noconsole main.py 

cls
echo --------------DONE--------------
echo EXE CAN BE FOUND FROM DIST FOLDER
pause