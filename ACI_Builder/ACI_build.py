#!/usr/bin/env python

import xlrd
import acitoolkit.acitoolkit as ACI
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import credentials
import re


def main():
    aci_book = xlrd.open_workbook("EPG_Input.xlsx")
    aci_sheet = aci_book.sheet_by_index(0)

    for row in range(aci_sheet.nrows):
        for column in range(aci_sheet.ncols):
            if aci_sheet.cell_value(row, column) == "Create_EPG":
                Create_EPG(aci_sheet, row)
                print "Creating EPG"
            elif aci_sheet.cell_value(row, column) == "Create_Contract":
                print "Creating Contract"
                Create_Contract(aci_sheet, row)
            elif aci_sheet.cell_value(row, column) == "Create_BD":
                print "Creating Bridge Domain"
                Create_BD(aci_sheet, row)


def apic_login():
    url = credentials.ACI_login['ipaddr']
    login = credentials.ACI_login['username']
    password = credentials.ACI_login['password']
    # Login to APIC
    session = ACI.Session(url, login, password)
    resp = session.login()
    if not resp.ok:
        print('%% Could not login to APIC')
        sys.exit(0)
    return (session)


def Create_EPG(aci_sheet, row):
    # call login function and return session
    session = apic_login()

    # create variables by importing values from spreadsheet
    tn_name = ACI.Tenant(aci_sheet.cell_value(row, 1))
    ANP_name = ACI.AppProfile(aci_sheet.cell_value(row, 2), tn_name)
    EPG_name = ACI.EPG(aci_sheet.cell_value(row, 3), ANP_name)
    print EPG_name
    BD_name = ACI.BridgeDomain(aci_sheet.cell_value(row, 8), tn_name)
    contract = ACI.Contract(aci_sheet.cell_value(row, 9), tn_name)
    direction = aci_sheet.cell_value(row, 10)
    vmm_name = ACI.EPGDomain.get_by_name(session, (aci_sheet.cell_value(row, 7)))
    phy_domain_name = ACI.EPGDomain.get_by_name(session, (aci_sheet.cell_value(row, 6)))

    #associated EPG with Bridge Domain
    EPG_name.add_bd(BD_name)

    #associate EPG with VMM DOmain
    if vmm_name == None:
        print "no VMM domain selected"
    else:
        EPG_name.add_infradomain(vmm_name)
        print "EPG %s associated with vmm domain %s" % (EPG_name, vmm_name)

    #set EPG for intra-EPG isolation
    #EPG_name.set_intra_epg_isolation('enforced')

    # figure out direction of provider/consumer relationship
    if direction == 'consume':
        EPG_name.consume(contract)
    elif direction == 'provide':
        EPG_name.provide(contract)
    elif direction == '' or 'None':
        print 'No provider or consumer direction selected'

    # define the physical interfaces
    #single_port matches the format that should be on the spreadsheet for a single port with the pod,leaf,blade,port format
    single_port = re.compile('.*/.*/.*/.*')
    #The vpc_port matches any text
    vpc_port = re.compile('.*.')
    get_phys = aci_sheet.cell_value(row,4)

    #if the description matches the single port format, the string is split into the different values
    if single_port.match(get_phys) is not None:
        get_phys_split = get_phys.split('/')
        intf1 = ACI.Interface('eth', get_phys_split[0], get_phys_split[1], get_phys_split[2], get_phys_split[3])
        # define the encapsulation
        get_vlan_id = int(aci_sheet.cell_value(row, 5))
        print get_vlan_id
        static_encap_if = ACI.L2Interface('encap_' + str(get_vlan_id), 'vlan', get_vlan_id)

        # attach encap to physical interface
        static_encap_if.attach(intf1)

        # attach static port binding to EPG
        EPG_name.attach(static_encap_if)
        print 'EPG %s is associated with interface %s with encap vlan-' % (EPG_name, intf1, get_vlan_id)
    #if the vpc_port matches, the second sheet of the spreadsheet is consulted to get the physical interfaces of the VPC name
    elif vpc_port.match(get_phys):
        phys_aci_book = xlrd.open_workbook("EPG_Input.xlsx")
        phys_aci_sheet = phys_aci_book.sheet_by_index(1)
        for row in range(phys_aci_sheet.nrows):
            for column in range(phys_aci_sheet.ncols):
                if phys_aci_sheet.cell_value(row, column) == get_phys:
                    vpc_pair = phys_aci_sheet.cell_value(row,1)
                    interface_selector = phys_aci_sheet.cell_value(row,2)
                    vpc_leaf_split = vpc_pair.split('-')
                    intf_selector_split = interface_selector.split(',')
                    intf1 = ACI.Interface('eth', '1', vpc_leaf_split[0],'1',intf_selector_split[0])
                    intf2 = ACI.Interface('eth', '1', vpc_leaf_split[1],'1',intf_selector_split[0])
                    pc1 = ACI.PortChannel(get_phys)
                    pc1.attach(intf1)
                    pc1.attach(intf2)

                    # define the encapsulation
                    get_vlan_id = int(aci_sheet.cell_value(row, 5))
                    static_encap_if = ACI.L2Interface('encap_' + str(get_vlan_id), 'vlan', get_vlan_id)

                    # attach encap to physical interface
                    static_encap_if.attach(pc1)

                    # attach static port binding to EPG
                    EPG_name.attach(static_encap_if)
                    print 'EPG %s is associated with VPC %s with encap vlan-%s' % (EPG_name, get_phys, get_vlan_id)


    #associate EPG with physical domain
    if phy_domain_name == None:
        print 'no physical domain selected'
    else:
        EPG_name.add_infradomain(phy_domain_name)
        print 'EPG %s associated with physical domain %s' % (EPG_name, phy_domain_name)



    # ensure tenant exists and push configuration
    resp = session.push_to_apic(tn_name.get_url(), data=tn_name.get_json())
    if resp.ok:
        print 'Tenant %s deployed' % tn_name
        print 'EPG %s deployed' % EPG_name
        print '=' * 20


def Create_BD(aci_sheet, row):
    # call login function and return session
    session = apic_login()

	# create variables by importing values from spreadsheet
    tn_name = ACI.Tenant(aci_sheet.cell_value(row, 1))
    VRF_name = ACI.Context(aci_sheet.cell_value(row, 3), tn_name)
    BD_name = ACI.BridgeDomain(aci_sheet.cell_value(row, 2), tn_name)
    advertise = aci_sheet.cell_value(row, 7)
    subnet = ACI.Subnet((aci_sheet.cell_value(row, 2) + '_subnet'), BD_name)
    subnet.set_addr(aci_sheet.cell_value(row, 6))
    OutsideL3 = ACI.OutsideL3(aci_sheet.cell_value(row, 8), tn_name)
    L3_out = aci_sheet.cell_value(row, 8)

    BD_name.add_context(VRF_name)
    BD_name.add_subnet(subnet)

    if advertise == "yes":
        BD_name.add_l3out(OutsideL3)

    resp = session.push_to_apic(tn_name.get_url(), data=tn_name.get_json())
    if resp.ok:
        print 'Bridge Domain %s deployed' % BD_name
        print '=' * 20


def Create_Contract(aci_sheet, row):
    # call login function and return session
    session = apic_login()

    # create variables by importing values from spreadsheet
    tn_name = ACI.Tenant(aci_sheet.cell_value(row, 1))
    print tn_name
    contract_name = ACI.Contract(aci_sheet.cell_value(row, 2), tn_name)
    print contract_name
    filter_entry = ACI.FilterEntry('PythonFilter',
                                   applyToFrag='no',
                                   arpOpc='unspecified',
                                   dFromPort=str(aci_sheet.cell_value(row, 8)),
                                   dToPort=str(aci_sheet.cell_value(row, 9)),
                                   etherT='ip',
                                   prot=(aci_sheet.cell_value(row, 7)),
                                   sFromPort='1',
                                   sToPort='65535',
                                   tcpRules='unspecified',
                                   parent=contract_name)
    print filter_entry

    resp = session.push_to_apic(tn_name.get_url(), data=tn_name.get_json())
    if resp.ok:
        print 'Contract %s deployed' % contract_name
        print '=' * 20
    else:
        print 'contract %s not deployed' % contract_name


if __name__ == '__main__':
    main()
