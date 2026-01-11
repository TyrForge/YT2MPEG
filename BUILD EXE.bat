@echo off

pip install -r requirements.txt
pyinstaller --noconfirm --onefile --windowed --icon "./FILE.ico" --name "YT2MPEG"  "./main.py"
rmdir /S /Q "./build/"

cls
echo --------------DONE--------------
echo EXE CAN BE FOUND FROM DIST FOLDER

pause
