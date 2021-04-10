# Extended Automated Blacklist mod

This mod has now 2 modes which you can change to your desire. You can switch with the corresponding key between them.

This mod has basically 2 main parts, every mode has it:

[1] A player can be added to your blacklist by shooting you. You can define the constraints.

[2] A player can be added to your blacklist by pressing the "blacklisting key". You can define the constraints.

These are the defaults:

Mode [1]: The mod adds all arties to your blacklist, if you press the "blacklisting key". Also, the arty that hits you will be added automatically.

Mode [2]: The mod adds all players to your blacklist, if you press the "blacklisting key". Every player who is hitting you with HE will be added.

You can also choose the game modes (random, ranked or other game modes) for both main parts.

Friends (not anonymized) and platoon mates will be excluded from blacklisting. Due to this logic some game modes may not work properly with the "blacklisting key".

If your blacklist is full, you can easily extend it within the configuration window (restarting the game is required).

You now can also your blacklist. Pressing the corresponding key enables/stops clearing. 

Another corresponding key starts clearing. This may take some time. Make sure you are in the garage.

Another great feature is the automation of pressing the "blacklisting key".

It's also possible to add specific tanks that should be blacklisted. It works in both main parts.
To add that tank, there's more to be done. First, there's a text-field in the customization window "Some specific tank".
You need to write the specific tank ID into that field and press "Apply". After that you press "Apply", press the switching button below the text-field.
This will change the list with all specific tanks. If you press that small button, and the specific tank is not in the list, it will be added. 
If it's already in the list, it will be removed. To check that, watch your garage messages. You may ask yourself how do you get that specific tank ID?
There are 2 ways to get that:
[1] You have a replay from someone (maybe you?) who played that specific tank. You can find the specific tank ID in the replay-name.
    A replay-name is always like this: Date_Time_TankID_MapID_MapName. The TankID should be like this: Nation-SomeStuff_TankName. Replace the "-" after Nation with ":".
    Now you have the specific tank ID. Example: uk:GB86_Centurion_Action_X.
[2] There's actually a folder with all the names. Go to WorldofTanks\res\packages\scripts.pkg\scripts\item_defs\vehicles\.
    There are folders with the Nation and inside these there is the second part of the specific tank ID. You can open scripts.pkg with 7-Zip, WinRAR or something similar.

Installation:
Extract the *.wotmod-files from the zipped file. Copy them to WorldofTanks\mods\version\.

Uninstallation:
Delete the *.wotmod-files from WorldofTanks\mods\version\ (and all the files from WorldofTanks\mods\configs\).