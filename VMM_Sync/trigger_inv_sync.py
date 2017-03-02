#!/usr/bin/env python


# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.pol
import cobra.model.vmm
import credentials
from cobra.internal.codec.xmlcodec import toXMLStr
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

#def take_backup ():
#	#Login to APIC
#	ls = cobra.mit.session.LoginSession('https://'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
#	md = cobra.mit.access.MoDirectory(ls)
#	md.login()
#
#	polUni = cobra.model.pol.Uni('')
#	fabricInst = cobra.model.fabric.Inst(polUni)
#
#	backup = cobra.model.config.ExportP(fabricInst, name="Bob_Leaf_replacement", snapshot="true", adminSt="triggered")
#
#	c = cobra.mit.request.ConfigRequest()
#	c.addMo(fabricInst)
#	md.commit(c)
#
#take_backup()

def trigger_sync():
	#Login to APIC
	ls = cobra.mit.session.LoginSession('https://'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
	md = cobra.mit.access.MoDirectory(ls)
	md.login()


	polUni = cobra.model.pol.Uni('')
	vmmProvP = cobra.model.vmm.ProvP(polUni, 'VMware')
	vmmDomP = cobra.model.vmm.DomP(vmmProvP, 'e7vmw1_Data')

	# build the request using cobra syntax
	vmmCtrlrP = cobra.model.vmm.CtrlrP(vmmDomP, inventoryTrigSt='triggered')


	# commit the generated code to APIC
	print toXMLStr(vmmDomP)
	c = cobra.mit.request.ConfigRequest()
	c.addMo(vmmDomP)
	md.commit(c)

trigger_sync()




#vmmUsrAccP

