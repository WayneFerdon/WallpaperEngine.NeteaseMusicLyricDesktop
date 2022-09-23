@REM delete previous build
taskkill /IM NeteaseMusicStatus.exe /F

@REM build and copy dependents
pyinstaller -F --hidden-import queue ./Scripts/NeteaseMusicStatus.pyw
xcopy .\dist\NeteaseMusicStatus.exe .\Release /y
xcopy .\Scripts\Hanzi2Kanji.json .\Release /y

@REM delete temp
del .\NeteaseMusicStatus.spec /f /s /q 
rd /s /q .\Scripts\__pycache__
rd /s /q .\build
rd /s /q .\dist
pause