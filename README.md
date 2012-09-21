<h1>NuanceOmniPageCloudPy</h1>

<h3>Nuance OmniPage Cloud Python module</h3>

<h4>Required Modules</h4>

- BeautifulSoup3 (NOT 4) - http://www.crummy.com/software/BeautifulSoup/
- pycurl - http://pycurl.sourceforge.net
- requests - http://docs.python-requests.org/en/latest/index.html

<h4>Notice for OS X users having trouble installing PyCurl</h4>

pycurl uses command line tools (like CLang from the LLVM package) that must be installed manually via Xcode.
Starting with Xcode 4.3 - you must now manually install command line tools from Xcode menu > Preferences > Downloads.
See: http://stackoverflow.com/questions/9353444/how-to-use-install-gcc-on-mac-os-x-10-8-xcode-4-4

<h4>Usage</h4>

This example uses your account name (MY_ACCOUNT_NAME) and account key (MY_ACCOUNT_KEY) to convert a .png file into a .docx file (job type ID 13).
For more information on job type IDs, check out the table at the end of the API Reference Guide included with the SDK.

    import NuanceOmniPageCloud
    n = NuanceOmniPageCloud.NuanceOmniPageCloud(account_name=MY_ACCOUNT_NAME, account_key=MY_ACCOUNT_KEY)
    job_info_dict = n.convert('/Users/oamasood/stuff/profile.png', '/Users/oamasood/stuff/profile.docx', 13)
    # Returns a dict with all the JobInfo parameters

Now, let's cancel a job...

    canceled_job_info_dict = n.cancel_job(job_info_dict['job_id'])
    
If you experience any issues, let me know...

<h4>License</h4>
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.