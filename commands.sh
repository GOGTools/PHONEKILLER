:: 1. Install the styling and bundling libraries
pip install colorama pyinstaller

:: 2. Create a clean project folder and navigate inside it
mkdir PhoneKillerProject
cd PhoneKillerProject

pyinstaller --onefile --add-data "adb.exe;." phone_killer.py
