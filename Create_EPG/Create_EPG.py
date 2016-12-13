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
#ls = cobra.mit.session.LoginSession('https:'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
#md = cobra.mit.access.MoDirectory(ls)
#md.login()

#open worksheet and find functions to run
def start_xls():
	aci_book = xlrd.open_workbook("EPG_Input.xlsx")
	aci_sheet = aci_book.sheet_by_index(0)

	for row in range(aci_sheet.nrows):
		for column in range(aci_sheet.ncols):
			if aci_sheet.cell_value(row,column) == "Create_EPG":
				Create_EPG(aci_sheet,row)
			elif aci_sheet.cell_value(row,column) == "Create_BD":
				Create_BD(aci_sheet,row)
		

#create Tenant
def Create_EPG (aci_sheet,row):
	tn_name = aci_sheet.cell_value(row,1)
	ANP_name = aci_sheet.cell_value(row,2)
	EPG_name = aci_sheet.cell_value(row,3)
	static_path = aci_sheet.cell_value(row,4)
	if static_path == "":
		static_path = "None"
	VMM_name = aci_sheet.cell_value(row,5)
	if VMM_name == "":
		VMM_name = "None"
	BD_name = aci_sheet.cell_value(row,6)
	cnt_name = aci_sheet.cell_value(row,7)


	#Define top level pol
	#polUni = cobra.model.pol.Uni('')
	#fvTenant = cobra.model.fv.Tenant(polUni, tn_name)
	#fvCommon = cobra.model.fv.Tenant(polUni, 'common')
	print tn_name

	#create ANP
	#fvAp = cobra.model.fv.Ap(fvTenant, name=ANP_name)
	print ANP_name

	#create EPGs
	#fvAEPg1 = cobra.model.fv.AEPg(fvAp, name=EPG_name)
	print EPG_name

	#Associate EPGs with Bridge Domains
	#fvRsBd1 = cobra.model.fv.RsBd(fvAEPg1, tnFvBDName=BD_name)
	print BD_name

	#Associate EPG with VMM Domain
	if VMM_name != "None":
		#fvRsDomAtt1 = cobra.model.fv.RsDomAtt(fvAEPg1, tDn='uni/vmmp-VMware/dom-'+VMM_name, resImedcy=u'immediate')
		print VMM_name
	elif VMM_name == "None":
		print "No VMM Domain Selected"


def Create_BD(aci_sheet,row):
	tn_name = aci_sheet.cell_value(row,1)
	BD_name = aci_sheet.cell_value(row,2)
	VRF_name = aci_sheet.cell_value(row,3)
	subnet = aci_sheet.cell_value(row,4)
	advertise = aci_sheet.cell_value(row,5)
	L3_out = aci_sheet.cell_value(row,6)

	#Create Bridge Domain
	#fvBD1 = cobra.model.fv.BD(fvTenant, name=BD_name)
	print BD_name
	
	#Associate Bridge Domain to VRF
	#fvRsCtx1 = cobra.model.fv.RsCtx(fvBD1, tnFvCtxName=VRF_name)
	print VRF_name

	#Associate Web Bridge Domain with L3 out
	#fvRsBDToOut = cobra.model.fv.RsBDToOut(fvBD1, tnL3extOutName=L3_out)
	print L3_out

	#Create Subnets for the Bridge Domains, BD1 is allowed across VRFs
	if advertise == "yes":
		#fvSubnet1 = cobra.model.fv.Subnet(fvBD1, ip=subnet, scope='public,shared')
		print subnet +" is advertised"
	elif advertise == "no":
		#fvSubnet1 = cobra.model.fv.Subnet(fvBD1, ip=subnet, scope='private')
		print subnet + " is not advertised"






	#Define External L3 information
	#l3extOut = cobra.model.l3ext.Out(fvCommon, name=l3Out_name)
	#l3extInstP = cobra.model.l3ext.InstP(l3extOut, name=l3Out_name)

	#Associate Demo_Web Contract
	#fvRsCons1 = cobra.model.fv.RsCons(fvAEPg1, tnVzBrCPName='Demo_Web')





	#Commit to the apic
	#c = cobra.mit.request.ConfigRequest()
	#c.addMo(fvTenant)
	#md.commit(c)

#get VMWare VMM already created and present as choices
#def get_vmm():
#	vmmprovider = md.lookupByClass('vmmDomP', parentDn="uni")
#	for vmmd in vmmprovider:
#		vmm_convert =  str("{}".format(vmmd.rn))
#		(junk, vmm_spl) = vmm_convert.split('dom-')
#		print vmm_spl

#	vmm_choice = raw_input ("VMM Domain > ")
#	return vmm_choice

#start operations
start_xls()

