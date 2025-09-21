<?xml version="1.0" encoding="UTF-8"?>
<SCL xmlns="http://www.iec.ch/61850/2003/SCL" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.iec.ch/61850/2003/SCL SCL.xsd" version="2007" revision="B" release="4">
  <Header id="TestSubstation" version="1.0" revision="1" toolID="SCD Generator" nameStructure="IEDName">
    <Text>Test substation SCD file for demonstration</Text>
  </Header>
  
  <Substation name="TestSubstation" desc="110kV Test Substation">
    <VoltageLevel name="110kV" desc="110kV Voltage Level" voltage="110000" nomFreq="50">
      <Bay name="Bay1" desc="Line Bay 1">
        <ConductingEquipment name="Q1" type="CBR" desc="Circuit Breaker">
          <LNode iedName="ProtIED1" ldInst="CTRL" lnClass="CSWI" lnInst="1"/>
        </ConductingEquipment>
        <ConductingEquipment name="T1" type="VTR" desc="Voltage Transformer">
          <LNode iedName="MeasIED1" ldInst="TVTR" lnClass="TVTR" lnInst="1"/>
        </ConductingEquipment>
      </Bay>
      <Bay name="Bay2" desc="Transformer Bay">
        <ConductingEquipment name="TR1" type="PTR" desc="Power Transformer">
          <LNode iedName="ProtIED2" ldInst="PTRC" lnClass="PTRC" lnInst="1"/>
        </ConductingEquipment>
      </Bay>
    </VoltageLevel>
  </Substation>
  
  <Communication>
    <SubNetwork name="StationBus" type="8-MMS" desc="Station Bus Network">
      <ConnectedAP iedName="ProtIED1" apName="AP1">
        <Address>
          <P type="IP">192.168.1.10</P>
          <P type="IP-SUBNET">255.255.255.0</P>
          <P type="IP-GATEWAY">192.168.1.1</P>
        </Address>
        <GSE ldInst="CTRL" cbName="GCB01">
          <Address>
            <P type="MAC-Address">01-0C-CD-01-00-01</P>
            <P type="APPID">0001</P>
            <P type="VLAN-ID">100</P>
          </Address>
        </GSE>
      </ConnectedAP>
      
      <ConnectedAP iedName="ProtIED2" apName="AP1">
        <Address>
          <P type="IP">192.168.1.11</P>
          <P type="IP-SUBNET">255.255.255.0</P>
          <P type="IP-GATEWAY">192.168.1.1</P>
        </Address>
        <SMV ldInst="MSVCB" cbName="MSVCB01">
          <Address>
            <P type="MAC-Address">01-0C-CD-04-00-01</P>
            <P type="APPID">4001</P>
            <P type="VLAN-ID">101</P>
          </Address>
        </SMV>
      </ConnectedAP>
      
      <ConnectedAP iedName="MeasIED1" apName="AP1">
        <Address>
          <P type="IP">192.168.1.12</P>
          <P type="IP-SUBNET">255.255.255.0</P>
          <P type="IP-GATEWAY">192.168.1.1</P>
        </Address>
      </ConnectedAP>
      
      <ConnectedAP iedName="ControlIED" apName="AP1">
        <Address>
          <P type="IP">192.168.1.13</P>
          <P type="IP-SUBNET">255.255.255.0</P>
          <P type="IP-GATEWAY">192.168.1.1</P>
        </Address>
      </ConnectedAP>
    </SubNetwork>
  </Communication>
  
  <IED name="ProtIED1" type="Protection" manufacturer="TestVendor" configVersion="1.0">
    <AccessPoint name="AP1">
      <Server>
        <Authentication none="true"/>
        <LDevice inst="CTRL">
          <LN0 lnClass="LLN0" inst="">
            <DataSet name="Events">
              <FCDA ldInst="CTRL" lnClass="CSWI" lnInst="1" doName="Pos" fc="ST"/>
              <FCDA ldInst="CTRL" lnClass="XCBR" lnInst="1" doName="Pos" fc="ST"/>
            </DataSet>
            <GSEControl name="GCB01" type="GOOSE" appID="Events" datSet="Events"/>
          </LN0>
          <LN lnClass="CSWI" inst="1" lnType="CSWIType">
            <DOI name="Pos">
              <DAI name="stVal">
                <Val>intermediate-state</Val>
              </DAI>
            </DOI>
          </LN>
          <LN lnClass="XCBR" inst="1" lnType="XCBRType"/>
        </LDevice>
      </Server>
    </AccessPoint>
  </IED>
  
  <IED name="ProtIED2" type="Protection" manufacturer="TestVendor" configVersion="1.0">
    <AccessPoint name="AP1">
      <Server>
        <Authentication none="true"/>
        <LDevice inst="MSVCB">
          <LN0 lnClass="LLN0" inst="">
            <DataSet name="MeasValues">
              <FCDA ldInst="MSVCB" lnClass="TCTR" lnInst="1" doName="Amp" fc="MX"/>
              <FCDA ldInst="MSVCB" lnClass="TVTR" lnInst="1" doName="Vol" fc="MX"/>
            </DataSet>
            <SampledValueControl name="MSVCB01" smvID="TestSMV01" datSet="MeasValues" smpRate="4000" nofASDU="8"/>
          </LN0>
          <LN lnClass="TCTR" inst="1" lnType="TCTRType"/>
          <LN lnClass="TVTR" inst="1" lnType="TVTRType"/>
        </LDevice>
        <LDevice inst="PTRC">
          <LN0 lnClass="LLN0" inst=""/>
          <LN lnClass="PTRC" inst="1" lnType="PTRCType"/>
        </LDevice>
      </Server>
    </AccessPoint>
  </IED>
  
  <IED name="MeasIED1" type="Measurement" manufacturer="TestVendor" configVersion="1.0">
    <AccessPoint name="AP1">
      <Server>
        <Authentication none="true"/>
        <LDevice inst="TVTR">
          <LN0 lnClass="LLN0" inst=""/>
          <LN lnClass="TVTR" inst="1" lnType="TVTRType"/>
        </LDevice>
      </Server>
    </AccessPoint>
  </IED>
  
  <IED name="ControlIED" type="Control" manufacturer="TestVendor" configVersion="1.0">
    <AccessPoint name="AP1">
      <Server>
        <Authentication none="true"/>
        <LDevice inst="CTRL">
          <LN0 lnClass="LLN0" inst=""/>
          <LN lnClass="GGIO" inst="1" lnType="GGIOType"/>
        </LDevice>
      </Server>
    </AccessPoint>
  </IED>
  
  <DataTypeTemplates>
    <LNodeType id="CSWIType" lnClass="CSWI">
      <DO name="Pos" type="DPCType"/>
      <DO name="BlkOpn" type="SPCType"/>
      <DO name="BlkCls" type="SPCType"/>
    </LNodeType>
    
    <LNodeType id="XCBRType" lnClass="XCBR">
      <DO name="Pos" type="DBPosType"/>
      <DO name="OpCnt" type="INSType"/>
    </LNodeType>
    
    <LNodeType id="TCTRType" lnClass="TCTR">
      <DO name="Amp" type="SAVType"/>
      <DO name="Rat" type="ASGType"/>
    </LNodeType>
    
    <LNodeType id="TVTRType" lnClass="TVTR">
      <DO name="Vol" type="SAVType"/>
      <DO name="VolSv" type="SAVType"/>
    </LNodeType>
    
    <LNodeType id="PTRCType" lnClass="PTRC">
      <DO name="Str" type="ACTType"/>
      <DO name="Op" type="ACTType"/>
    </LNodeType>
    
    <LNodeType id="GGIOType" lnClass="GGIO">
      <DO name="Ind1" type="SPSType"/>
      <DO name="SPCSO1" type="SPCType"/>
    </LNodeType>
    
    <DOType id="DPCType" cdc="DPC">
      <DA name="origin" fc="ST" dchg="true" type="ORG"/>
      <DA name="stVal" fc="ST" dchg="true" type="DbPosKind"/>
      <DA name="q" fc="ST" qchg="true" type="Quality"/>
      <DA name="t" fc="ST" type="Timestamp"/>
    </DOType>
    
    <DOType id="SPCType" cdc="SPC">
      <DA name="origin" fc="ST" dchg="true" type="ORG"/>
      <DA name="ctlVal" fc="CO" type="BOOLEAN"/>
      <DA name="operTm" fc="CO" type="Timestamp"/>
    </DOType>
    
    <DOType id="DBPosType" cdc="DPS">
      <DA name="stVal" fc="ST" dchg="true" type="DbPosKind"/>
      <DA name="q" fc="ST" qchg="true" type="Quality"/>
      <DA name="t" fc="ST" type="Timestamp"/>
    </DOType>
    
    <DOType id="INSType" cdc="INS">
      <DA name="stVal" fc="ST" dchg="true" type="INT32"/>
      <DA name="q" fc="ST" qchg="true" type="Quality"/>
      <DA name="t" fc="ST" type="Timestamp"/>
    </DOType>
    
    <DOType id="SAVType" cdc="SAV">
      <DA name="instMag" fc="MX" type="AnalogueValue"/>
      <DA name="q" fc="MX" qchg="true" type="Quality"/>
      <DA name="t" fc="MX" type="Timestamp"/>
    </DOType>
    
    <DOType id="ASGType" cdc="ASG">
      <DA name="setMag" fc="SP" dchg="true" type="AnalogueValue"/>
    </DOType>
    
    <DOType id="ACTType" cdc="ACT">
      <DA name="general" fc="ST" dchg="true" type="BOOLEAN"/>
      <DA name="q" fc="ST" qchg="true" type="Quality"/>
      <DA name="t" fc="ST" type="Timestamp"/>
    </DOType>
    
    <DOType id="SPSType" cdc="SPS">
      <DA name="stVal" fc="ST" dchg="true" type="BOOLEAN"/>
      <DA name="q" fc="ST" qchg="true" type="Quality"/>
      <DA name="t" fc="ST" type="Timestamp"/>
    </DOType>
    
    <DAType id="ORG">
      <BDA name="orCat" type="OriginatorCategoryKind"/>
      <BDA name="orIdent" type="OCTET64"/>
    </DAType>
    
    <DAType id="AnalogueValue">
      <BDA name="f" type="FLOAT32"/>
    </DAType>
    
    <EnumType id="DbPosKind">
      <EnumVal ord="0">intermediate-state</EnumVal>
      <EnumVal ord="1">off</EnumVal>
      <EnumVal ord="2">on</EnumVal>
      <EnumVal ord="3">bad-state</EnumVal>
    </EnumType>
    
    <EnumType id="OriginatorCategoryKind">
      <EnumVal ord="0">not-supported</EnumVal>
      <EnumVal ord="1">bay-control</EnumVal>
      <EnumVal ord="2">station-control</EnumVal>
      <EnumVal ord="3">remote-control</EnumVal>
      <EnumVal ord="4">automatic-bay</EnumVal>
      <EnumVal ord="5">automatic-station</EnumVal>
      <EnumVal ord="6">automatic-remote</EnumVal>
      <EnumVal ord="7">maintenance</EnumVal>
      <EnumVal ord="8">process</EnumVal>
    </EnumType>
  </DataTypeTemplates>
</SCL>