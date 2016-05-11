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
from cobra.internal.codec.xmlcodec import toXMLStr
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

#Login to APIC
ls = cobra.mit.session.LoginSession('https://10.207.10.100', 'admin', 'password')
md = cobra.mit.access.MoDirectory(ls)
md.login()

#create Tenant
def tenantCreate (tnName, epg1, epg2, epg3, l3Out, VMM):
	polUni = cobra.model.pol.Uni('')
	fvTenant = cobra.model.fv.Tenant(polUni, tnName)
	fvCommon = cobra.model.fv.Tenant(polUni, 'common')

	#Create VRF
	fvCtx1 = cobra.model.fv.Ctx(fvTenant, name=tnName+'_VRF')

	#Create Bridge Domain
	fvBD1 = cobra.model.fv.BD(fvTenant, name=epg1+'_BD')
	fvBD2 = cobra.model.fv.BD(fvTenant, name=epg2+'_BD')
	fvBD3 = cobra.model.fv.BD(fvTenant, name=epg3+'_BD')

	#Associate Bridge Domain to VRF
	fvRsCtx1 = cobra.model.fv.RsCtx(fvBD1, tnFvCtxName=tnName+'_VRF')
	fvRsCtx2 = cobra.model.fv.RsCtx(fvBD2, tnFvCtxName=tnName+'_VRF')
	fvRsCtx3 = cobra.model.fv.RsCtx(fvBD3, tnFvCtxName=tnName+'_VRF')

	#Associate Web Bridge Domain with L3 out
	fvRsBDToOut = cobra.model.fv.RsBDToOut(fvBD1, tnL3extOutName=l3Out)

	#Create Subnets for the Bridge Domains, BD1 is allowed across VRFs
	fvSubnet1 = cobra.model.fv.Subnet(fvBD1, ip=u'10.207.132.1/24', scope='public,shared')
	fvSubnet2 = cobra.model.fv.Subnet(fvBD2, ip=u'10.207.133.1/24', scope='private')
	fvSubnet3 = cobra.model.fv.Subnet(fvBD3, ip=u'10.207.134.1/24', scope='private')

	#create ANP
	fvAp = cobra.model.fv.Ap(fvTenant, name=tnName+'_ANP')

	#create EPGs
	fvAEPg1 = cobra.model.fv.AEPg(fvAp, name=tnName+'_'+epg1)
	fvAEPg2 = cobra.model.fv.AEPg(fvAp, name=tnName+'_'+epg2)
	fvAEPg3 = cobra.model.fv.AEPg(fvAp, name=tnName+'_'+epg3)

	#Associate EPGs with Bridge Domains
	fvRsBd1 = cobra.model.fv.RsBd(fvAEPg1, tnFvBDName=epg1+'_BD')
	fvRsBd2 = cobra.model.fv.RsBd(fvAEPg2, tnFvBDName=epg2+'_BD')
	fvRsBd3 = cobra.model.fv.RsBd(fvAEPg3, tnFvBDName=epg3+'_BD')

	#Define External L3 information
	l3extOut = cobra.model.l3ext.Out(fvCommon, name=l3Out)
	l3extInstP = cobra.model.l3ext.InstP(l3extOut, name=l3Out)

	#Associate Demo_Web Contract
	#fvRsCons1 = cobra.model.fv.RsCons(fvAEPg1, tnVzBrCPName='Demo_Web')

	#Associate EPG with VMM Domain
	fvRsDomAtt1 = cobra.model.fv.RsDomAtt(fvAEPg1, tDn='uni/vmmp-VMware/dom-'+VMM, resImedcy=u'immediate')
	fvRsDomAtt2 = cobra.model.fv.RsDomAtt(fvAEPg2, tDn='uni/vmmp-VMware/dom-'+VMM, resImedcy=u'immediate')
	fvRsDomAtt3 = cobra.model.fv.RsDomAtt(fvAEPg3, tDn='uni/vmmp-VMware/dom-'+VMM, resImedcy=u'immediate')





	#Commit to the apic
	c = cobra.mit.request.ConfigRequest()
	c.addMo(fvTenant)
	md.commit(c)

#get VMWare VMM already created and present as choices
def get_vmm():
	vmmprovider = md.lookupByClass('vmmDomP', parentDn="uni")
	for vmmd in vmmprovider:
		print "{}".format(vmmd.rn)
	vmm_choice = raw_input ("VMM Domain > ")
	return(vmm_choice)

#start operations
tenant_input = raw_input ("Tenant Name > ")
epg1_input = raw_input ("EPG1 > ")
epg2_input = raw_input ("EPG2 > ")
epg3_input = raw_input ("EPG3 > ")
l3Out = raw_input ("L3 Out > ")
#VMM = raw_input ("VMM Domain > ")
VMM = get_vmm()

tenantCreate(tenant_input, epg1_input, epg2_input, epg3_input, l3Out, VMM)


