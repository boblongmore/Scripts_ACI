#!/usr/bin/env python


# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fabric
import cobra.model.pol
import cobra.model.config
import credentials
<<<<<<< Updated upstream
=======
import sys
>>>>>>> Stashed changes
from cobra.internal.codec.xmlcodec import toXMLStr
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

def take_backup ():
	#Login to APIC
	ls = cobra.mit.session.LoginSession('https://'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
	md = cobra.mit.access.MoDirectory(ls)
	md.login()

<<<<<<< Updated upstream
	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)

	backup = cobra.model.config.ExportP(fabricInst, name="backup_created_with_python", snapshot="true", adminSt="triggered")
=======

	backup_input = sys.argv
	backup_description = str(backup_input[1])
	print "backup created with name: %s" % backup_description
	polUni = cobra.model.pol.Uni('')
	fabricInst = cobra.model.fabric.Inst(polUni)

	backup = cobra.model.config.ExportP(fabricInst, name=backup_description, snapshot="true", adminSt="triggered")
>>>>>>> Stashed changes

	c = cobra.mit.request.ConfigRequest()
	c.addMo(fabricInst)
	md.commit(c)

take_backup()