__version__ = "1.0.0"
_IGNOREVERSION = None
_UPDATECHECKING = True

import os
import sys
import re
import requests


class UpdateHandler:
    def __init__(self, repolink: str,
                 scriptname: str=None, versionlink: str=None, whatsnewlink: str=None, scriptlink: str=None):
        """
        Initializes updatehandler class.

        :param repolink: Root link to the github repository
        :param scriptname: The name of the current script
        :param versionlink: Link to the version.txt file in the github repository
        :param whatsnewlink: Link to the whatsnew.txt file in the github repository
        :param scriptlink: Link to the script file in the github repository

        If not specified, scriptname, versionlink, whatsnewlink, and scriptlink will be automatically generated
        If importing as a module, make sure you specify scriptname - if you don't, it will default to the name
        of this module
        """
        self.repolink = repolink
        rawrepolink = repolink.replace("https://github.com","https://raw.githubusercontent.com")
        if not scriptname:
            scriptname = os.path.basename(__file__)
        if not versionlink:
            versionlink = rawrepolink + "/main/version.txt"
        if not whatsnewlink:
            whatsnewlink = rawrepolink + "/main/whatsnew.txt"
        if not scriptlink:
            scriptlink = rawrepolink + f"/main/{scriptname}"
        self.scriptname = scriptname
        self.versionlink = versionlink
        self.whatsnewlink = whatsnewlink
        self.scriptlink = scriptlink

    @staticmethod
    def _getrequest(link: str, errormessage: str = None) -> (int, str):
        """
        Utility function to make http get request
        If request fails, returns (None, None)

        :param link: Link to make request to
        :param errormessage: Error message to print if request fails. If errormessage is None,
        no error messages will be printed
        """
        if "requests" in globals():
            try:
                response = requests.get(link)
            except Exception:
                if errormessage is not None:
                    print(f"{errormessage}: Get request to {link} failed")
            else:
                if response.status_code != 200:
                    if errormessage is not None:
                        print(f"{errormessage}:"
                              f" {link}"
                              " returned http status code"
                              f" {str(response.status_code)}")
        return (response.status_code == 200, response.text) if "response" in locals() else (None, None)

    def _checkcorrupted(self, currentcode: str) -> None:
        """
        Checks if current script has been corrupted.
        If if has, attempts to repair it.
        Changes will be applied on next run.

        :param currentcode: The code of the current script to repair to if necessary
         (it is the caller's responsibility to obtain this variable before attempting anything
         that may corrupt the script)
        """
        with open(__file__, 'r+') as f:
            if f.read() != currentcode:
                print(f"{self.scriptname} has been corrupted. Attempting to repair...")
                try:
                    f.write(currentcode)
                except Exception:
                    # We use sys.exit because we do not want this exception to be caught
                    sys.exit(f"Failed to repair {self.scriptname}.")
                else:
                    print(f"Successfully repaired {self.scriptname}. Rerun the script.")
                    sys.exit()

    @staticmethod
    def ignoreversion(version: str) -> None:
        """
        Edits current script to ignore specified version when checking for updates.
        Changes will be applied on next run.

        :param version: Version to ignore
        """
        with open(__file__, 'r') as f:
            currentcode = f.read()
        with open(__file__, 'w') as f:
            new = re.sub("\n_IGNOREVERSION = .*\n", f"\n_IGNOREVERSION = \"{version}\"\n", currentcode)
            f.write(new)

    @staticmethod
    def disableupdatechecking() -> None:
        """
        Edits current script to disable update checking.
        Changes will be applied on next run.
        """
        with open(__file__, 'r') as f:
            currentcode = f.read()
        with open(__file__, 'w') as f:
            new = currentcode.replace("\n_UPDATECHECKING = True\n", "\n_UPDATECHECKING = False\n")
            f.write(new)

    def update(self) -> None:
        """
        Edits current script to latest version on remote github repository.
        Changes will be applied on next run.

        :raises requests.exceptions.RequestException: If http request to remote github repository fails
        """
        success, text = self._getrequest(self.scriptlink, errormessage=None)
        if success:
            with open(__file__, 'w') as f:
                f.write(text)
        else:
            raise requests.exceptions.RequestException(f"Request to {self.scriptlink} failed.")

    def checkforupdates(self) -> None:
        """
        Checks for updates to the current script on remote github repository.
        Interacts with user via Y/N prompts
        Changes will be applied on next run.

        Possible outcomes:
        -Nothing happens
        -Script is updated to latest version on remote github repository
        -The latest version on remote github repository is set to be ignored
        in future update checks

        :raises sys.exit: If changes to script are made
        """
        success, text = self._getrequest(self.versionlink,
                                         errormessage=f"{self.scriptname}: Unable to check for updates")
        if success:
            cloudversion = text.strip()
            if not (cloudversion == __version__ or cloudversion == _IGNOREVERSION):
                print(f"{self.scriptname} has an update! {self.repolink}")
                success, text = self._getrequest(self.versionlink,
                                                 errormessage=f"Unable to retrieve changelog for update")
                if success:
                    whatsnew = text
                    print(whatsnew)
                toupdate = input("Would you like to update? (Y/N):")
                if toupdate.strip().lower() == "y":
                    with open(__file__, 'r') as f:
                        currentcode = f.read()
                    try:
                        self.update()
                    except Exception as err:
                        print("Update failed: " + str(err))
                        try:
                            self._checkcorrupted(currentcode)
                        except Exception:
                            pass
                    else:
                        print(f"Successfully updated {self.scriptname}! Rerun the script.")
                        sys.exit()
                else:
                    toignore = input("Would you like to permanently ignore this version? (Y/N):")
                    if toignore.strip().lower() == "y":
                        with open(__file__, 'r') as f:
                            currentcode = f.read()
                        try:
                            self.ignoreversion(cloudversion)
                        except Exception as err:
                            print("Failed to permanently ignore this version: " + str(err))
                            try:
                                self._checkcorrupted(currentcode)
                            except Exception:
                                pass
                        else:
                            print(f"Successfully ignored this version! Rerun {self.scriptname}.")
                            sys.exit()
            else:
                print("No updates found")

    def updatedialog(self):
        """
        Asks user if they would like to check for updates.
        If yes, calls checkforupdates() function.
        Interacts with user via Y/N prompts
        Changes will be applied on next run.

        Possible outcomes:
        -Nothing happens
        -Script is updated to latest version on remote github repository
        -The latest version on remote github repository is set to be ignored
        in future update checks
        -Update checks are permanently disabled

        :raises sys.exit: If changes to script are made
        """
        if not _UPDATECHECKING:
            return
        tocheckforupdates = input(f"{self.scriptname}: Would you like to check for updates? (Y/N):")
        if tocheckforupdates.strip().lower() == "y":
            self.checkforupdates()
        else:
            todisable = input("Would you like to permanently disable update checking? (Y/N):")
            if todisable.strip().lower() == "y":
                with open(__file__, 'r') as f:
                    currentcode = f.read()
                try:
                    self.disableupdatechecking()
                except Exception as err:
                    print("Failed to permanently disable update checking: " + str(err))
                    try:
                        self._checkcorrupted(currentcode)
                    except Exception:
                        pass
                else:
                    print(f"Successfully disabled update checking! Rerun {self.scriptname}")
                    sys.exit()


if __name__ == "__main__":
    updatehandler = UpdateHandler(repolink="https://github.com/Horridmodz/PythonAutoUpdate/POC",
                                  scriptname="AutoUpdatePOC.py",
                                  versionlink="https://raw.githubusercontent.com/Horridmodz/PythonAutoUpdate"
                                                "/main/POC"
                                                "/version.txt",
                                  whatsnewlink="https://raw.githubusercontent.com/Horridmodz/PythonAutoUpdate"
                                              "/main/POC"
                                              "/whatsnew.txt",
                                  scriptlink="https://raw.githubusercontent.com/Horridmodz/PythonAutoUpdate"
                                              "/main/POC"
                                              "/AutoUpdatePOC.py",
                                  )
    updatehandler.updatedialog()