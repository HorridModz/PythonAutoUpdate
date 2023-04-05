# PythonAutoUpdate
A base for an auto updating python script using github.

This can easily be added to existing scripts.

# Table of contents

- [Setup](#setup)
- [Adding to Your Script](#adding-to-your-script)
- [Method 1: Directly Adding to Script](#method-1-directly-adding-to-script)
- [Method 2: Importing as a Module](#method-2-importing-as-a-module)
- [Usage](#usage)
- [Example](#example)

# Setup
Github repositories are used for version control. To use this tool, make a github repository with the following files:
1. A file to store the script code (which will be automatically updated). This must match the name of the local script file.
2. A file to store the script's current version. The recommended name is `version.txt`.
3. A file to store a summary of the latest changes in the newest version. The recommended name is `whatsnew.txt`.

# Adding to Your Script

# Method 1: Directly Adding to Script
1. Make sure your script imports the following modules:
   - os
   - sys
   - re
   - requests
2. Add this code to the beginning of your script:
```py
__version__ = "1.0.0" # Replace with the current version of your script
ignoreversion = None
updatechecking = True
```
Change `__version__` to the current version of your script.
3. Copy and paste the entire UpdateHandler class, and add it to your script.

# Method 2: Importing as a Module
1. Download PythonAutoUpdate.py and add it to your main script's project
2. At line 1 of PythonAutoUpdate.py
   (
```py
__version__ = "1.0.0"
```
),
 change `__version__` to the current version of your script
3. In your main script, import PythonAutoUpdate:
```py
import PythonAutoUpdate
```

# Usage

**Note**:
This section will be according to [Method 2: Importing as a Module](#method-2-importing-as-a-module), meaning things will be in the `PythonAutoUpdate` scope rather than the global scope.

First off, initialize the `UpdateHandler` class:

```py
updatehandler = PythonAutoUpdate.UpdateHandler(repolink, scriptname, versionlink, whatsnewlink, codelink)
```

**Parameters**:
```
- repolink: Link to the github repository you created
- scriptname: The name of the current script. Must match the name of the script file on the github repository.
- versionlink: Link to the version.txt (or whatever name you gave it) file in the github repository
- whatsnewlink: Link to the whatsnew.txt (or whatever name you gave it) file in the github repository
- scriptlink: Link to the script file in the github repository
```

To run the update dialog, use the `updatedialog` method. This will ask the user if they want to check for updates, and allow them to permanently disable update checking:

```py
updatehandler.updatedialog()
```

If you want to always check for updates, without asking the user if they want to or allowing them to turn it off, you can directly call `checkforupdates`:

```py
updatehandler.checkforupdates()
```

**The latter is recommended**, because it can be annoying for the user to go through the update dialog every time.

# Example
Go to the [POC](POCLINKHERE) for an example. The POC implements [Method 1: Directly Adding to Script](#method-1-directly-adding-to-script).

*The POC does not actually do anything*, and it will not find updates. To see the system fully in action, you will have to try it out yourself.