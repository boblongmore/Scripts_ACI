#!/usr/bin/env python

import xlrd
import acitoolkit.acitoolkit as ACI
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import credentials


def main():
	aci_book = xlrd.open_workbook("EPG_Input.xlsx")
	aci_sheet = aci_book.sheet_by_index(0)

	for row in range(aci_sheet.nrows):
		for column in range(aci_sheet.ncols):
			if aci_sheet.cell_value(row,column) == "Create_EPG":
				Create_EPG(aci_sheet,row)
			#elif aci_sheet.cell_value(row,column) == "Create_Contract":
			#	print "Creating Contract"
			elif aci_sheet.cell_value(row,column) == "Create_BD":
				print "Creating Bridge Domain"
				Create_BD(aci_sheet,row)
			#elif aci_sheet.cell_value(row,column) == "Create_Contract":
			#	print "Creating Contract"
			#	Create_Contract(aci_sheet,row)

def APIC_login():
	url = credentials.ACI_login['ipaddr']
	login = credentials.ACI_login['username']
	password = credentials.ACI_login['password']
    # Login to APIC
	session = ACI.Session(url, login, password)
	resp = session.login()
	if not resp.ok:
		print('%% Could not login to APIC')
		sys.exit(0)
	return(session)

def Create_EPG(aci_sheet,row):
	#call login function and return session 
	session = APIC_login()

    #create variables by importing values from spreadsheet
	tn_name = ACI.Tenant(aci_sheet.cell_value(row,1))
	ANP_name = ACI.AppProfile(aci_sheet.cell_value(row,2), tn_name)
	EPG_name = ACI.EPG(aci_sheet.cell_value(row,3), ANP_name)
	BD_name = ACI.BridgeDomain(aci_sheet.cell_value(row,8), tn_name)

	EPG_name.add_bd(BD_name)

	#ensure tenant exists
	resp = session.push_to_apic(tn_name.get_url(), data=tn_name.get_json())
	if resp.ok:
		print 'Tenant %s deployed' % tn_name

def Create_BD(aci_sheet,row):
	#call login function and return session 
	session = APIC_login()

    #create variables by importing values from spreadsheet	
	tn_name = ACI.Tenant(aci_sheet.cell_value(row,1))
	#ANP_name = ACI.AppProfile(aci_sheet.cell_value(row,2), tn_name)
	#EPG_name = ACI.EPG(aci_sheet.cell_value(row,3), ANP_name)
	VRF_name = ACI.Context(aci_sheet.cell_value(row,3), tn_name)
	BD_name = ACI.BridgeDomain(aci_sheet.cell_value(row,2), tn_name)
	subnet = ACI.Subnet((aci_sheet.cell_value(row,2) + '_subnet'), BD_name)
	print subnet
	subnet.set_addr(aci_sheet.cell_value(row,6))
	#L3_out = aci_sheet.cell_value(row,6)
	#advertise = aci_sheet.cell_value(row,5)


	BD_name.add_context(VRF_name)
	BD_name.add_subnet(subnet)

	#if advertise == "yes":
	#	BD_name.add_l3out(L3_out)

	resp = session.push_to_apic(tn_name.get_url(), data=tn_name.get_json())
	if resp.ok:
		print 'Bridge Domain deployed'



if __name__ == '__main__':
    main()