#!/usr/bin/env python

# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fvns
import cobra.model.infra
import cobra.model.pol
import cobra.model.vmm
from cobra.internal.codec.xmlcodec import toXMLStr
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

user_cred = raw_input("password: ")
#Login to APIC
ls = cobra.mit.session.LoginSession('https://10.207.10.100', 'admin', user_cred)
md = cobra.mit.access.MoDirectory(ls)
md.login()

def VMM_Create(vswitch_name, vcenter_name, vdc_name, dvs_version, vlan_pool, vcenter_un, vcenter_pw):
	# the top level object on which operations will be made
	polUni = cobra.model.pol.Uni('')
	vmmProvP = cobra.model.vmm.ProvP(polUni, 'VMware')

	# build the request using cobra syntax
	vmmDomP = cobra.model.vmm.DomP(vmmProvP, name=vswitch_name)
	vmmCtrlrP = cobra.model.vmm.CtrlrP(vmmDomP, name=vcenter_name, rootContName=vdc_name, dvsVersion=dvs_version, hostOrIp=vcenter_name + '.datalinklabs.local')
	vmmRsAcc = cobra.model.vmm.RsAcc(vmmCtrlrP, tDn=u'uni/vmmp-VMware/dom-'+vswitch_name+'/usracc-'+vswitch_name+'_Credentials')
	infraRsVlanNs = cobra.model.infra.RsVlanNs(vmmDomP, tDn=u'uni/infra/vlanns-['+vlan_pool+']-dynamic')
	vmmUsrAccP = cobra.model.vmm.UsrAccP(vmmDomP, name=vswitch_name+'_Credentials', pwd=vcenter_pw, usr=vcenter_un)
	vmmVSwitchPolicyCont = cobra.model.vmm.VSwitchPolicyCont(vmmDomP)


	# commit the generated code to APIC
	print toXMLStr(vmmProvP)
	c = cobra.mit.request.ConfigRequest()
	c.addMo(vmmProvP)
	md.commit(c)

def VMM_Create2():
	polUni = cobra.model.pol.Uni('')
	vmmProvP = cobra.model.vmm.ProvP(polUni, 'VMware')
	vmmDomP = cobra.model.vmm.DomP(vmmProvP, name=u'e7_VMW1_Guest')
	vmmCtrlrP = cobra.model.vmm.CtrlrP(vmmDomP, name=u'e7vmw1vic01', rootContName=u'e7dc1', dvsVersion=u'6.0', hostOrIp=u'e7vmw1vic01.datalinklabs.local')
	vmmRsAcc = cobra.model.vmm.RsAcc(vmmCtrlrP, tDn=u'uni/vmmp-VMware/dom-e7_VMW1_Guest/usracc-e7_VMW1_Guest_Credentials')
	infraRsVlanNs = cobra.model.infra.RsVlanNs(vmmDomP, tDn=u'uni/infra/vlanns-[VMW1_Data_Vlan_pool]-dynamic')
	vmmUsrAccP = cobra.model.vmm.UsrAccP(vmmDomP, name=u'e7_VMW1_Guest_Credentials', pwd=u'D@talink1', usr=u'administrator@vsphere.local')
	vmmVSwitchPolicyCont = cobra.model.vmm.VSwitchPolicyCont(vmmDomP)
	
	
	# commit the generated code to APIC
	print toXMLStr(vmmProvP)
	c = cobra.mit.request.ConfigRequest()
	c.addMo(vmmProvP)
	md.commit(c)




#start operations
#vswitch_input = raw_input ("vswitch_name > ")
#vcenter_input = raw_input ("vcenter_name > ")
#vdc_input = raw_input ("datacenter_name > ")
#dvsversion_input = raw_input ("5.5 or 6.0 > ")
#vlan_pool_input = raw_input ("vlan pool name > ")
#vcenter_un_input = 'administrator@vsphere.local'
#vcenter_pw_input = raw_input ("vcenter password > ")
#
#VMM_Create(vswitch_input, vcenter_input, vdc_input, dvsversion_input, vlan_pool_input, vcenter_un_input, vcenter_pw_input)
VMM_Create2()


