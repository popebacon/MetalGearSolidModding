@echo off
setlocal

:: ============================================================
:: restore_backup.bat
:: Restores original MGS1 DAT files from the BACKUP folder.
:: Use this to undo injections and return to a clean state.
:: ============================================================

set MOD_DIR=G:\Program Files (x86)\GOG Galaxy\Games\Metal Gear Solid - Modded
set BACKUP_DIR=%MOD_DIR%\BACKUP

echo.
echo Metal Gear Solid - Restore Backup
echo ===================================
echo Source: %BACKUP_DIR%
echo Target: %MOD_DIR%
echo.

if not exist "%BACKUP_DIR%\STAGE.DAT.orig" (
    echo ERROR: No backup found at %BACKUP_DIR%
    echo Run inject_mess_hall.bat at least once to create a backup first.
    pause
    exit /b 1
)

set /P CONFIRM=This will overwrite current DAT files. Continue? (Y/N):
if /I not "%CONFIRM%"=="Y" (
    echo Cancelled.
    pause
    exit /b 0
)

copy /Y "%BACKUP_DIR%\STAGE.DAT.orig"   "%MOD_DIR%\STAGE.DAT"   >nul && echo   [OK] STAGE.DAT restored
copy /Y "%BACKUP_DIR%\STAGE.HDR.orig"   "%MOD_DIR%\STAGE.HDR"   >nul && echo   [OK] STAGE.HDR restored
copy /Y "%BACKUP_DIR%\SCRIPT.DAT.orig"  "%MOD_DIR%\SCRIPT.DAT"  >nul && echo   [OK] SCRIPT.DAT restored
copy /Y "%BACKUP_DIR%\TEXTURE.DAT.orig" "%MOD_DIR%\TEXTURE.DAT" >nul && echo   [OK] TEXTURE.DAT restored

echo.
echo Restore complete.
pause
endlocal
