# AddSteamGamesToLibrary
Add a list of steam games to your steam library

Some notes:
- You must disable two factor authentication for this script to work.
- Be sure to add your Steam credentials in the credential file.
- Copy a list of the games you'd like to add to your account to 'games.txt'. Be sure the spelling matches exactly or the script may not be able to find them on Steam.
- The default behavior is to skip demo and early access games. This can be changed in the 'config.ini' file.
- Steam rate limits how many games you can add to your account at a time. If the script detects this failure, it will exit. Wait a half hour and try again.
