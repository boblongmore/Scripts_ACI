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
				print "Creating EPG"
			elif aci_sheet.cell_value(row,column) == "Create_Contract":
				print "Creating Contract"
				Create_Contract(aci_sheet,row)
			elif aci_sheet.cell_value(row,column) == "Create_BD":
				print "Creating Bridge Domain"
				Create_BD(aci_sheet,row)

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
	print EPG_name
	BD_name = ACI.BridgeDomain(aci_sheet.cell_value(row,8), tn_name)
	contract = ACI.Contract(aci_sheet.cell_value(row,9), tn_name)
	direction = aci_sheet.cell_value(row,10)

	EPG_name.add_bd(BD_name)

	#figure out direction of provider/consumer relationship
	if direction == 'consume':
		EPG_name.consume(contract)
	elif direction == 'provide':
		EPG_name.provide(contract)
	elif direction == '' or 'None':
		print 'No provider or consumer direction selected'

	#ensure tenant exists
	resp = session.push_to_apic(tn_name.get_url(), data=tn_name.get_json())
	if resp.ok:
		print 'Tenant %s deployed' % tn_name
		print 'EPG %s deployed' % EPG_name
		print '=' * 20

def Create_BD(aci_sheet,row):
	#call login function and return session 
	session = APIC_login()

    #create variables by importing values from spreadsheet	
	tn_name = ACI.Tenant(aci_sheet.cell_value(row,1))
	VRF_name = ACI.Context(aci_sheet.cell_value(row,3), tn_name)
	BD_name = ACI.BridgeDomain(aci_sheet.cell_value(row,2), tn_name)
	advertise = aci_sheet.cell_value(row, 7)
	subnet = ACI.Subnet((aci_sheet.cell_value(row,2) + '_subnet'), BD_name)
	subnet.set_addr(aci_sheet.cell_value(row,6))
	OutsideL3 = ACI.OutsideL3(aci_sheet.cell_value(row, 8), tn_name)
	L3_out = aci_sheet.cell_value(row, 8)

	BD_name.add_context(VRF_name)
	BD_name.add_subnet(subnet)

	if advertise == "yes":
		BD_name.add_l3out(OutsideL3)

	resp = session.push_to_apic(tn_name.get_url(), data=tn_name.get_json())
	if resp.ok:
		print 'Bridge Domain %s deployed' %BD_name
		print '=' * 20

def Create_Contract(aci_sheet,row):
	#call login function and return session 
	session = APIC_login()

	#create variables by importing values from spreadsheet
	tn_name = ACI.Tenant(aci_sheet.cell_value(row,1))
	print tn_name
	contract_name = ACI.Contract(aci_sheet.cell_value(row,2), tn_name)
	print contract_name
	filter_entry = ACI.FilterEntry('PythonFilter', 
									applyToFrag='no', 
									arpOpc='unspecified', 
									dFromPort=str(aci_sheet.cell_value(row,8)), 
									dToPort=str(aci_sheet.cell_value(row,9)), 
									etherT='ip',
									prot=(aci_sheet.cell_value(row,7)),
									sFromPort='1',
									sToPort='65535',
									tcpRules='unspecified',
									parent=contract_name)
	print filter_entry


	resp = session.push_to_apic(tn_name.get_url(), data=tn_name.get_json())
	if resp.ok:
		print 'Contract %s deployed' %contract_name
		print '=' * 20
	else:
		print 'contract %s not deployed' %contract_name




if __name__ == '__main__':
    main()