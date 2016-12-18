This script take input from an excel file. Column 1 of the spreadsheet contains function names. The other rows contain information to populate variables within the script. You will need the xlrd module to run this.

This script references a credentials file that has a dictionary of credentials for UCS and ACI. It is called credentials.py and should be in the following format.

ACI_login = { 'ipaddr' : '10.1.1.1', 'username' : 'admin', 'password' : 'acipassword' }

If you don't wish to use the credentials file, you can edit the values to reflect your environment, or change them to variables that you input either through raw_input or sys.argv.
