@echo off
setlocal

:: ============================================================
:: inject_mess_hall.bat
:: Copies mess hall stage files into the MGS1 modded directory.
:: Run this from the repo root after editing stage source files.
:: ============================================================

set MOD_DIR=G:\Program Files (x86)\GOG Galaxy\Games\Metal Gear Solid - Modded
set STAGE_SRC=%~dp0..\stages\mess_hall

echo.
echo Metal Gear Solid - Mess Hall Stage Injector
echo ============================================
echo Target: %MOD_DIR%
echo.

:: Check target directory exists
if not exist "%MOD_DIR%\" (
    echo ERROR: Modded directory not found:
    echo   %MOD_DIR%
    echo.
    echo Check the path and try again.
    pause
    exit /b 1
)

:: Check for required game files
if not exist "%MOD_DIR%\STAGE.DAT" (
    echo ERROR: STAGE.DAT not found in mod directory.
    echo Make sure you have copied the base game files first.
    pause
    exit /b 1
)

:: Create a backup folder with timestamp if one doesn't exist yet
set BACKUP_DIR=%MOD_DIR%\BACKUP
if not exist "%BACKUP_DIR%\" (
    echo Creating backup of original DAT files...
    mkdir "%BACKUP_DIR%"
    copy "%MOD_DIR%\STAGE.DAT"   "%BACKUP_DIR%\STAGE.DAT.orig"   >nul
    copy "%MOD_DIR%\STAGE.HDR"   "%BACKUP_DIR%\STAGE.HDR.orig"   >nul
    copy "%MOD_DIR%\SCRIPT.DAT"  "%BACKUP_DIR%\SCRIPT.DAT.orig"  >nul
    copy "%MOD_DIR%\TEXTURE.DAT" "%BACKUP_DIR%\TEXTURE.DAT.orig" >nul
    echo Backup saved to: %BACKUP_DIR%
    echo.
)

:: Copy stage source files into a staging folder inside the mod directory
:: (VR-Disc Patcher or your injector reads from here)
set STAGE_OUT=%MOD_DIR%\MESS_HALL_INJECT
if not exist "%STAGE_OUT%\" mkdir "%STAGE_OUT%"

echo Copying stage files...
copy /Y "%STAGE_SRC%\stage\STCMV_MESS.DAT" "%STAGE_OUT%\"  >nul && echo   [OK] STCMV_MESS.DAT
copy /Y "%STAGE_SRC%\stage\STCMV_MESS.HDR" "%STAGE_OUT%\"  >nul && echo   [OK] STCMV_MESS.HDR
copy /Y "%STAGE_SRC%\stage\ENEMY_MESS.DAT" "%STAGE_OUT%\"  >nul && echo   [OK] ENEMY_MESS.DAT
copy /Y "%STAGE_SRC%\stage\ITEM_MESS.DAT"  "%STAGE_OUT%\"  >nul && echo   [OK] ITEM_MESS.DAT

echo.
echo Copying scripts...
copy /Y "%STAGE_SRC%\scripts\mess_codec.SCR"  "%STAGE_OUT%\" >nul && echo   [OK] mess_codec.SCR
copy /Y "%STAGE_SRC%\scripts\mess_events.SCR" "%STAGE_OUT%\" >nul && echo   [OK] mess_events.SCR

echo.
echo Copying texture specs...
copy /Y "%STAGE_SRC%\textures\mess_walls.TIM.txt" "%STAGE_OUT%\" >nul && echo   [OK] mess_walls.TIM.txt
copy /Y "%STAGE_SRC%\textures\mess_props.TIM.txt" "%STAGE_OUT%\" >nul && echo   [OK] mess_props.TIM.txt

echo.
echo ============================================
echo Files staged to:
echo   %STAGE_OUT%
echo.
echo Next steps:
echo   1. Open VR-Disc Patcher (or your injector).
echo   2. Point it at: %MOD_DIR%\STAGE.DAT
echo   3. Inject STCMV_MESS.DAT into slot 0x48.
echo   4. Inject STCMV_MESS.HDR into the matching header slot.
echo   5. Inject mess_codec.SCR and mess_events.SCR into SCRIPT.DAT.
echo   6. Convert .TIM.txt specs to binary TIM2 files, then inject into TEXTURE.DAT.
echo   7. Patch the NWSB B2 corridor stage (0x09) to add the door trigger.
echo   8. Launch MGSI.EXE from %MOD_DIR% to test.
echo ============================================
echo.
pause
endlocal
