#!/usr/bin/env python

# list of packages that should be imported for this code to work
import cobra.mit.access
import cobra.mit.request
import cobra.mit.session
import cobra.model.fv
import cobra.model.pol
import cobra.model.vmm
import cobra.model.l3ext
import cobra.model.ospf
import cobra.model.vz
import credentials
import xlrd
from cobra.internal.codec.xmlcodec import toXMLStr
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

#Login to APIC
ls = cobra.mit.session.LoginSession('https:'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
md = cobra.mit.access.MoDirectory(ls)
md.login()

#open worksheet and find functions to run
aci_book = xlrd.open_workbook("EPG_Input.xlsx")
aci_sheet = aci_book.sheet_by_index(0)

for row in range(aci_sheet.nrows):
	for column in range(aci_sheet.ncols):
		if aci_sheet.cell_value(row,column) == "Create_EPG":
			EPG_name = aci_sheet.cell_value(row,1)
			VMM_name = aci_sheet.cell_value(row,3)
			BD_name = aci_sheet.cell_value(row,4)
			Cnt_name = aci_sheet.cell_value(row,5)

for name in aci_sheet.col_values(0):
	if name == "Create_EPG":
		CreateEPG()
	elif name == "Create_BD":
		Create_BD()
		

#create Tenant
def CreateEPG (tn_name, epg_name, l3Out_name, VMM_name, VRF_name, BD_subnet, ANP_name):
	polUni = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(polUni, tnName)
	fvCommon = cobra.model.fv.Tenant(polUni, 'common')

	#Create Bridge Domain
	fvBD1 = cobra.model.fv.BD(fvTenant, name=epg_name+'_BD')

	#Associate Bridge Domain to VRF
	fvRsCtx1 = cobra.model.fv.RsCtx(fvBD1, tnFvCtxName=VRF_name)

	#Associate Web Bridge Domain with L3 out
	fvRsBDToOut = cobra.model.fv.RsBDToOut(fvBD1, tnL3extOutName=l3Out_name)

	#Create Subnets for the Bridge Domains, BD1 is allowed across VRFs
	fvSubnet1 = cobra.model.fv.Subnet(fvBD1, ip=BD_subnet, scope='public,shared')

	#create ANP
	fvAp = cobra.model.fv.Ap(fvTenant, name=ANP_name)

	#create EPGs
	fvAEPg1 = cobra.model.fv.AEPg(fvAp, name=epg_name)

	#Associate EPGs with Bridge Domains
	fvRsBd1 = cobra.model.fv.RsBd(fvAEPg1, tnFvBDName=epg_name)

	#Define External L3 information
	l3extOut = cobra.model.l3ext.Out(fvCommon, name=l3Out_name)
	l3extInstP = cobra.model.l3ext.InstP(l3extOut, name=l3Out_name)

	#Associate Demo_Web Contract
	#fvRsCons1 = cobra.model.fv.RsCons(fvAEPg1, tnVzBrCPName='Demo_Web')

	#Associate EPG with VMM Domain
	fvRsDomAtt1 = cobra.model.fv.RsDomAtt(fvAEPg1, tDn='uni/vmmp-VMware/dom-'+VMM_name, resImedcy=u'immediate')





	#Commit to the apic
	c = cobra.mit.request.ConfigRequest()
	c.addMo(fvTenant)
	md.commit(c)

#get VMWare VMM already created and present as choices
def get_vmm():
	vmmprovider = md.lookupByClass('vmmDomP', parentDn="uni")
	for vmmd in vmmprovider:
		vmm_convert =  str("{}".format(vmmd.rn))
		(junk, vmm_spl) = vmm_convert.split('dom-')
		print vmm_spl

	vmm_choice = raw_input ("VMM Domain > ")
	return vmm_choice

#start operations
tenant_input = raw_input ("Tenant Name > ")
epg1_input = raw_input ("EPG1 > ")
epg2_input = raw_input ("EPG2 > ")
epg3_input = raw_input ("EPG3 > ")
l3Out = raw_input ("L3 Out > ")
#VMM = raw_input ("VMM Domain > ")
VMM = get_vmm()

tenantCreate(tenant_input, epg1_input, epg2_input, epg3_input, l3Out, VMM)


