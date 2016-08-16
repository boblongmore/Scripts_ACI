#!/usr/bin/env python

# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fvns
import cobra.model.infra
import cobra.model.pol
from cobra.internal.codec.xmlcodec import toXMLStr
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

user_cred = raw_input("password: ")
#Login to APIC
ls = cobra.mit.session.LoginSession('https://10.207.10.100', 'admin', user_cred)
md = cobra.mit.access.MoDirectory(ls)
md.login()

#create Tenant
def vlanCreate (vName, vID):
	polUni = cobra.model.pol.Uni('')
	infraInfra = cobra.model.infra.Infra(polUni)


	fvnsVlanInstP = cobra.model.fvns.VlanInstP(infraInfra, name=vName, allocMode='dynamic')
	fvnsEncapBlk = cobra.model.fvns.EncapBlk(fvnsVlanInstP, to="vlan-"+vID, from_="vlan-"+vID, name='', descr='', allocMode='dynamic')



	#Commit to the apic
	c = cobra.mit.request.ConfigRequest()
	c.addMo(infraInfra)
	md.commit(c)

	query_vlan(vName)

def query_vlan(vName):
	vq = cobra.mit.access.ClassQuery('fvnsEncapBlk')
	vq.subtree = 'children'
	vlan_list = md.query(vq)
	for vlans in vlan_list:
		vlan_name = str('{}'.format(vlans.dn))
		if vName in vlan_name:
			print vlan_name+" has been created"


#start operations
name_input = raw_input ("Pool Name > ")
ID_input = raw_input ("VLAN ID > ")

vlanCreate(name_input, ID_input)


