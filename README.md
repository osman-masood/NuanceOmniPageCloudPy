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

<code>
import NuanceOmniPageCloud
</code>
<code>
n = NuanceOmniPageCloud.NuanceOmniPageCloud(account_name=MY_ACCOUNT_NAME, account_key=MY_ACCOUNT_KEY)
</code>
<code>
n.convert('/Users/oamasood/stuff/profile.png', '/Users/oamasood/stuff/profile.docx', 13)
</code>

If you experience any issues, let me know...