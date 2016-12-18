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


#open worksheet and find functions to run
def start_xls():
	aci_book = xlrd.open_workbook("EPG_Input.xlsx")
	aci_sheet = aci_book.sheet_by_index(0)

	for row in range(aci_sheet.nrows):
		for column in range(aci_sheet.ncols):
			if aci_sheet.cell_value(row,column) == "Create_EPG":
				Create_EPG(aci_sheet,row)
				print "Creating EPG"
			elif aci_sheet.cell_value(row,column) == "Create_BD":
				print "Creating Bridge Domain"
				Create_BD(aci_sheet,row)
			elif aci_sheet.cell_value(row,column) == "Create_Contract":
				print "Creating Contract"
				Create_Contract(aci_sheet,row)

#Create EPG
def Create_EPG (aci_sheet,row):
	#Login to APIC
	ls = cobra.mit.session.LoginSession('https://'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
	md = cobra.mit.access.MoDirectory(ls)
	md.login()

	#create variables by importing values from spreadsheet
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
	polUni = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(polUni, tn_name)
	print "The tenant name is: " + tn_name

	#create ANP
	fvAp = cobra.model.fv.Ap(fvTenant, name=ANP_name)
	print "The Applicaiton Profile name is:" + ANP_name

	#create EPGs
	fvAEPg1 = cobra.model.fv.AEPg(fvAp, name=EPG_name)
	print "The EPG name is: " + EPG_name

	#Associate EPGs with Bridge Domains
	fvRsBd1 = cobra.model.fv.RsBd(fvAEPg1, tnFvBDName=BD_name)
	print "EPG " + EPG_name + " is associated with the bridge domain: " + BD_name

	#Associate EPG with VMM Domain
	if VMM_name != "None":
		fvRsDomAtt1 = cobra.model.fv.RsDomAtt(fvAEPg1, tDn='uni/vmmp-VMware/dom-'+VMM_name, resImedcy=u'immediate')
		print "Associated with: " + VMM_name
	elif VMM_name == "None":
		print "No VMM Domain Selected"

	#need to add contract

	#Commit to the apic
	c = cobra.mit.request.ConfigRequest()
	c.addMo(fvTenant)
	md.commit(c)


# Create Bridge Domain
def Create_BD(aci_sheet,row):
	#Login to APIC
	ls = cobra.mit.session.LoginSession('https://'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
	md = cobra.mit.access.MoDirectory(ls)
	md.login()

	#define variables from spreadsheet
	tn_name = aci_sheet.cell_value(row,1)
	BD_name = aci_sheet.cell_value(row,2)
	VRF_name = aci_sheet.cell_value(row,3)
	subnet = aci_sheet.cell_value(row,4)
	advertise = aci_sheet.cell_value(row,5)
	L3_out = aci_sheet.cell_value(row,6)


	#Define top level pol
	polUni = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(polUni, tn_name)
	print tn_name

	#Create VRF
	fvCtx = cobra.model.fv.Ctx(fvTenant, name=VRF_name)
	print "VRF is: " + VRF_name

	#Create Bridge Domain
	fvBD1 = cobra.model.fv.BD(fvTenant, name=BD_name)
	print BD_name
	
	#Associate Bridge Domain to VRF
	fvRsCtx1 = cobra.model.fv.RsCtx(fvBD1, tnFvCtxName=VRF_name)
	print VRF_name


	#Create Subnets for the Bridge Domains, BD1 is allowed across VRFs
	if advertise == "yes":
		fvSubnet1 = cobra.model.fv.Subnet(fvBD1, ip=subnet, scope='public,shared')
		#Associate Web Bridge Domain with L3 out
		#fvRsBDToOut = cobra.model.fv.RsBDToOut(fvBD1, tnL3extOutName=L3_out)
		print subnet +" is advertised"
	elif advertise == "no":
		fvSubnet1 = cobra.model.fv.Subnet(fvBD1, ip=subnet)
		print subnet + " is not advertised"

	#Commit to the apic
	c = cobra.mit.request.ConfigRequest()
	c.addMo(fvTenant)
	md.commit(c)

# Create Contract and Filter
def Create_Contract(aci_sheet,row):
	#Login to APIC
	ls = cobra.mit.session.LoginSession('https://'+credentials.ACI_login["ipaddr"], credentials.ACI_login["username"], credentials.ACI_login["password"])
	md = cobra.mit.access.MoDirectory(ls)
	md.login()

	# Define Variables
	tn_name = aci_sheet.cell_value(row,1)
	Contract_name = aci_sheet.cell_value(row,2)
	subject_name = aci_sheet.cell_value(row,3)
	filter_name = aci_sheet.cell_value(row,4)
	proto_type = aci_sheet.cell_value(row,5)
	filter_port = aci_sheet.cell_value(row,6)
	contract_scope = aci_sheet.cell_value(row,7)
	if contract_scope == "VRF":
		contract_scope = "context"

	#Define top-level pol
	polUni = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(polUni, tn_name)

	#create contract
	vzBrCP = cobra.model.vz.BrCP(fvTenant, name=Contract_name, scope=contract_scope)

	# built the contract subject
	vzSubj = cobra.model.vz.Subj(vzBrCP, name=subject_name)
	vzRsSubjFiltAtt = cobra.model.vz.RsSubjFiltAtt(vzSubj, directives=u'none', tnVzFilterName=filter_name)

	# build the filter
	vzFilter = cobra.model.vz.Filter(fvTenant, name=filter_name)
	vzEntry = cobra.model.vz.Entry(vzFilter, name=filter_port, prot=proto_type, etherT=u'ip', dFromPort=filter_port, dToPort=filter_port)

	#Commit to the apic
	print "Creating contract " + Contract_name
	c = cobra.mit.request.ConfigRequest()
	c.addMo(fvTenant)
	md.commit(c)


#start operations
start_xls()

