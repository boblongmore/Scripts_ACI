this script performs a config backup. The script takes an argument on the command line for the backup name that will appear in ACI. 

example: python ACI_backup.py This_backup_made_by_ACI_backup_script

this script references a credentials file that has a dictionary of credentials for UCS and ACI. It is called credentials.py and should be in the following format.

ACI_login = { 'ipaddr' : '10.1.1.1', 'username' : 'admin', 'password' : 'acipassword' }


If you don't wish to use the credentials file, you can edit the values to reflect your environment, or change them to variables that you input either through raw_input or sys.argv.
