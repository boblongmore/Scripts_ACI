#!/usr/bin/env python


# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fabric
import cobra.model.pol
import cobra.model.config
import credentials
import sys
from cobra.internal.codec.xmlcodec import toXMLStr
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

def main():
	take_backup()

def take_backup ():
	#Login to APIC
	ls = cobra.mit.session.LoginSession('https://'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
	md = cobra.mit.access.MoDirectory(ls)
	md.login()


	backup_input = sys.argv
	backup_description = str(backup_input[1])
	print "backup created with name: %s" % backup_description
	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)

	backup = cobra.model.config.ExportP(fabricInst, name=backup_description, snapshot="true", adminSt="triggered")

	c = cobra.mit.request.ConfigRequest()
	c.addMo(fabricInst)
	md.commit(c)

if __name__ == '__main__':
    main()
