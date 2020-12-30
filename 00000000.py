#!pcsx2py

# This volatile module `monitor.00000000` may be re-loaded and loose all variables on some events:
# - Game startup (on _reloadElfInfo)
# - Resume, where it is suspended by pressing ESC key (on AppCoreThread::Resume)
# Not:
# - Resume, where it is suspended by System menu → Pause
# - Load game state

import pcsx2

pcsx2.WriteLn('Hello')
