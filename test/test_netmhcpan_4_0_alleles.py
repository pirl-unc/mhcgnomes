from mhcgnomes import parse, Allele, Gene, AlleleWithoutGene

def test_BoLA_T2C():
    result = parse('BoLA-T2C')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("BoLA-T2C"): %s' % (result,)

def test_Chi_B0401():
    result = parse('Chi-B0401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Chi-B0401"): %s' % (result,)

def test_Chi_B1201():
    result = parse('Chi-B1201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Chi-B1201"): %s' % (result,)

def test_Chi_B1501():
    result = parse('Chi-B1501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Chi-B1501"): %s' % (result,)

def test_H_2_Lq():
    result = parse('H-2-Lq')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H-2-Lq"): %s' % (result,)

def test_H2_Db():
    result = parse('H2-Db')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H2-Db"): %s' % (result,)

def test_H2_Dd():
    result = parse('H2-Dd')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H2-Dd"): %s' % (result,)

def test_H2_Kb():
    result = parse('H2-Kb')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H2-Kb"): %s' % (result,)

def test_H2_Kd():
    result = parse('H2-Kd')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H2-Kd"): %s' % (result,)

def test_H2_Kk():
    result = parse('H2-Kk')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H2-Kk"): %s' % (result,)

def test_H2_Ld():
    result = parse('H2-Ld')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H2-Ld"): %s' % (result,)

def test_H2_Qa1():
    result = parse('H2-Qa1')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H2-Qa1"): %s' % (result,)

def test_H2_Qa2():
    result = parse('H2-Qa2')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("H2-Qa2"): %s' % (result,)

def test_HLA_A0101():
    result = parse('HLA-A0101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0101"): %s' % (result,)

def test_HLA_A0102():
    result = parse('HLA-A0102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0102"): %s' % (result,)

def test_HLA_A0103():
    result = parse('HLA-A0103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0103"): %s' % (result,)

def test_HLA_A0104():
    result = parse('HLA-A0104')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0104"): %s' % (result,)

def test_HLA_A0106():
    result = parse('HLA-A0106')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0106"): %s' % (result,)

def test_HLA_A0107():
    result = parse('HLA-A0107')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0107"): %s' % (result,)

def test_HLA_A0108():
    result = parse('HLA-A0108')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0108"): %s' % (result,)

def test_HLA_A0109():
    result = parse('HLA-A0109')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0109"): %s' % (result,)

def test_HLA_A0110():
    result = parse('HLA-A0110')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0110"): %s' % (result,)

def test_HLA_A0111():
    result = parse('HLA-A0111')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0111"): %s' % (result,)

def test_HLA_A0112():
    result = parse('HLA-A0112')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0112"): %s' % (result,)

def test_HLA_A0113():
    result = parse('HLA-A0113')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0113"): %s' % (result,)

def test_HLA_A0114():
    result = parse('HLA-A0114')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0114"): %s' % (result,)

def test_HLA_A0115():
    result = parse('HLA-A0115')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0115"): %s' % (result,)

def test_HLA_A0117():
    result = parse('HLA-A0117')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0117"): %s' % (result,)

def test_HLA_A0118():
    result = parse('HLA-A0118')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0118"): %s' % (result,)

def test_HLA_A0119():
    result = parse('HLA-A0119')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0119"): %s' % (result,)

def test_HLA_A0120():
    result = parse('HLA-A0120')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0120"): %s' % (result,)

def test_HLA_A0121():
    result = parse('HLA-A0121')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0121"): %s' % (result,)

def test_HLA_A0122():
    result = parse('HLA-A0122')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0122"): %s' % (result,)

def test_HLA_A0123():
    result = parse('HLA-A0123')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0123"): %s' % (result,)

def test_HLA_A0124():
    result = parse('HLA-A0124')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0124"): %s' % (result,)

def test_HLA_A0125():
    result = parse('HLA-A0125')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0125"): %s' % (result,)

def test_HLA_A0126():
    result = parse('HLA-A0126')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0126"): %s' % (result,)

def test_HLA_A0201():
    result = parse('HLA-A0201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0201"): %s' % (result,)

def test_HLA_A0202():
    result = parse('HLA-A0202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0202"): %s' % (result,)

def test_HLA_A0203():
    result = parse('HLA-A0203')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0203"): %s' % (result,)

def test_HLA_A0204():
    result = parse('HLA-A0204')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0204"): %s' % (result,)

def test_HLA_A0205():
    result = parse('HLA-A0205')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0205"): %s' % (result,)

def test_HLA_A0206():
    result = parse('HLA-A0206')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0206"): %s' % (result,)

def test_HLA_A0207():
    result = parse('HLA-A0207')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0207"): %s' % (result,)

def test_HLA_A0208():
    result = parse('HLA-A0208')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0208"): %s' % (result,)

def test_HLA_A0209():
    result = parse('HLA-A0209')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0209"): %s' % (result,)

def test_HLA_A0210():
    result = parse('HLA-A0210')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0210"): %s' % (result,)

def test_HLA_A0211():
    result = parse('HLA-A0211')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0211"): %s' % (result,)

def test_HLA_A0212():
    result = parse('HLA-A0212')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0212"): %s' % (result,)

def test_HLA_A0213():
    result = parse('HLA-A0213')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0213"): %s' % (result,)

def test_HLA_A0214():
    result = parse('HLA-A0214')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0214"): %s' % (result,)

def test_HLA_A0215():
    result = parse('HLA-A0215')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0215"): %s' % (result,)

def test_HLA_A0216():
    result = parse('HLA-A0216')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0216"): %s' % (result,)

def test_HLA_A0217():
    result = parse('HLA-A0217')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0217"): %s' % (result,)

def test_HLA_A0218():
    result = parse('HLA-A0218')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0218"): %s' % (result,)

def test_HLA_A0219():
    result = parse('HLA-A0219')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0219"): %s' % (result,)

def test_HLA_A0220():
    result = parse('HLA-A0220')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0220"): %s' % (result,)

def test_HLA_A0221():
    result = parse('HLA-A0221')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0221"): %s' % (result,)

def test_HLA_A0222():
    result = parse('HLA-A0222')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0222"): %s' % (result,)

def test_HLA_A0224():
    result = parse('HLA-A0224')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0224"): %s' % (result,)

def test_HLA_A0225():
    result = parse('HLA-A0225')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0225"): %s' % (result,)

def test_HLA_A0226():
    result = parse('HLA-A0226')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0226"): %s' % (result,)

def test_HLA_A0227():
    result = parse('HLA-A0227')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0227"): %s' % (result,)

def test_HLA_A0228():
    result = parse('HLA-A0228')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0228"): %s' % (result,)

def test_HLA_A0229():
    result = parse('HLA-A0229')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0229"): %s' % (result,)

def test_HLA_A0230():
    result = parse('HLA-A0230')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0230"): %s' % (result,)

def test_HLA_A0231():
    result = parse('HLA-A0231')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0231"): %s' % (result,)

def test_HLA_A0233():
    result = parse('HLA-A0233')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0233"): %s' % (result,)

def test_HLA_A0234():
    result = parse('HLA-A0234')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0234"): %s' % (result,)

def test_HLA_A0235():
    result = parse('HLA-A0235')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0235"): %s' % (result,)

def test_HLA_A0236():
    result = parse('HLA-A0236')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0236"): %s' % (result,)

def test_HLA_A0237():
    result = parse('HLA-A0237')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0237"): %s' % (result,)

def test_HLA_A0238():
    result = parse('HLA-A0238')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0238"): %s' % (result,)

def test_HLA_A0239():
    result = parse('HLA-A0239')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0239"): %s' % (result,)

def test_HLA_A0240():
    result = parse('HLA-A0240')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0240"): %s' % (result,)

def test_HLA_A0241():
    result = parse('HLA-A0241')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0241"): %s' % (result,)

def test_HLA_A0242():
    result = parse('HLA-A0242')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0242"): %s' % (result,)

def test_HLA_A0243():
    result = parse('HLA-A0243')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0243"): %s' % (result,)

def test_HLA_A0244():
    result = parse('HLA-A0244')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0244"): %s' % (result,)

def test_HLA_A0245():
    result = parse('HLA-A0245')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0245"): %s' % (result,)

def test_HLA_A0246():
    result = parse('HLA-A0246')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0246"): %s' % (result,)

def test_HLA_A0247():
    result = parse('HLA-A0247')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0247"): %s' % (result,)

def test_HLA_A0248():
    result = parse('HLA-A0248')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0248"): %s' % (result,)

def test_HLA_A0249():
    result = parse('HLA-A0249')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0249"): %s' % (result,)

def test_HLA_A0250():
    result = parse('HLA-A0250')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0250"): %s' % (result,)

def test_HLA_A0251():
    result = parse('HLA-A0251')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0251"): %s' % (result,)

def test_HLA_A0252():
    result = parse('HLA-A0252')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0252"): %s' % (result,)

def test_HLA_A0254():
    result = parse('HLA-A0254')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0254"): %s' % (result,)

def test_HLA_A0255():
    result = parse('HLA-A0255')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0255"): %s' % (result,)

def test_HLA_A0256():
    result = parse('HLA-A0256')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0256"): %s' % (result,)

def test_HLA_A0257():
    result = parse('HLA-A0257')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0257"): %s' % (result,)

def test_HLA_A0258():
    result = parse('HLA-A0258')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0258"): %s' % (result,)

def test_HLA_A0259():
    result = parse('HLA-A0259')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0259"): %s' % (result,)

def test_HLA_A0260():
    result = parse('HLA-A0260')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0260"): %s' % (result,)

def test_HLA_A0261():
    result = parse('HLA-A0261')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0261"): %s' % (result,)

def test_HLA_A0262():
    result = parse('HLA-A0262')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0262"): %s' % (result,)

def test_HLA_A0263():
    result = parse('HLA-A0263')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0263"): %s' % (result,)

def test_HLA_A0264():
    result = parse('HLA-A0264')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0264"): %s' % (result,)

def test_HLA_A0265():
    result = parse('HLA-A0265')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0265"): %s' % (result,)

def test_HLA_A0266():
    result = parse('HLA-A0266')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0266"): %s' % (result,)

def test_HLA_A0267():
    result = parse('HLA-A0267')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0267"): %s' % (result,)

def test_HLA_A0268():
    result = parse('HLA-A0268')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0268"): %s' % (result,)

def test_HLA_A0269():
    result = parse('HLA-A0269')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0269"): %s' % (result,)

def test_HLA_A0270():
    result = parse('HLA-A0270')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0270"): %s' % (result,)

def test_HLA_A0271():
    result = parse('HLA-A0271')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0271"): %s' % (result,)

def test_HLA_A0272():
    result = parse('HLA-A0272')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0272"): %s' % (result,)

def test_HLA_A0273():
    result = parse('HLA-A0273')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0273"): %s' % (result,)

def test_HLA_A0274():
    result = parse('HLA-A0274')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0274"): %s' % (result,)

def test_HLA_A0275():
    result = parse('HLA-A0275')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0275"): %s' % (result,)

def test_HLA_A0276():
    result = parse('HLA-A0276')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0276"): %s' % (result,)

def test_HLA_A0277():
    result = parse('HLA-A0277')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0277"): %s' % (result,)

def test_HLA_A0278():
    result = parse('HLA-A0278')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0278"): %s' % (result,)

def test_HLA_A0279():
    result = parse('HLA-A0279')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0279"): %s' % (result,)

def test_HLA_A0280():
    result = parse('HLA-A0280')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0280"): %s' % (result,)

def test_HLA_A0281():
    result = parse('HLA-A0281')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0281"): %s' % (result,)

def test_HLA_A0283():
    result = parse('HLA-A0283')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0283"): %s' % (result,)

def test_HLA_A0284():
    result = parse('HLA-A0284')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0284"): %s' % (result,)

def test_HLA_A0285():
    result = parse('HLA-A0285')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0285"): %s' % (result,)

def test_HLA_A0286():
    result = parse('HLA-A0286')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0286"): %s' % (result,)

def test_HLA_A0287():
    result = parse('HLA-A0287')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0287"): %s' % (result,)

def test_HLA_A0289():
    result = parse('HLA-A0289')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0289"): %s' % (result,)

def test_HLA_A0290():
    result = parse('HLA-A0290')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0290"): %s' % (result,)

def test_HLA_A0291():
    result = parse('HLA-A0291')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0291"): %s' % (result,)

def test_HLA_A0292():
    result = parse('HLA-A0292')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0292"): %s' % (result,)

def test_HLA_A0293():
    result = parse('HLA-A0293')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0293"): %s' % (result,)

def test_HLA_A0295():
    result = parse('HLA-A0295')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0295"): %s' % (result,)

def test_HLA_A0296():
    result = parse('HLA-A0296')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0296"): %s' % (result,)

def test_HLA_A0297():
    result = parse('HLA-A0297')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0297"): %s' % (result,)

def test_HLA_A0299():
    result = parse('HLA-A0299')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0299"): %s' % (result,)

def test_HLA_A0301():
    result = parse('HLA-A0301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0301"): %s' % (result,)

def test_HLA_A0302():
    result = parse('HLA-A0302')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0302"): %s' % (result,)

def test_HLA_A0303():
    result = parse('HLA-A0303')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0303"): %s' % (result,)

def test_HLA_A0304():
    result = parse('HLA-A0304')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0304"): %s' % (result,)

def test_HLA_A0305():
    result = parse('HLA-A0305')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0305"): %s' % (result,)

def test_HLA_A0306():
    result = parse('HLA-A0306')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0306"): %s' % (result,)

def test_HLA_A0307():
    result = parse('HLA-A0307')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0307"): %s' % (result,)

def test_HLA_A0308():
    result = parse('HLA-A0308')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0308"): %s' % (result,)

def test_HLA_A0309():
    result = parse('HLA-A0309')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0309"): %s' % (result,)

def test_HLA_A0310():
    result = parse('HLA-A0310')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0310"): %s' % (result,)

def test_HLA_A0312():
    result = parse('HLA-A0312')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0312"): %s' % (result,)

def test_HLA_A0313():
    result = parse('HLA-A0313')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0313"): %s' % (result,)

def test_HLA_A0314():
    result = parse('HLA-A0314')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0314"): %s' % (result,)

def test_HLA_A0315():
    result = parse('HLA-A0315')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0315"): %s' % (result,)

def test_HLA_A0316():
    result = parse('HLA-A0316')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0316"): %s' % (result,)

def test_HLA_A0317():
    result = parse('HLA-A0317')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0317"): %s' % (result,)

def test_HLA_A0318():
    result = parse('HLA-A0318')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0318"): %s' % (result,)

def test_HLA_A0319():
    result = parse('HLA-A0319')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0319"): %s' % (result,)

def test_HLA_A0320():
    result = parse('HLA-A0320')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0320"): %s' % (result,)

def test_HLA_A0321():
    result = parse('HLA-A0321')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0321"): %s' % (result,)

def test_HLA_A0322():
    result = parse('HLA-A0322')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0322"): %s' % (result,)

def test_HLA_A0323():
    result = parse('HLA-A0323')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0323"): %s' % (result,)

def test_HLA_A0324():
    result = parse('HLA-A0324')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0324"): %s' % (result,)

def test_HLA_A0325():
    result = parse('HLA-A0325')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0325"): %s' % (result,)

def test_HLA_A0326():
    result = parse('HLA-A0326')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0326"): %s' % (result,)

def test_HLA_A0327():
    result = parse('HLA-A0327')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0327"): %s' % (result,)

def test_HLA_A0328():
    result = parse('HLA-A0328')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0328"): %s' % (result,)

def test_HLA_A0329():
    result = parse('HLA-A0329')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0329"): %s' % (result,)

def test_HLA_A0330():
    result = parse('HLA-A0330')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A0330"): %s' % (result,)

def test_HLA_A1101():
    result = parse('HLA-A1101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1101"): %s' % (result,)

def test_HLA_A1102():
    result = parse('HLA-A1102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1102"): %s' % (result,)

def test_HLA_A1103():
    result = parse('HLA-A1103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1103"): %s' % (result,)

def test_HLA_A1104():
    result = parse('HLA-A1104')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1104"): %s' % (result,)

def test_HLA_A1105():
    result = parse('HLA-A1105')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1105"): %s' % (result,)

def test_HLA_A1106():
    result = parse('HLA-A1106')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1106"): %s' % (result,)

def test_HLA_A1107():
    result = parse('HLA-A1107')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1107"): %s' % (result,)

def test_HLA_A1108():
    result = parse('HLA-A1108')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1108"): %s' % (result,)

def test_HLA_A1109():
    result = parse('HLA-A1109')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1109"): %s' % (result,)

def test_HLA_A1110():
    result = parse('HLA-A1110')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1110"): %s' % (result,)

def test_HLA_A1111():
    result = parse('HLA-A1111')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1111"): %s' % (result,)

def test_HLA_A1112():
    result = parse('HLA-A1112')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1112"): %s' % (result,)

def test_HLA_A1113():
    result = parse('HLA-A1113')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1113"): %s' % (result,)

def test_HLA_A1114():
    result = parse('HLA-A1114')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1114"): %s' % (result,)

def test_HLA_A1115():
    result = parse('HLA-A1115')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1115"): %s' % (result,)

def test_HLA_A1116():
    result = parse('HLA-A1116')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1116"): %s' % (result,)

def test_HLA_A1117():
    result = parse('HLA-A1117')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1117"): %s' % (result,)

def test_HLA_A1118():
    result = parse('HLA-A1118')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1118"): %s' % (result,)

def test_HLA_A1119():
    result = parse('HLA-A1119')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1119"): %s' % (result,)

def test_HLA_A1120():
    result = parse('HLA-A1120')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1120"): %s' % (result,)

def test_HLA_A1121():
    result = parse('HLA-A1121')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1121"): %s' % (result,)

def test_HLA_A1122():
    result = parse('HLA-A1122')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1122"): %s' % (result,)

def test_HLA_A1123():
    result = parse('HLA-A1123')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1123"): %s' % (result,)

def test_HLA_A1124():
    result = parse('HLA-A1124')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1124"): %s' % (result,)

def test_HLA_A1125():
    result = parse('HLA-A1125')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1125"): %s' % (result,)

def test_HLA_A1126():
    result = parse('HLA-A1126')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1126"): %s' % (result,)

def test_HLA_A1127():
    result = parse('HLA-A1127')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1127"): %s' % (result,)

def test_HLA_A1128():
    result = parse('HLA-A1128')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1128"): %s' % (result,)

def test_HLA_A1129():
    result = parse('HLA-A1129')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1129"): %s' % (result,)

def test_HLA_A1130():
    result = parse('HLA-A1130')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1130"): %s' % (result,)

def test_HLA_A1131():
    result = parse('HLA-A1131')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1131"): %s' % (result,)

def test_HLA_A1132():
    result = parse('HLA-A1132')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A1132"): %s' % (result,)

def test_HLA_A2301():
    result = parse('HLA-A2301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2301"): %s' % (result,)

def test_HLA_A2302():
    result = parse('HLA-A2302')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2302"): %s' % (result,)

def test_HLA_A2303():
    result = parse('HLA-A2303')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2303"): %s' % (result,)

def test_HLA_A2304():
    result = parse('HLA-A2304')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2304"): %s' % (result,)

def test_HLA_A2305():
    result = parse('HLA-A2305')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2305"): %s' % (result,)

def test_HLA_A2306():
    result = parse('HLA-A2306')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2306"): %s' % (result,)

def test_HLA_A2307():
    result = parse('HLA-A2307')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2307"): %s' % (result,)

def test_HLA_A2309():
    result = parse('HLA-A2309')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2309"): %s' % (result,)

def test_HLA_A2310():
    result = parse('HLA-A2310')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2310"): %s' % (result,)

def test_HLA_A2312():
    result = parse('HLA-A2312')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2312"): %s' % (result,)

def test_HLA_A2313():
    result = parse('HLA-A2313')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2313"): %s' % (result,)

def test_HLA_A2314():
    result = parse('HLA-A2314')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2314"): %s' % (result,)

def test_HLA_A2315():
    result = parse('HLA-A2315')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2315"): %s' % (result,)

def test_HLA_A2316():
    result = parse('HLA-A2316')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2316"): %s' % (result,)

def test_HLA_A2402():
    result = parse('HLA-A2402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2402"): %s' % (result,)

def test_HLA_A2403():
    result = parse('HLA-A2403')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2403"): %s' % (result,)

def test_HLA_A2404():
    result = parse('HLA-A2404')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2404"): %s' % (result,)

def test_HLA_A2405():
    result = parse('HLA-A2405')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2405"): %s' % (result,)

def test_HLA_A2406():
    result = parse('HLA-A2406')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2406"): %s' % (result,)

def test_HLA_A2407():
    result = parse('HLA-A2407')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2407"): %s' % (result,)

def test_HLA_A2408():
    result = parse('HLA-A2408')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2408"): %s' % (result,)

def test_HLA_A2409():
    result = parse('HLA-A2409')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2409"): %s' % (result,)

def test_HLA_A2410():
    result = parse('HLA-A2410')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2410"): %s' % (result,)

def test_HLA_A2411():
    result = parse('HLA-A2411')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2411"): %s' % (result,)

def test_HLA_A2413():
    result = parse('HLA-A2413')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2413"): %s' % (result,)

def test_HLA_A2414():
    result = parse('HLA-A2414')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2414"): %s' % (result,)

def test_HLA_A2415():
    result = parse('HLA-A2415')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2415"): %s' % (result,)

def test_HLA_A2417():
    result = parse('HLA-A2417')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2417"): %s' % (result,)

def test_HLA_A2418():
    result = parse('HLA-A2418')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2418"): %s' % (result,)

def test_HLA_A2419():
    result = parse('HLA-A2419')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2419"): %s' % (result,)

def test_HLA_A2420():
    result = parse('HLA-A2420')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2420"): %s' % (result,)

def test_HLA_A2421():
    result = parse('HLA-A2421')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2421"): %s' % (result,)

def test_HLA_A2422():
    result = parse('HLA-A2422')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2422"): %s' % (result,)

def test_HLA_A2423():
    result = parse('HLA-A2423')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2423"): %s' % (result,)

def test_HLA_A2424():
    result = parse('HLA-A2424')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2424"): %s' % (result,)

def test_HLA_A2425():
    result = parse('HLA-A2425')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2425"): %s' % (result,)

def test_HLA_A2426():
    result = parse('HLA-A2426')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2426"): %s' % (result,)

def test_HLA_A2427():
    result = parse('HLA-A2427')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2427"): %s' % (result,)

def test_HLA_A2428():
    result = parse('HLA-A2428')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2428"): %s' % (result,)

def test_HLA_A2429():
    result = parse('HLA-A2429')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2429"): %s' % (result,)

def test_HLA_A2430():
    result = parse('HLA-A2430')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2430"): %s' % (result,)

def test_HLA_A2431():
    result = parse('HLA-A2431')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2431"): %s' % (result,)

def test_HLA_A2432():
    result = parse('HLA-A2432')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2432"): %s' % (result,)

def test_HLA_A2433():
    result = parse('HLA-A2433')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2433"): %s' % (result,)

def test_HLA_A2434():
    result = parse('HLA-A2434')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2434"): %s' % (result,)

def test_HLA_A2435():
    result = parse('HLA-A2435')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2435"): %s' % (result,)

def test_HLA_A2437():
    result = parse('HLA-A2437')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2437"): %s' % (result,)

def test_HLA_A2438():
    result = parse('HLA-A2438')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2438"): %s' % (result,)

def test_HLA_A2439():
    result = parse('HLA-A2439')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2439"): %s' % (result,)

def test_HLA_A2440():
    result = parse('HLA-A2440')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2440"): %s' % (result,)

def test_HLA_A2441():
    result = parse('HLA-A2441')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2441"): %s' % (result,)

def test_HLA_A2442():
    result = parse('HLA-A2442')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2442"): %s' % (result,)

def test_HLA_A2443():
    result = parse('HLA-A2443')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2443"): %s' % (result,)

def test_HLA_A2444():
    result = parse('HLA-A2444')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2444"): %s' % (result,)

def test_HLA_A2446():
    result = parse('HLA-A2446')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2446"): %s' % (result,)

def test_HLA_A2447():
    result = parse('HLA-A2447')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2447"): %s' % (result,)

def test_HLA_A2449():
    result = parse('HLA-A2449')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2449"): %s' % (result,)

def test_HLA_A2450():
    result = parse('HLA-A2450')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2450"): %s' % (result,)

def test_HLA_A2451():
    result = parse('HLA-A2451')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2451"): %s' % (result,)

def test_HLA_A2452():
    result = parse('HLA-A2452')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2452"): %s' % (result,)

def test_HLA_A2453():
    result = parse('HLA-A2453')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2453"): %s' % (result,)

def test_HLA_A2454():
    result = parse('HLA-A2454')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2454"): %s' % (result,)

def test_HLA_A2455():
    result = parse('HLA-A2455')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2455"): %s' % (result,)

def test_HLA_A2456():
    result = parse('HLA-A2456')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2456"): %s' % (result,)

def test_HLA_A2457():
    result = parse('HLA-A2457')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2457"): %s' % (result,)

def test_HLA_A2458():
    result = parse('HLA-A2458')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2458"): %s' % (result,)

def test_HLA_A2459():
    result = parse('HLA-A2459')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2459"): %s' % (result,)

def test_HLA_A2461():
    result = parse('HLA-A2461')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2461"): %s' % (result,)

def test_HLA_A2462():
    result = parse('HLA-A2462')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2462"): %s' % (result,)

def test_HLA_A2463():
    result = parse('HLA-A2463')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2463"): %s' % (result,)

def test_HLA_A2464():
    result = parse('HLA-A2464')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2464"): %s' % (result,)

def test_HLA_A2465():
    result = parse('HLA-A2465')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2465"): %s' % (result,)

def test_HLA_A2466():
    result = parse('HLA-A2466')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2466"): %s' % (result,)

def test_HLA_A2467():
    result = parse('HLA-A2467')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2467"): %s' % (result,)

def test_HLA_A2468():
    result = parse('HLA-A2468')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2468"): %s' % (result,)

def test_HLA_A2469():
    result = parse('HLA-A2469')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2469"): %s' % (result,)

def test_HLA_A2470():
    result = parse('HLA-A2470')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2470"): %s' % (result,)

def test_HLA_A2471():
    result = parse('HLA-A2471')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2471"): %s' % (result,)

def test_HLA_A2472():
    result = parse('HLA-A2472')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2472"): %s' % (result,)

def test_HLA_A2473():
    result = parse('HLA-A2473')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2473"): %s' % (result,)

def test_HLA_A2474():
    result = parse('HLA-A2474')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2474"): %s' % (result,)

def test_HLA_A2475():
    result = parse('HLA-A2475')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2475"): %s' % (result,)

def test_HLA_A2476():
    result = parse('HLA-A2476')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2476"): %s' % (result,)

def test_HLA_A2477():
    result = parse('HLA-A2477')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2477"): %s' % (result,)

def test_HLA_A2478():
    result = parse('HLA-A2478')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2478"): %s' % (result,)

def test_HLA_A2479():
    result = parse('HLA-A2479')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2479"): %s' % (result,)

def test_HLA_A2501():
    result = parse('HLA-A2501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2501"): %s' % (result,)

def test_HLA_A2502():
    result = parse('HLA-A2502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2502"): %s' % (result,)

def test_HLA_A2503():
    result = parse('HLA-A2503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2503"): %s' % (result,)

def test_HLA_A2504():
    result = parse('HLA-A2504')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2504"): %s' % (result,)

def test_HLA_A2505():
    result = parse('HLA-A2505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2505"): %s' % (result,)

def test_HLA_A2506():
    result = parse('HLA-A2506')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2506"): %s' % (result,)

def test_HLA_A2601():
    result = parse('HLA-A2601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2601"): %s' % (result,)

def test_HLA_A2602():
    result = parse('HLA-A2602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2602"): %s' % (result,)

def test_HLA_A2603():
    result = parse('HLA-A2603')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2603"): %s' % (result,)

def test_HLA_A2604():
    result = parse('HLA-A2604')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2604"): %s' % (result,)

def test_HLA_A2605():
    result = parse('HLA-A2605')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2605"): %s' % (result,)

def test_HLA_A2606():
    result = parse('HLA-A2606')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2606"): %s' % (result,)

def test_HLA_A2607():
    result = parse('HLA-A2607')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2607"): %s' % (result,)

def test_HLA_A2608():
    result = parse('HLA-A2608')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2608"): %s' % (result,)

def test_HLA_A2609():
    result = parse('HLA-A2609')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2609"): %s' % (result,)

def test_HLA_A2610():
    result = parse('HLA-A2610')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2610"): %s' % (result,)

def test_HLA_A2611():
    result = parse('HLA-A2611')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2611"): %s' % (result,)

def test_HLA_A2612():
    result = parse('HLA-A2612')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2612"): %s' % (result,)

def test_HLA_A2613():
    result = parse('HLA-A2613')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2613"): %s' % (result,)

def test_HLA_A2614():
    result = parse('HLA-A2614')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2614"): %s' % (result,)

def test_HLA_A2615():
    result = parse('HLA-A2615')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2615"): %s' % (result,)

def test_HLA_A2616():
    result = parse('HLA-A2616')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2616"): %s' % (result,)

def test_HLA_A2617():
    result = parse('HLA-A2617')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2617"): %s' % (result,)

def test_HLA_A2618():
    result = parse('HLA-A2618')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2618"): %s' % (result,)

def test_HLA_A2619():
    result = parse('HLA-A2619')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2619"): %s' % (result,)

def test_HLA_A2620():
    result = parse('HLA-A2620')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2620"): %s' % (result,)

def test_HLA_A2621():
    result = parse('HLA-A2621')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2621"): %s' % (result,)

def test_HLA_A2622():
    result = parse('HLA-A2622')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2622"): %s' % (result,)

def test_HLA_A2623():
    result = parse('HLA-A2623')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2623"): %s' % (result,)

def test_HLA_A2624():
    result = parse('HLA-A2624')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2624"): %s' % (result,)

def test_HLA_A2626():
    result = parse('HLA-A2626')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2626"): %s' % (result,)

def test_HLA_A2627():
    result = parse('HLA-A2627')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2627"): %s' % (result,)

def test_HLA_A2628():
    result = parse('HLA-A2628')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2628"): %s' % (result,)

def test_HLA_A2629():
    result = parse('HLA-A2629')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2629"): %s' % (result,)

def test_HLA_A2630():
    result = parse('HLA-A2630')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2630"): %s' % (result,)

def test_HLA_A2631():
    result = parse('HLA-A2631')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2631"): %s' % (result,)

def test_HLA_A2632():
    result = parse('HLA-A2632')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2632"): %s' % (result,)

def test_HLA_A2633():
    result = parse('HLA-A2633')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2633"): %s' % (result,)

def test_HLA_A2634():
    result = parse('HLA-A2634')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2634"): %s' % (result,)

def test_HLA_A2635():
    result = parse('HLA-A2635')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2635"): %s' % (result,)

def test_HLA_A2901():
    result = parse('HLA-A2901')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2901"): %s' % (result,)

def test_HLA_A2902():
    result = parse('HLA-A2902')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2902"): %s' % (result,)

def test_HLA_A2903():
    result = parse('HLA-A2903')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2903"): %s' % (result,)

def test_HLA_A2904():
    result = parse('HLA-A2904')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2904"): %s' % (result,)

def test_HLA_A2905():
    result = parse('HLA-A2905')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2905"): %s' % (result,)

def test_HLA_A2906():
    result = parse('HLA-A2906')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2906"): %s' % (result,)

def test_HLA_A2907():
    result = parse('HLA-A2907')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2907"): %s' % (result,)

def test_HLA_A2909():
    result = parse('HLA-A2909')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2909"): %s' % (result,)

def test_HLA_A2910():
    result = parse('HLA-A2910')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2910"): %s' % (result,)

def test_HLA_A2911():
    result = parse('HLA-A2911')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2911"): %s' % (result,)

def test_HLA_A2912():
    result = parse('HLA-A2912')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2912"): %s' % (result,)

def test_HLA_A2913():
    result = parse('HLA-A2913')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2913"): %s' % (result,)

def test_HLA_A2914():
    result = parse('HLA-A2914')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2914"): %s' % (result,)

def test_HLA_A2915():
    result = parse('HLA-A2915')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2915"): %s' % (result,)

def test_HLA_A2916():
    result = parse('HLA-A2916')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A2916"): %s' % (result,)

def test_HLA_A3001():
    result = parse('HLA-A3001')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3001"): %s' % (result,)

def test_HLA_A3002():
    result = parse('HLA-A3002')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3002"): %s' % (result,)

def test_HLA_A3003():
    result = parse('HLA-A3003')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3003"): %s' % (result,)

def test_HLA_A3004():
    result = parse('HLA-A3004')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3004"): %s' % (result,)

def test_HLA_A3006():
    result = parse('HLA-A3006')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3006"): %s' % (result,)

def test_HLA_A3007():
    result = parse('HLA-A3007')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3007"): %s' % (result,)

def test_HLA_A3008():
    result = parse('HLA-A3008')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3008"): %s' % (result,)

def test_HLA_A3009():
    result = parse('HLA-A3009')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3009"): %s' % (result,)

def test_HLA_A3010():
    result = parse('HLA-A3010')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3010"): %s' % (result,)

def test_HLA_A3011():
    result = parse('HLA-A3011')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3011"): %s' % (result,)

def test_HLA_A3012():
    result = parse('HLA-A3012')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3012"): %s' % (result,)

def test_HLA_A3013():
    result = parse('HLA-A3013')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3013"): %s' % (result,)

def test_HLA_A3014():
    result = parse('HLA-A3014')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3014"): %s' % (result,)

def test_HLA_A3015():
    result = parse('HLA-A3015')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3015"): %s' % (result,)

def test_HLA_A3016():
    result = parse('HLA-A3016')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3016"): %s' % (result,)

def test_HLA_A3017():
    result = parse('HLA-A3017')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3017"): %s' % (result,)

def test_HLA_A3018():
    result = parse('HLA-A3018')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3018"): %s' % (result,)

def test_HLA_A3019():
    result = parse('HLA-A3019')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3019"): %s' % (result,)

def test_HLA_A3020():
    result = parse('HLA-A3020')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3020"): %s' % (result,)

def test_HLA_A3021():
    result = parse('HLA-A3021')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3021"): %s' % (result,)

def test_HLA_A3022():
    result = parse('HLA-A3022')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3022"): %s' % (result,)

def test_HLA_A3101():
    result = parse('HLA-A3101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3101"): %s' % (result,)

def test_HLA_A3102():
    result = parse('HLA-A3102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3102"): %s' % (result,)

def test_HLA_A3103():
    result = parse('HLA-A3103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3103"): %s' % (result,)

def test_HLA_A3104():
    result = parse('HLA-A3104')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3104"): %s' % (result,)

def test_HLA_A3105():
    result = parse('HLA-A3105')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3105"): %s' % (result,)

def test_HLA_A3106():
    result = parse('HLA-A3106')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3106"): %s' % (result,)

def test_HLA_A3107():
    result = parse('HLA-A3107')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3107"): %s' % (result,)

def test_HLA_A3108():
    result = parse('HLA-A3108')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3108"): %s' % (result,)

def test_HLA_A3109():
    result = parse('HLA-A3109')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3109"): %s' % (result,)

def test_HLA_A3110():
    result = parse('HLA-A3110')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3110"): %s' % (result,)

def test_HLA_A3111():
    result = parse('HLA-A3111')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3111"): %s' % (result,)

def test_HLA_A3112():
    result = parse('HLA-A3112')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3112"): %s' % (result,)

def test_HLA_A3113():
    result = parse('HLA-A3113')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3113"): %s' % (result,)

def test_HLA_A3114():
    result = parse('HLA-A3114')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3114"): %s' % (result,)

def test_HLA_A3115():
    result = parse('HLA-A3115')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3115"): %s' % (result,)

def test_HLA_A3116():
    result = parse('HLA-A3116')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3116"): %s' % (result,)

def test_HLA_A3117():
    result = parse('HLA-A3117')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3117"): %s' % (result,)

def test_HLA_A3118():
    result = parse('HLA-A3118')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3118"): %s' % (result,)

def test_HLA_A3201():
    result = parse('HLA-A3201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3201"): %s' % (result,)

def test_HLA_A3202():
    result = parse('HLA-A3202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3202"): %s' % (result,)

def test_HLA_A3203():
    result = parse('HLA-A3203')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3203"): %s' % (result,)

def test_HLA_A3204():
    result = parse('HLA-A3204')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3204"): %s' % (result,)

def test_HLA_A3205():
    result = parse('HLA-A3205')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3205"): %s' % (result,)

def test_HLA_A3206():
    result = parse('HLA-A3206')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3206"): %s' % (result,)

def test_HLA_A3207():
    result = parse('HLA-A3207')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3207"): %s' % (result,)

def test_HLA_A3208():
    result = parse('HLA-A3208')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3208"): %s' % (result,)

def test_HLA_A3209():
    result = parse('HLA-A3209')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3209"): %s' % (result,)

def test_HLA_A3210():
    result = parse('HLA-A3210')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3210"): %s' % (result,)

def test_HLA_A3211():
    result = parse('HLA-A3211')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3211"): %s' % (result,)

def test_HLA_A3212():
    result = parse('HLA-A3212')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3212"): %s' % (result,)

def test_HLA_A3213():
    result = parse('HLA-A3213')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3213"): %s' % (result,)

def test_HLA_A3214():
    result = parse('HLA-A3214')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3214"): %s' % (result,)

def test_HLA_A3215():
    result = parse('HLA-A3215')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3215"): %s' % (result,)

def test_HLA_A3301():
    result = parse('HLA-A3301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3301"): %s' % (result,)

def test_HLA_A3303():
    result = parse('HLA-A3303')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3303"): %s' % (result,)

def test_HLA_A3304():
    result = parse('HLA-A3304')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3304"): %s' % (result,)

def test_HLA_A3305():
    result = parse('HLA-A3305')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3305"): %s' % (result,)

def test_HLA_A3306():
    result = parse('HLA-A3306')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3306"): %s' % (result,)

def test_HLA_A3307():
    result = parse('HLA-A3307')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3307"): %s' % (result,)

def test_HLA_A3308():
    result = parse('HLA-A3308')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3308"): %s' % (result,)

def test_HLA_A3309():
    result = parse('HLA-A3309')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3309"): %s' % (result,)

def test_HLA_A3310():
    result = parse('HLA-A3310')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3310"): %s' % (result,)

def test_HLA_A3311():
    result = parse('HLA-A3311')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3311"): %s' % (result,)

def test_HLA_A3312():
    result = parse('HLA-A3312')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3312"): %s' % (result,)

def test_HLA_A3313():
    result = parse('HLA-A3313')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3313"): %s' % (result,)

def test_HLA_A3401():
    result = parse('HLA-A3401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3401"): %s' % (result,)

def test_HLA_A3402():
    result = parse('HLA-A3402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3402"): %s' % (result,)

def test_HLA_A3403():
    result = parse('HLA-A3403')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3403"): %s' % (result,)

def test_HLA_A3404():
    result = parse('HLA-A3404')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3404"): %s' % (result,)

def test_HLA_A3405():
    result = parse('HLA-A3405')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3405"): %s' % (result,)

def test_HLA_A3406():
    result = parse('HLA-A3406')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3406"): %s' % (result,)

def test_HLA_A3407():
    result = parse('HLA-A3407')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3407"): %s' % (result,)

def test_HLA_A3408():
    result = parse('HLA-A3408')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3408"): %s' % (result,)

def test_HLA_A3601():
    result = parse('HLA-A3601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3601"): %s' % (result,)

def test_HLA_A3602():
    result = parse('HLA-A3602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3602"): %s' % (result,)

def test_HLA_A3603():
    result = parse('HLA-A3603')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3603"): %s' % (result,)

def test_HLA_A3604():
    result = parse('HLA-A3604')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A3604"): %s' % (result,)

def test_HLA_A4301():
    result = parse('HLA-A4301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A4301"): %s' % (result,)

def test_HLA_A6601():
    result = parse('HLA-A6601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6601"): %s' % (result,)

def test_HLA_A6602():
    result = parse('HLA-A6602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6602"): %s' % (result,)

def test_HLA_A6603():
    result = parse('HLA-A6603')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6603"): %s' % (result,)

def test_HLA_A6604():
    result = parse('HLA-A6604')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6604"): %s' % (result,)

def test_HLA_A6605():
    result = parse('HLA-A6605')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6605"): %s' % (result,)

def test_HLA_A6606():
    result = parse('HLA-A6606')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6606"): %s' % (result,)

def test_HLA_A6801():
    result = parse('HLA-A6801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6801"): %s' % (result,)

def test_HLA_A6802():
    result = parse('HLA-A6802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6802"): %s' % (result,)

def test_HLA_A6803():
    result = parse('HLA-A6803')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6803"): %s' % (result,)

def test_HLA_A6804():
    result = parse('HLA-A6804')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6804"): %s' % (result,)

def test_HLA_A6805():
    result = parse('HLA-A6805')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6805"): %s' % (result,)

def test_HLA_A6806():
    result = parse('HLA-A6806')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6806"): %s' % (result,)

def test_HLA_A6807():
    result = parse('HLA-A6807')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6807"): %s' % (result,)

def test_HLA_A6808():
    result = parse('HLA-A6808')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6808"): %s' % (result,)

def test_HLA_A6809():
    result = parse('HLA-A6809')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6809"): %s' % (result,)

def test_HLA_A6810():
    result = parse('HLA-A6810')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6810"): %s' % (result,)

def test_HLA_A6812():
    result = parse('HLA-A6812')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6812"): %s' % (result,)

def test_HLA_A6813():
    result = parse('HLA-A6813')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6813"): %s' % (result,)

def test_HLA_A6814():
    result = parse('HLA-A6814')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6814"): %s' % (result,)

def test_HLA_A6815():
    result = parse('HLA-A6815')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6815"): %s' % (result,)

def test_HLA_A6816():
    result = parse('HLA-A6816')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6816"): %s' % (result,)

def test_HLA_A6817():
    result = parse('HLA-A6817')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6817"): %s' % (result,)

def test_HLA_A6819():
    result = parse('HLA-A6819')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6819"): %s' % (result,)

def test_HLA_A6820():
    result = parse('HLA-A6820')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6820"): %s' % (result,)

def test_HLA_A6821():
    result = parse('HLA-A6821')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6821"): %s' % (result,)

def test_HLA_A6822():
    result = parse('HLA-A6822')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6822"): %s' % (result,)

def test_HLA_A6823():
    result = parse('HLA-A6823')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6823"): %s' % (result,)

def test_HLA_A6824():
    result = parse('HLA-A6824')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6824"): %s' % (result,)

def test_HLA_A6825():
    result = parse('HLA-A6825')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6825"): %s' % (result,)

def test_HLA_A6826():
    result = parse('HLA-A6826')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6826"): %s' % (result,)

def test_HLA_A6827():
    result = parse('HLA-A6827')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6827"): %s' % (result,)

def test_HLA_A6828():
    result = parse('HLA-A6828')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6828"): %s' % (result,)

def test_HLA_A6829():
    result = parse('HLA-A6829')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6829"): %s' % (result,)

def test_HLA_A6830():
    result = parse('HLA-A6830')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6830"): %s' % (result,)

def test_HLA_A6831():
    result = parse('HLA-A6831')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6831"): %s' % (result,)

def test_HLA_A6832():
    result = parse('HLA-A6832')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6832"): %s' % (result,)

def test_HLA_A6833():
    result = parse('HLA-A6833')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6833"): %s' % (result,)

def test_HLA_A6834():
    result = parse('HLA-A6834')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6834"): %s' % (result,)

def test_HLA_A6835():
    result = parse('HLA-A6835')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6835"): %s' % (result,)

def test_HLA_A6836():
    result = parse('HLA-A6836')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6836"): %s' % (result,)

def test_HLA_A6837():
    result = parse('HLA-A6837')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6837"): %s' % (result,)

def test_HLA_A6838():
    result = parse('HLA-A6838')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6838"): %s' % (result,)

def test_HLA_A6839():
    result = parse('HLA-A6839')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6839"): %s' % (result,)

def test_HLA_A6840():
    result = parse('HLA-A6840')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6840"): %s' % (result,)

def test_HLA_A6901():
    result = parse('HLA-A6901')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A6901"): %s' % (result,)

def test_HLA_A7401():
    result = parse('HLA-A7401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7401"): %s' % (result,)

def test_HLA_A7402():
    result = parse('HLA-A7402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7402"): %s' % (result,)

def test_HLA_A7403():
    result = parse('HLA-A7403')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7403"): %s' % (result,)

def test_HLA_A7404():
    result = parse('HLA-A7404')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7404"): %s' % (result,)

def test_HLA_A7405():
    result = parse('HLA-A7405')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7405"): %s' % (result,)

def test_HLA_A7406():
    result = parse('HLA-A7406')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7406"): %s' % (result,)

def test_HLA_A7407():
    result = parse('HLA-A7407')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7407"): %s' % (result,)

def test_HLA_A7408():
    result = parse('HLA-A7408')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7408"): %s' % (result,)

def test_HLA_A7409():
    result = parse('HLA-A7409')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7409"): %s' % (result,)

def test_HLA_A7410():
    result = parse('HLA-A7410')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7410"): %s' % (result,)

def test_HLA_A7411():
    result = parse('HLA-A7411')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A7411"): %s' % (result,)

def test_HLA_A8001():
    result = parse('HLA-A8001')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A8001"): %s' % (result,)

def test_HLA_A9201():
    result = parse('HLA-A9201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9201"): %s' % (result,)

def test_HLA_A9202():
    result = parse('HLA-A9202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9202"): %s' % (result,)

def test_HLA_A9203():
    result = parse('HLA-A9203')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9203"): %s' % (result,)

def test_HLA_A9204():
    result = parse('HLA-A9204')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9204"): %s' % (result,)

def test_HLA_A9205():
    result = parse('HLA-A9205')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9205"): %s' % (result,)

def test_HLA_A9206():
    result = parse('HLA-A9206')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9206"): %s' % (result,)

def test_HLA_A9207():
    result = parse('HLA-A9207')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9207"): %s' % (result,)

def test_HLA_A9208():
    result = parse('HLA-A9208')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9208"): %s' % (result,)

def test_HLA_A9209():
    result = parse('HLA-A9209')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9209"): %s' % (result,)

def test_HLA_A9210():
    result = parse('HLA-A9210')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9210"): %s' % (result,)

def test_HLA_A9211():
    result = parse('HLA-A9211')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9211"): %s' % (result,)

def test_HLA_A9212():
    result = parse('HLA-A9212')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9212"): %s' % (result,)

def test_HLA_A9214():
    result = parse('HLA-A9214')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9214"): %s' % (result,)

def test_HLA_A9215():
    result = parse('HLA-A9215')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9215"): %s' % (result,)

def test_HLA_A9216():
    result = parse('HLA-A9216')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9216"): %s' % (result,)

def test_HLA_A9217():
    result = parse('HLA-A9217')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9217"): %s' % (result,)

def test_HLA_A9218():
    result = parse('HLA-A9218')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9218"): %s' % (result,)

def test_HLA_A9219():
    result = parse('HLA-A9219')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9219"): %s' % (result,)

def test_HLA_A9220():
    result = parse('HLA-A9220')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9220"): %s' % (result,)

def test_HLA_A9221():
    result = parse('HLA-A9221')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9221"): %s' % (result,)

def test_HLA_A9222():
    result = parse('HLA-A9222')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9222"): %s' % (result,)

def test_HLA_A9223():
    result = parse('HLA-A9223')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9223"): %s' % (result,)

def test_HLA_A9224():
    result = parse('HLA-A9224')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9224"): %s' % (result,)

def test_HLA_A9226():
    result = parse('HLA-A9226')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-A9226"): %s' % (result,)

def test_HLA_B0702():
    result = parse('HLA-B0702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0702"): %s' % (result,)

def test_HLA_B0703():
    result = parse('HLA-B0703')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0703"): %s' % (result,)

def test_HLA_B0704():
    result = parse('HLA-B0704')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0704"): %s' % (result,)

def test_HLA_B0705():
    result = parse('HLA-B0705')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0705"): %s' % (result,)

def test_HLA_B0706():
    result = parse('HLA-B0706')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0706"): %s' % (result,)

def test_HLA_B0707():
    result = parse('HLA-B0707')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0707"): %s' % (result,)

def test_HLA_B0708():
    result = parse('HLA-B0708')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0708"): %s' % (result,)

def test_HLA_B0709():
    result = parse('HLA-B0709')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0709"): %s' % (result,)

def test_HLA_B0710():
    result = parse('HLA-B0710')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0710"): %s' % (result,)

def test_HLA_B0711():
    result = parse('HLA-B0711')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0711"): %s' % (result,)

def test_HLA_B0712():
    result = parse('HLA-B0712')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0712"): %s' % (result,)

def test_HLA_B0713():
    result = parse('HLA-B0713')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0713"): %s' % (result,)

def test_HLA_B0714():
    result = parse('HLA-B0714')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0714"): %s' % (result,)

def test_HLA_B0715():
    result = parse('HLA-B0715')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0715"): %s' % (result,)

def test_HLA_B0716():
    result = parse('HLA-B0716')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0716"): %s' % (result,)

def test_HLA_B0717():
    result = parse('HLA-B0717')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0717"): %s' % (result,)

def test_HLA_B0718():
    result = parse('HLA-B0718')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0718"): %s' % (result,)

def test_HLA_B0719():
    result = parse('HLA-B0719')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0719"): %s' % (result,)

def test_HLA_B0720():
    result = parse('HLA-B0720')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0720"): %s' % (result,)

def test_HLA_B0721():
    result = parse('HLA-B0721')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0721"): %s' % (result,)

def test_HLA_B0722():
    result = parse('HLA-B0722')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0722"): %s' % (result,)

def test_HLA_B0723():
    result = parse('HLA-B0723')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0723"): %s' % (result,)

def test_HLA_B0724():
    result = parse('HLA-B0724')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0724"): %s' % (result,)

def test_HLA_B0725():
    result = parse('HLA-B0725')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0725"): %s' % (result,)

def test_HLA_B0726():
    result = parse('HLA-B0726')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0726"): %s' % (result,)

def test_HLA_B0727():
    result = parse('HLA-B0727')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0727"): %s' % (result,)

def test_HLA_B0728():
    result = parse('HLA-B0728')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0728"): %s' % (result,)

def test_HLA_B0729():
    result = parse('HLA-B0729')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0729"): %s' % (result,)

def test_HLA_B0730():
    result = parse('HLA-B0730')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0730"): %s' % (result,)

def test_HLA_B0731():
    result = parse('HLA-B0731')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0731"): %s' % (result,)

def test_HLA_B0732():
    result = parse('HLA-B0732')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0732"): %s' % (result,)

def test_HLA_B0733():
    result = parse('HLA-B0733')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0733"): %s' % (result,)

def test_HLA_B0734():
    result = parse('HLA-B0734')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0734"): %s' % (result,)

def test_HLA_B0735():
    result = parse('HLA-B0735')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0735"): %s' % (result,)

def test_HLA_B0736():
    result = parse('HLA-B0736')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0736"): %s' % (result,)

def test_HLA_B0737():
    result = parse('HLA-B0737')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0737"): %s' % (result,)

def test_HLA_B0738():
    result = parse('HLA-B0738')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0738"): %s' % (result,)

def test_HLA_B0739():
    result = parse('HLA-B0739')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0739"): %s' % (result,)

def test_HLA_B0740():
    result = parse('HLA-B0740')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0740"): %s' % (result,)

def test_HLA_B0741():
    result = parse('HLA-B0741')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0741"): %s' % (result,)

def test_HLA_B0742():
    result = parse('HLA-B0742')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0742"): %s' % (result,)

def test_HLA_B0743():
    result = parse('HLA-B0743')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0743"): %s' % (result,)

def test_HLA_B0744():
    result = parse('HLA-B0744')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0744"): %s' % (result,)

def test_HLA_B0745():
    result = parse('HLA-B0745')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0745"): %s' % (result,)

def test_HLA_B0746():
    result = parse('HLA-B0746')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0746"): %s' % (result,)

def test_HLA_B0747():
    result = parse('HLA-B0747')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0747"): %s' % (result,)

def test_HLA_B0748():
    result = parse('HLA-B0748')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0748"): %s' % (result,)

def test_HLA_B0749():
    result = parse('HLA-B0749')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0749"): %s' % (result,)

def test_HLA_B0750():
    result = parse('HLA-B0750')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0750"): %s' % (result,)

def test_HLA_B0751():
    result = parse('HLA-B0751')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0751"): %s' % (result,)

def test_HLA_B0752():
    result = parse('HLA-B0752')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0752"): %s' % (result,)

def test_HLA_B0753():
    result = parse('HLA-B0753')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0753"): %s' % (result,)

def test_HLA_B0754():
    result = parse('HLA-B0754')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0754"): %s' % (result,)

def test_HLA_B0755():
    result = parse('HLA-B0755')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0755"): %s' % (result,)

def test_HLA_B0756():
    result = parse('HLA-B0756')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0756"): %s' % (result,)

def test_HLA_B0757():
    result = parse('HLA-B0757')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0757"): %s' % (result,)

def test_HLA_B0758():
    result = parse('HLA-B0758')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0758"): %s' % (result,)

def test_HLA_B0801():
    result = parse('HLA-B0801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0801"): %s' % (result,)

def test_HLA_B0802():
    result = parse('HLA-B0802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0802"): %s' % (result,)

def test_HLA_B0803():
    result = parse('HLA-B0803')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0803"): %s' % (result,)

def test_HLA_B0804():
    result = parse('HLA-B0804')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0804"): %s' % (result,)

def test_HLA_B0805():
    result = parse('HLA-B0805')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0805"): %s' % (result,)

def test_HLA_B0806():
    result = parse('HLA-B0806')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0806"): %s' % (result,)

def test_HLA_B0807():
    result = parse('HLA-B0807')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0807"): %s' % (result,)

def test_HLA_B0808():
    result = parse('HLA-B0808')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0808"): %s' % (result,)

def test_HLA_B0809():
    result = parse('HLA-B0809')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0809"): %s' % (result,)

def test_HLA_B0810():
    result = parse('HLA-B0810')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0810"): %s' % (result,)

def test_HLA_B0811():
    result = parse('HLA-B0811')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0811"): %s' % (result,)

def test_HLA_B0812():
    result = parse('HLA-B0812')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0812"): %s' % (result,)

def test_HLA_B0813():
    result = parse('HLA-B0813')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0813"): %s' % (result,)

def test_HLA_B0814():
    result = parse('HLA-B0814')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0814"): %s' % (result,)

def test_HLA_B0815():
    result = parse('HLA-B0815')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0815"): %s' % (result,)

def test_HLA_B0816():
    result = parse('HLA-B0816')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0816"): %s' % (result,)

def test_HLA_B0817():
    result = parse('HLA-B0817')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0817"): %s' % (result,)

def test_HLA_B0818():
    result = parse('HLA-B0818')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0818"): %s' % (result,)

def test_HLA_B0819():
    result = parse('HLA-B0819')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0819"): %s' % (result,)

def test_HLA_B0820():
    result = parse('HLA-B0820')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0820"): %s' % (result,)

def test_HLA_B0821():
    result = parse('HLA-B0821')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0821"): %s' % (result,)

def test_HLA_B0822():
    result = parse('HLA-B0822')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0822"): %s' % (result,)

def test_HLA_B0823():
    result = parse('HLA-B0823')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0823"): %s' % (result,)

def test_HLA_B0824():
    result = parse('HLA-B0824')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0824"): %s' % (result,)

def test_HLA_B0825():
    result = parse('HLA-B0825')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0825"): %s' % (result,)

def test_HLA_B0826():
    result = parse('HLA-B0826')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0826"): %s' % (result,)

def test_HLA_B0827():
    result = parse('HLA-B0827')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0827"): %s' % (result,)

def test_HLA_B0828():
    result = parse('HLA-B0828')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0828"): %s' % (result,)

def test_HLA_B0829():
    result = parse('HLA-B0829')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0829"): %s' % (result,)

def test_HLA_B0831():
    result = parse('HLA-B0831')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0831"): %s' % (result,)

def test_HLA_B0832():
    result = parse('HLA-B0832')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0832"): %s' % (result,)

def test_HLA_B0833():
    result = parse('HLA-B0833')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B0833"): %s' % (result,)

def test_HLA_B1301():
    result = parse('HLA-B1301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1301"): %s' % (result,)

def test_HLA_B1302():
    result = parse('HLA-B1302')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1302"): %s' % (result,)

def test_HLA_B1303():
    result = parse('HLA-B1303')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1303"): %s' % (result,)

def test_HLA_B1304():
    result = parse('HLA-B1304')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1304"): %s' % (result,)

def test_HLA_B1306():
    result = parse('HLA-B1306')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1306"): %s' % (result,)

def test_HLA_B1308():
    result = parse('HLA-B1308')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1308"): %s' % (result,)

def test_HLA_B1309():
    result = parse('HLA-B1309')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1309"): %s' % (result,)

def test_HLA_B1310():
    result = parse('HLA-B1310')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1310"): %s' % (result,)

def test_HLA_B1311():
    result = parse('HLA-B1311')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1311"): %s' % (result,)

def test_HLA_B1312():
    result = parse('HLA-B1312')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1312"): %s' % (result,)

def test_HLA_B1313():
    result = parse('HLA-B1313')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1313"): %s' % (result,)

def test_HLA_B1314():
    result = parse('HLA-B1314')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1314"): %s' % (result,)

def test_HLA_B1315():
    result = parse('HLA-B1315')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1315"): %s' % (result,)

def test_HLA_B1316():
    result = parse('HLA-B1316')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1316"): %s' % (result,)

def test_HLA_B1317():
    result = parse('HLA-B1317')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1317"): %s' % (result,)

def test_HLA_B1318():
    result = parse('HLA-B1318')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1318"): %s' % (result,)

def test_HLA_B1319():
    result = parse('HLA-B1319')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1319"): %s' % (result,)

def test_HLA_B1320():
    result = parse('HLA-B1320')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1320"): %s' % (result,)

def test_HLA_B1401():
    result = parse('HLA-B1401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1401"): %s' % (result,)

def test_HLA_B1402():
    result = parse('HLA-B1402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1402"): %s' % (result,)

def test_HLA_B1403():
    result = parse('HLA-B1403')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1403"): %s' % (result,)

def test_HLA_B1404():
    result = parse('HLA-B1404')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1404"): %s' % (result,)

def test_HLA_B1405():
    result = parse('HLA-B1405')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1405"): %s' % (result,)

def test_HLA_B1406():
    result = parse('HLA-B1406')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1406"): %s' % (result,)

def test_HLA_B1501():
    result = parse('HLA-B1501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1501"): %s' % (result,)

def test_HLA_B1502():
    result = parse('HLA-B1502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1502"): %s' % (result,)

def test_HLA_B1503():
    result = parse('HLA-B1503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1503"): %s' % (result,)

def test_HLA_B1504():
    result = parse('HLA-B1504')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1504"): %s' % (result,)

def test_HLA_B1505():
    result = parse('HLA-B1505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1505"): %s' % (result,)

def test_HLA_B1506():
    result = parse('HLA-B1506')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1506"): %s' % (result,)

def test_HLA_B1507():
    result = parse('HLA-B1507')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1507"): %s' % (result,)

def test_HLA_B1508():
    result = parse('HLA-B1508')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1508"): %s' % (result,)

def test_HLA_B1509():
    result = parse('HLA-B1509')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1509"): %s' % (result,)

def test_HLA_B1510():
    result = parse('HLA-B1510')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1510"): %s' % (result,)

def test_HLA_B1511():
    result = parse('HLA-B1511')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1511"): %s' % (result,)

def test_HLA_B1512():
    result = parse('HLA-B1512')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1512"): %s' % (result,)

def test_HLA_B1513():
    result = parse('HLA-B1513')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1513"): %s' % (result,)

def test_HLA_B1514():
    result = parse('HLA-B1514')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1514"): %s' % (result,)

def test_HLA_B1515():
    result = parse('HLA-B1515')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1515"): %s' % (result,)

def test_HLA_B1516():
    result = parse('HLA-B1516')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1516"): %s' % (result,)

def test_HLA_B1517():
    result = parse('HLA-B1517')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1517"): %s' % (result,)

def test_HLA_B1518():
    result = parse('HLA-B1518')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1518"): %s' % (result,)

def test_HLA_B1519():
    result = parse('HLA-B1519')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1519"): %s' % (result,)

def test_HLA_B1520():
    result = parse('HLA-B1520')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1520"): %s' % (result,)

def test_HLA_B1521():
    result = parse('HLA-B1521')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1521"): %s' % (result,)

def test_HLA_B1523():
    result = parse('HLA-B1523')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1523"): %s' % (result,)

def test_HLA_B1524():
    result = parse('HLA-B1524')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1524"): %s' % (result,)

def test_HLA_B1525():
    result = parse('HLA-B1525')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1525"): %s' % (result,)

def test_HLA_B1527():
    result = parse('HLA-B1527')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1527"): %s' % (result,)

def test_HLA_B1528():
    result = parse('HLA-B1528')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1528"): %s' % (result,)

def test_HLA_B1529():
    result = parse('HLA-B1529')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1529"): %s' % (result,)

def test_HLA_B1530():
    result = parse('HLA-B1530')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1530"): %s' % (result,)

def test_HLA_B1531():
    result = parse('HLA-B1531')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1531"): %s' % (result,)

def test_HLA_B1532():
    result = parse('HLA-B1532')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1532"): %s' % (result,)

def test_HLA_B1533():
    result = parse('HLA-B1533')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1533"): %s' % (result,)

def test_HLA_B1534():
    result = parse('HLA-B1534')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1534"): %s' % (result,)

def test_HLA_B1535():
    result = parse('HLA-B1535')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1535"): %s' % (result,)

def test_HLA_B1536():
    result = parse('HLA-B1536')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1536"): %s' % (result,)

def test_HLA_B1537():
    result = parse('HLA-B1537')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1537"): %s' % (result,)

def test_HLA_B1538():
    result = parse('HLA-B1538')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1538"): %s' % (result,)

def test_HLA_B1539():
    result = parse('HLA-B1539')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1539"): %s' % (result,)

def test_HLA_B1540():
    result = parse('HLA-B1540')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1540"): %s' % (result,)

def test_HLA_B1542():
    result = parse('HLA-B1542')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1542"): %s' % (result,)

def test_HLA_B1543():
    result = parse('HLA-B1543')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1543"): %s' % (result,)

def test_HLA_B1544():
    result = parse('HLA-B1544')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1544"): %s' % (result,)

def test_HLA_B1545():
    result = parse('HLA-B1545')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1545"): %s' % (result,)

def test_HLA_B1546():
    result = parse('HLA-B1546')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1546"): %s' % (result,)

def test_HLA_B1547():
    result = parse('HLA-B1547')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1547"): %s' % (result,)

def test_HLA_B1548():
    result = parse('HLA-B1548')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1548"): %s' % (result,)

def test_HLA_B1549():
    result = parse('HLA-B1549')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1549"): %s' % (result,)

def test_HLA_B1550():
    result = parse('HLA-B1550')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1550"): %s' % (result,)

def test_HLA_B1551():
    result = parse('HLA-B1551')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1551"): %s' % (result,)

def test_HLA_B1552():
    result = parse('HLA-B1552')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1552"): %s' % (result,)

def test_HLA_B1553():
    result = parse('HLA-B1553')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1553"): %s' % (result,)

def test_HLA_B1554():
    result = parse('HLA-B1554')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1554"): %s' % (result,)

def test_HLA_B1555():
    result = parse('HLA-B1555')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1555"): %s' % (result,)

def test_HLA_B1556():
    result = parse('HLA-B1556')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1556"): %s' % (result,)

def test_HLA_B1557():
    result = parse('HLA-B1557')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1557"): %s' % (result,)

def test_HLA_B1558():
    result = parse('HLA-B1558')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1558"): %s' % (result,)

def test_HLA_B1560():
    result = parse('HLA-B1560')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1560"): %s' % (result,)

def test_HLA_B1561():
    result = parse('HLA-B1561')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1561"): %s' % (result,)

def test_HLA_B1562():
    result = parse('HLA-B1562')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1562"): %s' % (result,)

def test_HLA_B1563():
    result = parse('HLA-B1563')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1563"): %s' % (result,)

def test_HLA_B1564():
    result = parse('HLA-B1564')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1564"): %s' % (result,)

def test_HLA_B1565():
    result = parse('HLA-B1565')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1565"): %s' % (result,)

def test_HLA_B1566():
    result = parse('HLA-B1566')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1566"): %s' % (result,)

def test_HLA_B1567():
    result = parse('HLA-B1567')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1567"): %s' % (result,)

def test_HLA_B1568():
    result = parse('HLA-B1568')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1568"): %s' % (result,)

def test_HLA_B1569():
    result = parse('HLA-B1569')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1569"): %s' % (result,)

def test_HLA_B1570():
    result = parse('HLA-B1570')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1570"): %s' % (result,)

def test_HLA_B1571():
    result = parse('HLA-B1571')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1571"): %s' % (result,)

def test_HLA_B1572():
    result = parse('HLA-B1572')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1572"): %s' % (result,)

def test_HLA_B1573():
    result = parse('HLA-B1573')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1573"): %s' % (result,)

def test_HLA_B1574():
    result = parse('HLA-B1574')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1574"): %s' % (result,)

def test_HLA_B1575():
    result = parse('HLA-B1575')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1575"): %s' % (result,)

def test_HLA_B1576():
    result = parse('HLA-B1576')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1576"): %s' % (result,)

def test_HLA_B1577():
    result = parse('HLA-B1577')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1577"): %s' % (result,)

def test_HLA_B1578():
    result = parse('HLA-B1578')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1578"): %s' % (result,)

def test_HLA_B1580():
    result = parse('HLA-B1580')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1580"): %s' % (result,)

def test_HLA_B1581():
    result = parse('HLA-B1581')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1581"): %s' % (result,)

def test_HLA_B1582():
    result = parse('HLA-B1582')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1582"): %s' % (result,)

def test_HLA_B1583():
    result = parse('HLA-B1583')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1583"): %s' % (result,)

def test_HLA_B1584():
    result = parse('HLA-B1584')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1584"): %s' % (result,)

def test_HLA_B1585():
    result = parse('HLA-B1585')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1585"): %s' % (result,)

def test_HLA_B1586():
    result = parse('HLA-B1586')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1586"): %s' % (result,)

def test_HLA_B1587():
    result = parse('HLA-B1587')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1587"): %s' % (result,)

def test_HLA_B1588():
    result = parse('HLA-B1588')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1588"): %s' % (result,)

def test_HLA_B1589():
    result = parse('HLA-B1589')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1589"): %s' % (result,)

def test_HLA_B1590():
    result = parse('HLA-B1590')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1590"): %s' % (result,)

def test_HLA_B1591():
    result = parse('HLA-B1591')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1591"): %s' % (result,)

def test_HLA_B1592():
    result = parse('HLA-B1592')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1592"): %s' % (result,)

def test_HLA_B1593():
    result = parse('HLA-B1593')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1593"): %s' % (result,)

def test_HLA_B1595():
    result = parse('HLA-B1595')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1595"): %s' % (result,)

def test_HLA_B1596():
    result = parse('HLA-B1596')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1596"): %s' % (result,)

def test_HLA_B1597():
    result = parse('HLA-B1597')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1597"): %s' % (result,)

def test_HLA_B1598():
    result = parse('HLA-B1598')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1598"): %s' % (result,)

def test_HLA_B1599():
    result = parse('HLA-B1599')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1599"): %s' % (result,)

def test_HLA_B1801():
    result = parse('HLA-B1801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1801"): %s' % (result,)

def test_HLA_B1802():
    result = parse('HLA-B1802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1802"): %s' % (result,)

def test_HLA_B1803():
    result = parse('HLA-B1803')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1803"): %s' % (result,)

def test_HLA_B1804():
    result = parse('HLA-B1804')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1804"): %s' % (result,)

def test_HLA_B1805():
    result = parse('HLA-B1805')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1805"): %s' % (result,)

def test_HLA_B1806():
    result = parse('HLA-B1806')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1806"): %s' % (result,)

def test_HLA_B1807():
    result = parse('HLA-B1807')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1807"): %s' % (result,)

def test_HLA_B1808():
    result = parse('HLA-B1808')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1808"): %s' % (result,)

def test_HLA_B1809():
    result = parse('HLA-B1809')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1809"): %s' % (result,)

def test_HLA_B1810():
    result = parse('HLA-B1810')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1810"): %s' % (result,)

def test_HLA_B1811():
    result = parse('HLA-B1811')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1811"): %s' % (result,)

def test_HLA_B1812():
    result = parse('HLA-B1812')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1812"): %s' % (result,)

def test_HLA_B1813():
    result = parse('HLA-B1813')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1813"): %s' % (result,)

def test_HLA_B1814():
    result = parse('HLA-B1814')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1814"): %s' % (result,)

def test_HLA_B1815():
    result = parse('HLA-B1815')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1815"): %s' % (result,)

def test_HLA_B1818():
    result = parse('HLA-B1818')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1818"): %s' % (result,)

def test_HLA_B1819():
    result = parse('HLA-B1819')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1819"): %s' % (result,)

def test_HLA_B1820():
    result = parse('HLA-B1820')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1820"): %s' % (result,)

def test_HLA_B1821():
    result = parse('HLA-B1821')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1821"): %s' % (result,)

def test_HLA_B1822():
    result = parse('HLA-B1822')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1822"): %s' % (result,)

def test_HLA_B1823():
    result = parse('HLA-B1823')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1823"): %s' % (result,)

def test_HLA_B1824():
    result = parse('HLA-B1824')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1824"): %s' % (result,)

def test_HLA_B1825():
    result = parse('HLA-B1825')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1825"): %s' % (result,)

def test_HLA_B1826():
    result = parse('HLA-B1826')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B1826"): %s' % (result,)

def test_HLA_B2701():
    result = parse('HLA-B2701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2701"): %s' % (result,)

def test_HLA_B2702():
    result = parse('HLA-B2702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2702"): %s' % (result,)

def test_HLA_B2703():
    result = parse('HLA-B2703')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2703"): %s' % (result,)

def test_HLA_B2704():
    result = parse('HLA-B2704')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2704"): %s' % (result,)

def test_HLA_B2705():
    result = parse('HLA-B2705')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2705"): %s' % (result,)

def test_HLA_B2706():
    result = parse('HLA-B2706')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2706"): %s' % (result,)

def test_HLA_B2707():
    result = parse('HLA-B2707')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2707"): %s' % (result,)

def test_HLA_B2708():
    result = parse('HLA-B2708')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2708"): %s' % (result,)

def test_HLA_B2709():
    result = parse('HLA-B2709')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2709"): %s' % (result,)

def test_HLA_B2710():
    result = parse('HLA-B2710')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2710"): %s' % (result,)

def test_HLA_B2711():
    result = parse('HLA-B2711')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2711"): %s' % (result,)

def test_HLA_B2712():
    result = parse('HLA-B2712')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2712"): %s' % (result,)

def test_HLA_B2713():
    result = parse('HLA-B2713')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2713"): %s' % (result,)

def test_HLA_B2714():
    result = parse('HLA-B2714')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2714"): %s' % (result,)

def test_HLA_B2715():
    result = parse('HLA-B2715')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2715"): %s' % (result,)

def test_HLA_B2716():
    result = parse('HLA-B2716')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2716"): %s' % (result,)

def test_HLA_B2717():
    result = parse('HLA-B2717')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2717"): %s' % (result,)

def test_HLA_B2718():
    result = parse('HLA-B2718')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2718"): %s' % (result,)

def test_HLA_B2719():
    result = parse('HLA-B2719')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2719"): %s' % (result,)

def test_HLA_B2720():
    result = parse('HLA-B2720')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2720"): %s' % (result,)

def test_HLA_B2721():
    result = parse('HLA-B2721')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2721"): %s' % (result,)

def test_HLA_B2723():
    result = parse('HLA-B2723')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2723"): %s' % (result,)

def test_HLA_B2724():
    result = parse('HLA-B2724')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2724"): %s' % (result,)

def test_HLA_B2725():
    result = parse('HLA-B2725')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2725"): %s' % (result,)

def test_HLA_B2726():
    result = parse('HLA-B2726')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2726"): %s' % (result,)

def test_HLA_B2727():
    result = parse('HLA-B2727')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2727"): %s' % (result,)

def test_HLA_B2728():
    result = parse('HLA-B2728')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2728"): %s' % (result,)

def test_HLA_B2729():
    result = parse('HLA-B2729')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2729"): %s' % (result,)

def test_HLA_B2730():
    result = parse('HLA-B2730')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2730"): %s' % (result,)

def test_HLA_B2731():
    result = parse('HLA-B2731')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2731"): %s' % (result,)

def test_HLA_B2732():
    result = parse('HLA-B2732')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2732"): %s' % (result,)

def test_HLA_B2733():
    result = parse('HLA-B2733')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2733"): %s' % (result,)

def test_HLA_B2734():
    result = parse('HLA-B2734')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2734"): %s' % (result,)

def test_HLA_B2735():
    result = parse('HLA-B2735')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2735"): %s' % (result,)

def test_HLA_B2736():
    result = parse('HLA-B2736')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2736"): %s' % (result,)

def test_HLA_B2737():
    result = parse('HLA-B2737')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2737"): %s' % (result,)

def test_HLA_B2738():
    result = parse('HLA-B2738')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B2738"): %s' % (result,)

def test_HLA_B3501():
    result = parse('HLA-B3501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3501"): %s' % (result,)

def test_HLA_B3502():
    result = parse('HLA-B3502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3502"): %s' % (result,)

def test_HLA_B3503():
    result = parse('HLA-B3503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3503"): %s' % (result,)

def test_HLA_B3504():
    result = parse('HLA-B3504')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3504"): %s' % (result,)

def test_HLA_B3505():
    result = parse('HLA-B3505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3505"): %s' % (result,)

def test_HLA_B3506():
    result = parse('HLA-B3506')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3506"): %s' % (result,)

def test_HLA_B3507():
    result = parse('HLA-B3507')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3507"): %s' % (result,)

def test_HLA_B3508():
    result = parse('HLA-B3508')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3508"): %s' % (result,)

def test_HLA_B3509():
    result = parse('HLA-B3509')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3509"): %s' % (result,)

def test_HLA_B3510():
    result = parse('HLA-B3510')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3510"): %s' % (result,)

def test_HLA_B3511():
    result = parse('HLA-B3511')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3511"): %s' % (result,)

def test_HLA_B3512():
    result = parse('HLA-B3512')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3512"): %s' % (result,)

def test_HLA_B3513():
    result = parse('HLA-B3513')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3513"): %s' % (result,)

def test_HLA_B3514():
    result = parse('HLA-B3514')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3514"): %s' % (result,)

def test_HLA_B3515():
    result = parse('HLA-B3515')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3515"): %s' % (result,)

def test_HLA_B3516():
    result = parse('HLA-B3516')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3516"): %s' % (result,)

def test_HLA_B3517():
    result = parse('HLA-B3517')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3517"): %s' % (result,)

def test_HLA_B3518():
    result = parse('HLA-B3518')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3518"): %s' % (result,)

def test_HLA_B3519():
    result = parse('HLA-B3519')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3519"): %s' % (result,)

def test_HLA_B3520():
    result = parse('HLA-B3520')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3520"): %s' % (result,)

def test_HLA_B3521():
    result = parse('HLA-B3521')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3521"): %s' % (result,)

def test_HLA_B3522():
    result = parse('HLA-B3522')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3522"): %s' % (result,)

def test_HLA_B3523():
    result = parse('HLA-B3523')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3523"): %s' % (result,)

def test_HLA_B3524():
    result = parse('HLA-B3524')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3524"): %s' % (result,)

def test_HLA_B3525():
    result = parse('HLA-B3525')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3525"): %s' % (result,)

def test_HLA_B3526():
    result = parse('HLA-B3526')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3526"): %s' % (result,)

def test_HLA_B3527():
    result = parse('HLA-B3527')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3527"): %s' % (result,)

def test_HLA_B3528():
    result = parse('HLA-B3528')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3528"): %s' % (result,)

def test_HLA_B3529():
    result = parse('HLA-B3529')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3529"): %s' % (result,)

def test_HLA_B3530():
    result = parse('HLA-B3530')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3530"): %s' % (result,)

def test_HLA_B3531():
    result = parse('HLA-B3531')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3531"): %s' % (result,)

def test_HLA_B3532():
    result = parse('HLA-B3532')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3532"): %s' % (result,)

def test_HLA_B3533():
    result = parse('HLA-B3533')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3533"): %s' % (result,)

def test_HLA_B3534():
    result = parse('HLA-B3534')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3534"): %s' % (result,)

def test_HLA_B3535():
    result = parse('HLA-B3535')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3535"): %s' % (result,)

def test_HLA_B3536():
    result = parse('HLA-B3536')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3536"): %s' % (result,)

def test_HLA_B3537():
    result = parse('HLA-B3537')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3537"): %s' % (result,)

def test_HLA_B3538():
    result = parse('HLA-B3538')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3538"): %s' % (result,)

def test_HLA_B3539():
    result = parse('HLA-B3539')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3539"): %s' % (result,)

def test_HLA_B3540():
    result = parse('HLA-B3540')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3540"): %s' % (result,)

def test_HLA_B3541():
    result = parse('HLA-B3541')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3541"): %s' % (result,)

def test_HLA_B3542():
    result = parse('HLA-B3542')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3542"): %s' % (result,)

def test_HLA_B3543():
    result = parse('HLA-B3543')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3543"): %s' % (result,)

def test_HLA_B3544():
    result = parse('HLA-B3544')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3544"): %s' % (result,)

def test_HLA_B3545():
    result = parse('HLA-B3545')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3545"): %s' % (result,)

def test_HLA_B3546():
    result = parse('HLA-B3546')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3546"): %s' % (result,)

def test_HLA_B3547():
    result = parse('HLA-B3547')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3547"): %s' % (result,)

def test_HLA_B3548():
    result = parse('HLA-B3548')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3548"): %s' % (result,)

def test_HLA_B3549():
    result = parse('HLA-B3549')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3549"): %s' % (result,)

def test_HLA_B3550():
    result = parse('HLA-B3550')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3550"): %s' % (result,)

def test_HLA_B3551():
    result = parse('HLA-B3551')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3551"): %s' % (result,)

def test_HLA_B3552():
    result = parse('HLA-B3552')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3552"): %s' % (result,)

def test_HLA_B3554():
    result = parse('HLA-B3554')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3554"): %s' % (result,)

def test_HLA_B3555():
    result = parse('HLA-B3555')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3555"): %s' % (result,)

def test_HLA_B3556():
    result = parse('HLA-B3556')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3556"): %s' % (result,)

def test_HLA_B3557():
    result = parse('HLA-B3557')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3557"): %s' % (result,)

def test_HLA_B3558():
    result = parse('HLA-B3558')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3558"): %s' % (result,)

def test_HLA_B3559():
    result = parse('HLA-B3559')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3559"): %s' % (result,)

def test_HLA_B3560():
    result = parse('HLA-B3560')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3560"): %s' % (result,)

def test_HLA_B3561():
    result = parse('HLA-B3561')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3561"): %s' % (result,)

def test_HLA_B3562():
    result = parse('HLA-B3562')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3562"): %s' % (result,)

def test_HLA_B3563():
    result = parse('HLA-B3563')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3563"): %s' % (result,)

def test_HLA_B3564():
    result = parse('HLA-B3564')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3564"): %s' % (result,)

def test_HLA_B3565():
    result = parse('HLA-B3565')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3565"): %s' % (result,)

def test_HLA_B3566():
    result = parse('HLA-B3566')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3566"): %s' % (result,)

def test_HLA_B3567():
    result = parse('HLA-B3567')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3567"): %s' % (result,)

def test_HLA_B3568():
    result = parse('HLA-B3568')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3568"): %s' % (result,)

def test_HLA_B3569():
    result = parse('HLA-B3569')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3569"): %s' % (result,)

def test_HLA_B3570():
    result = parse('HLA-B3570')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3570"): %s' % (result,)

def test_HLA_B3571():
    result = parse('HLA-B3571')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3571"): %s' % (result,)

def test_HLA_B3572():
    result = parse('HLA-B3572')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3572"): %s' % (result,)

def test_HLA_B3573():
    result = parse('HLA-B3573')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3573"): %s' % (result,)

def test_HLA_B3574():
    result = parse('HLA-B3574')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3574"): %s' % (result,)

def test_HLA_B3575():
    result = parse('HLA-B3575')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3575"): %s' % (result,)

def test_HLA_B3576():
    result = parse('HLA-B3576')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3576"): %s' % (result,)

def test_HLA_B3577():
    result = parse('HLA-B3577')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3577"): %s' % (result,)

def test_HLA_B3701():
    result = parse('HLA-B3701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3701"): %s' % (result,)

def test_HLA_B3702():
    result = parse('HLA-B3702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3702"): %s' % (result,)

def test_HLA_B3704():
    result = parse('HLA-B3704')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3704"): %s' % (result,)

def test_HLA_B3705():
    result = parse('HLA-B3705')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3705"): %s' % (result,)

def test_HLA_B3706():
    result = parse('HLA-B3706')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3706"): %s' % (result,)

def test_HLA_B3707():
    result = parse('HLA-B3707')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3707"): %s' % (result,)

def test_HLA_B3708():
    result = parse('HLA-B3708')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3708"): %s' % (result,)

def test_HLA_B3709():
    result = parse('HLA-B3709')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3709"): %s' % (result,)

def test_HLA_B3710():
    result = parse('HLA-B3710')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3710"): %s' % (result,)

def test_HLA_B3711():
    result = parse('HLA-B3711')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3711"): %s' % (result,)

def test_HLA_B3712():
    result = parse('HLA-B3712')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3712"): %s' % (result,)

def test_HLA_B3713():
    result = parse('HLA-B3713')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3713"): %s' % (result,)

def test_HLA_B3801():
    result = parse('HLA-B3801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3801"): %s' % (result,)

def test_HLA_B3802():
    result = parse('HLA-B3802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3802"): %s' % (result,)

def test_HLA_B3803():
    result = parse('HLA-B3803')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3803"): %s' % (result,)

def test_HLA_B3804():
    result = parse('HLA-B3804')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3804"): %s' % (result,)

def test_HLA_B3805():
    result = parse('HLA-B3805')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3805"): %s' % (result,)

def test_HLA_B3806():
    result = parse('HLA-B3806')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3806"): %s' % (result,)

def test_HLA_B3807():
    result = parse('HLA-B3807')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3807"): %s' % (result,)

def test_HLA_B3808():
    result = parse('HLA-B3808')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3808"): %s' % (result,)

def test_HLA_B3809():
    result = parse('HLA-B3809')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3809"): %s' % (result,)

def test_HLA_B3810():
    result = parse('HLA-B3810')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3810"): %s' % (result,)

def test_HLA_B3811():
    result = parse('HLA-B3811')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3811"): %s' % (result,)

def test_HLA_B3812():
    result = parse('HLA-B3812')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3812"): %s' % (result,)

def test_HLA_B3813():
    result = parse('HLA-B3813')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3813"): %s' % (result,)

def test_HLA_B3814():
    result = parse('HLA-B3814')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3814"): %s' % (result,)

def test_HLA_B3815():
    result = parse('HLA-B3815')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3815"): %s' % (result,)

def test_HLA_B3816():
    result = parse('HLA-B3816')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3816"): %s' % (result,)

def test_HLA_B3901():
    result = parse('HLA-B3901')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3901"): %s' % (result,)

def test_HLA_B3902():
    result = parse('HLA-B3902')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3902"): %s' % (result,)

def test_HLA_B3903():
    result = parse('HLA-B3903')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3903"): %s' % (result,)

def test_HLA_B3904():
    result = parse('HLA-B3904')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3904"): %s' % (result,)

def test_HLA_B3905():
    result = parse('HLA-B3905')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3905"): %s' % (result,)

def test_HLA_B3906():
    result = parse('HLA-B3906')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3906"): %s' % (result,)

def test_HLA_B3908():
    result = parse('HLA-B3908')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3908"): %s' % (result,)

def test_HLA_B3909():
    result = parse('HLA-B3909')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3909"): %s' % (result,)

def test_HLA_B3910():
    result = parse('HLA-B3910')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3910"): %s' % (result,)

def test_HLA_B3912():
    result = parse('HLA-B3912')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3912"): %s' % (result,)

def test_HLA_B3913():
    result = parse('HLA-B3913')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3913"): %s' % (result,)

def test_HLA_B3914():
    result = parse('HLA-B3914')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3914"): %s' % (result,)

def test_HLA_B3915():
    result = parse('HLA-B3915')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3915"): %s' % (result,)

def test_HLA_B3916():
    result = parse('HLA-B3916')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3916"): %s' % (result,)

def test_HLA_B3917():
    result = parse('HLA-B3917')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3917"): %s' % (result,)

def test_HLA_B3918():
    result = parse('HLA-B3918')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3918"): %s' % (result,)

def test_HLA_B3919():
    result = parse('HLA-B3919')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3919"): %s' % (result,)

def test_HLA_B3920():
    result = parse('HLA-B3920')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3920"): %s' % (result,)

def test_HLA_B3922():
    result = parse('HLA-B3922')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3922"): %s' % (result,)

def test_HLA_B3923():
    result = parse('HLA-B3923')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3923"): %s' % (result,)

def test_HLA_B3924():
    result = parse('HLA-B3924')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3924"): %s' % (result,)

def test_HLA_B3926():
    result = parse('HLA-B3926')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3926"): %s' % (result,)

def test_HLA_B3927():
    result = parse('HLA-B3927')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3927"): %s' % (result,)

def test_HLA_B3928():
    result = parse('HLA-B3928')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3928"): %s' % (result,)

def test_HLA_B3929():
    result = parse('HLA-B3929')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3929"): %s' % (result,)

def test_HLA_B3930():
    result = parse('HLA-B3930')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3930"): %s' % (result,)

def test_HLA_B3931():
    result = parse('HLA-B3931')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3931"): %s' % (result,)

def test_HLA_B3932():
    result = parse('HLA-B3932')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3932"): %s' % (result,)

def test_HLA_B3933():
    result = parse('HLA-B3933')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3933"): %s' % (result,)

def test_HLA_B3934():
    result = parse('HLA-B3934')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3934"): %s' % (result,)

def test_HLA_B3935():
    result = parse('HLA-B3935')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3935"): %s' % (result,)

def test_HLA_B3936():
    result = parse('HLA-B3936')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3936"): %s' % (result,)

def test_HLA_B3937():
    result = parse('HLA-B3937')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3937"): %s' % (result,)

def test_HLA_B3938():
    result = parse('HLA-B3938')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3938"): %s' % (result,)

def test_HLA_B3939():
    result = parse('HLA-B3939')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3939"): %s' % (result,)

def test_HLA_B3941():
    result = parse('HLA-B3941')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3941"): %s' % (result,)

def test_HLA_B3942():
    result = parse('HLA-B3942')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B3942"): %s' % (result,)

def test_HLA_B4001():
    result = parse('HLA-B4001')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4001"): %s' % (result,)

def test_HLA_B4002():
    result = parse('HLA-B4002')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4002"): %s' % (result,)

def test_HLA_B4003():
    result = parse('HLA-B4003')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4003"): %s' % (result,)

def test_HLA_B4004():
    result = parse('HLA-B4004')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4004"): %s' % (result,)

def test_HLA_B4005():
    result = parse('HLA-B4005')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4005"): %s' % (result,)

def test_HLA_B4006():
    result = parse('HLA-B4006')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4006"): %s' % (result,)

def test_HLA_B4007():
    result = parse('HLA-B4007')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4007"): %s' % (result,)

def test_HLA_B4008():
    result = parse('HLA-B4008')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4008"): %s' % (result,)

def test_HLA_B4009():
    result = parse('HLA-B4009')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4009"): %s' % (result,)

def test_HLA_B4010():
    result = parse('HLA-B4010')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4010"): %s' % (result,)

def test_HLA_B4011():
    result = parse('HLA-B4011')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4011"): %s' % (result,)

def test_HLA_B4012():
    result = parse('HLA-B4012')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4012"): %s' % (result,)

def test_HLA_B4013():
    result = parse('HLA-B4013')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4013"): %s' % (result,)

def test_HLA_B4014():
    result = parse('HLA-B4014')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4014"): %s' % (result,)

def test_HLA_B4015():
    result = parse('HLA-B4015')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4015"): %s' % (result,)

def test_HLA_B4016():
    result = parse('HLA-B4016')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4016"): %s' % (result,)

def test_HLA_B4018():
    result = parse('HLA-B4018')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4018"): %s' % (result,)

def test_HLA_B4019():
    result = parse('HLA-B4019')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4019"): %s' % (result,)

def test_HLA_B4020():
    result = parse('HLA-B4020')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4020"): %s' % (result,)

def test_HLA_B4021():
    result = parse('HLA-B4021')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4021"): %s' % (result,)

def test_HLA_B4023():
    result = parse('HLA-B4023')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4023"): %s' % (result,)

def test_HLA_B4024():
    result = parse('HLA-B4024')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4024"): %s' % (result,)

def test_HLA_B4025():
    result = parse('HLA-B4025')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4025"): %s' % (result,)

def test_HLA_B4026():
    result = parse('HLA-B4026')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4026"): %s' % (result,)

def test_HLA_B4027():
    result = parse('HLA-B4027')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4027"): %s' % (result,)

def test_HLA_B4028():
    result = parse('HLA-B4028')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4028"): %s' % (result,)

def test_HLA_B4029():
    result = parse('HLA-B4029')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4029"): %s' % (result,)

def test_HLA_B4030():
    result = parse('HLA-B4030')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4030"): %s' % (result,)

def test_HLA_B4031():
    result = parse('HLA-B4031')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4031"): %s' % (result,)

def test_HLA_B4032():
    result = parse('HLA-B4032')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4032"): %s' % (result,)

def test_HLA_B4033():
    result = parse('HLA-B4033')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4033"): %s' % (result,)

def test_HLA_B4034():
    result = parse('HLA-B4034')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4034"): %s' % (result,)

def test_HLA_B4035():
    result = parse('HLA-B4035')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4035"): %s' % (result,)

def test_HLA_B4036():
    result = parse('HLA-B4036')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4036"): %s' % (result,)

def test_HLA_B4037():
    result = parse('HLA-B4037')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4037"): %s' % (result,)

def test_HLA_B4038():
    result = parse('HLA-B4038')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4038"): %s' % (result,)

def test_HLA_B4039():
    result = parse('HLA-B4039')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4039"): %s' % (result,)

def test_HLA_B4040():
    result = parse('HLA-B4040')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4040"): %s' % (result,)

def test_HLA_B4042():
    result = parse('HLA-B4042')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4042"): %s' % (result,)

def test_HLA_B4043():
    result = parse('HLA-B4043')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4043"): %s' % (result,)

def test_HLA_B4044():
    result = parse('HLA-B4044')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4044"): %s' % (result,)

def test_HLA_B4045():
    result = parse('HLA-B4045')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4045"): %s' % (result,)

def test_HLA_B4046():
    result = parse('HLA-B4046')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4046"): %s' % (result,)

def test_HLA_B4047():
    result = parse('HLA-B4047')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4047"): %s' % (result,)

def test_HLA_B4048():
    result = parse('HLA-B4048')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4048"): %s' % (result,)

def test_HLA_B4049():
    result = parse('HLA-B4049')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4049"): %s' % (result,)

def test_HLA_B4050():
    result = parse('HLA-B4050')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4050"): %s' % (result,)

def test_HLA_B4051():
    result = parse('HLA-B4051')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4051"): %s' % (result,)

def test_HLA_B4052():
    result = parse('HLA-B4052')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4052"): %s' % (result,)

def test_HLA_B4053():
    result = parse('HLA-B4053')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4053"): %s' % (result,)

def test_HLA_B4054():
    result = parse('HLA-B4054')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4054"): %s' % (result,)

def test_HLA_B4055():
    result = parse('HLA-B4055')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4055"): %s' % (result,)

def test_HLA_B4056():
    result = parse('HLA-B4056')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4056"): %s' % (result,)

def test_HLA_B4057():
    result = parse('HLA-B4057')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4057"): %s' % (result,)

def test_HLA_B4058():
    result = parse('HLA-B4058')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4058"): %s' % (result,)

def test_HLA_B4059():
    result = parse('HLA-B4059')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4059"): %s' % (result,)

def test_HLA_B4060():
    result = parse('HLA-B4060')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4060"): %s' % (result,)

def test_HLA_B4061():
    result = parse('HLA-B4061')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4061"): %s' % (result,)

def test_HLA_B4062():
    result = parse('HLA-B4062')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4062"): %s' % (result,)

def test_HLA_B4063():
    result = parse('HLA-B4063')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4063"): %s' % (result,)

def test_HLA_B4064():
    result = parse('HLA-B4064')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4064"): %s' % (result,)

def test_HLA_B4065():
    result = parse('HLA-B4065')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4065"): %s' % (result,)

def test_HLA_B4066():
    result = parse('HLA-B4066')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4066"): %s' % (result,)

def test_HLA_B4067():
    result = parse('HLA-B4067')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4067"): %s' % (result,)

def test_HLA_B4068():
    result = parse('HLA-B4068')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4068"): %s' % (result,)

def test_HLA_B4069():
    result = parse('HLA-B4069')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4069"): %s' % (result,)

def test_HLA_B4070():
    result = parse('HLA-B4070')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4070"): %s' % (result,)

def test_HLA_B4071():
    result = parse('HLA-B4071')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4071"): %s' % (result,)

def test_HLA_B4072():
    result = parse('HLA-B4072')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4072"): %s' % (result,)

def test_HLA_B4073():
    result = parse('HLA-B4073')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4073"): %s' % (result,)

def test_HLA_B4074():
    result = parse('HLA-B4074')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4074"): %s' % (result,)

def test_HLA_B4075():
    result = parse('HLA-B4075')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4075"): %s' % (result,)

def test_HLA_B4076():
    result = parse('HLA-B4076')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4076"): %s' % (result,)

def test_HLA_B4077():
    result = parse('HLA-B4077')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4077"): %s' % (result,)

def test_HLA_B4101():
    result = parse('HLA-B4101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4101"): %s' % (result,)

def test_HLA_B4102():
    result = parse('HLA-B4102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4102"): %s' % (result,)

def test_HLA_B4103():
    result = parse('HLA-B4103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4103"): %s' % (result,)

def test_HLA_B4104():
    result = parse('HLA-B4104')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4104"): %s' % (result,)

def test_HLA_B4105():
    result = parse('HLA-B4105')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4105"): %s' % (result,)

def test_HLA_B4106():
    result = parse('HLA-B4106')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4106"): %s' % (result,)

def test_HLA_B4107():
    result = parse('HLA-B4107')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4107"): %s' % (result,)

def test_HLA_B4108():
    result = parse('HLA-B4108')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4108"): %s' % (result,)

def test_HLA_B4201():
    result = parse('HLA-B4201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4201"): %s' % (result,)

def test_HLA_B4202():
    result = parse('HLA-B4202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4202"): %s' % (result,)

def test_HLA_B4204():
    result = parse('HLA-B4204')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4204"): %s' % (result,)

def test_HLA_B4205():
    result = parse('HLA-B4205')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4205"): %s' % (result,)

def test_HLA_B4206():
    result = parse('HLA-B4206')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4206"): %s' % (result,)

def test_HLA_B4207():
    result = parse('HLA-B4207')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4207"): %s' % (result,)

def test_HLA_B4208():
    result = parse('HLA-B4208')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4208"): %s' % (result,)

def test_HLA_B4209():
    result = parse('HLA-B4209')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4209"): %s' % (result,)

def test_HLA_B4402():
    result = parse('HLA-B4402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4402"): %s' % (result,)

def test_HLA_B4403():
    result = parse('HLA-B4403')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4403"): %s' % (result,)

def test_HLA_B4404():
    result = parse('HLA-B4404')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4404"): %s' % (result,)

def test_HLA_B4405():
    result = parse('HLA-B4405')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4405"): %s' % (result,)

def test_HLA_B4406():
    result = parse('HLA-B4406')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4406"): %s' % (result,)

def test_HLA_B4407():
    result = parse('HLA-B4407')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4407"): %s' % (result,)

def test_HLA_B4408():
    result = parse('HLA-B4408')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4408"): %s' % (result,)

def test_HLA_B4409():
    result = parse('HLA-B4409')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4409"): %s' % (result,)

def test_HLA_B4410():
    result = parse('HLA-B4410')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4410"): %s' % (result,)

def test_HLA_B4411():
    result = parse('HLA-B4411')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4411"): %s' % (result,)

def test_HLA_B4412():
    result = parse('HLA-B4412')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4412"): %s' % (result,)

def test_HLA_B4413():
    result = parse('HLA-B4413')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4413"): %s' % (result,)

def test_HLA_B4414():
    result = parse('HLA-B4414')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4414"): %s' % (result,)

def test_HLA_B4415():
    result = parse('HLA-B4415')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4415"): %s' % (result,)

def test_HLA_B4416():
    result = parse('HLA-B4416')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4416"): %s' % (result,)

def test_HLA_B4417():
    result = parse('HLA-B4417')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4417"): %s' % (result,)

def test_HLA_B4418():
    result = parse('HLA-B4418')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4418"): %s' % (result,)

def test_HLA_B4420():
    result = parse('HLA-B4420')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4420"): %s' % (result,)

def test_HLA_B4421():
    result = parse('HLA-B4421')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4421"): %s' % (result,)

def test_HLA_B4422():
    result = parse('HLA-B4422')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4422"): %s' % (result,)

def test_HLA_B4424():
    result = parse('HLA-B4424')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4424"): %s' % (result,)

def test_HLA_B4425():
    result = parse('HLA-B4425')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4425"): %s' % (result,)

def test_HLA_B4426():
    result = parse('HLA-B4426')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4426"): %s' % (result,)

def test_HLA_B4427():
    result = parse('HLA-B4427')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4427"): %s' % (result,)

def test_HLA_B4428():
    result = parse('HLA-B4428')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4428"): %s' % (result,)

def test_HLA_B4429():
    result = parse('HLA-B4429')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4429"): %s' % (result,)

def test_HLA_B4430():
    result = parse('HLA-B4430')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4430"): %s' % (result,)

def test_HLA_B4431():
    result = parse('HLA-B4431')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4431"): %s' % (result,)

def test_HLA_B4432():
    result = parse('HLA-B4432')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4432"): %s' % (result,)

def test_HLA_B4433():
    result = parse('HLA-B4433')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4433"): %s' % (result,)

def test_HLA_B4434():
    result = parse('HLA-B4434')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4434"): %s' % (result,)

def test_HLA_B4435():
    result = parse('HLA-B4435')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4435"): %s' % (result,)

def test_HLA_B4436():
    result = parse('HLA-B4436')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4436"): %s' % (result,)

def test_HLA_B4437():
    result = parse('HLA-B4437')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4437"): %s' % (result,)

def test_HLA_B4438():
    result = parse('HLA-B4438')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4438"): %s' % (result,)

def test_HLA_B4439():
    result = parse('HLA-B4439')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4439"): %s' % (result,)

def test_HLA_B4440():
    result = parse('HLA-B4440')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4440"): %s' % (result,)

def test_HLA_B4441():
    result = parse('HLA-B4441')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4441"): %s' % (result,)

def test_HLA_B4442():
    result = parse('HLA-B4442')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4442"): %s' % (result,)

def test_HLA_B4443():
    result = parse('HLA-B4443')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4443"): %s' % (result,)

def test_HLA_B4444():
    result = parse('HLA-B4444')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4444"): %s' % (result,)

def test_HLA_B4445():
    result = parse('HLA-B4445')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4445"): %s' % (result,)

def test_HLA_B4446():
    result = parse('HLA-B4446')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4446"): %s' % (result,)

def test_HLA_B4447():
    result = parse('HLA-B4447')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4447"): %s' % (result,)

def test_HLA_B4448():
    result = parse('HLA-B4448')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4448"): %s' % (result,)

def test_HLA_B4449():
    result = parse('HLA-B4449')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4449"): %s' % (result,)

def test_HLA_B4450():
    result = parse('HLA-B4450')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4450"): %s' % (result,)

def test_HLA_B4451():
    result = parse('HLA-B4451')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4451"): %s' % (result,)

def test_HLA_B4453():
    result = parse('HLA-B4453')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4453"): %s' % (result,)

def test_HLA_B4454():
    result = parse('HLA-B4454')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4454"): %s' % (result,)

def test_HLA_B4501():
    result = parse('HLA-B4501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4501"): %s' % (result,)

def test_HLA_B4502():
    result = parse('HLA-B4502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4502"): %s' % (result,)

def test_HLA_B4503():
    result = parse('HLA-B4503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4503"): %s' % (result,)

def test_HLA_B4504():
    result = parse('HLA-B4504')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4504"): %s' % (result,)

def test_HLA_B4505():
    result = parse('HLA-B4505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4505"): %s' % (result,)

def test_HLA_B4506():
    result = parse('HLA-B4506')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4506"): %s' % (result,)

def test_HLA_B4507():
    result = parse('HLA-B4507')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4507"): %s' % (result,)

def test_HLA_B4601():
    result = parse('HLA-B4601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4601"): %s' % (result,)

def test_HLA_B4602():
    result = parse('HLA-B4602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4602"): %s' % (result,)

def test_HLA_B4603():
    result = parse('HLA-B4603')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4603"): %s' % (result,)

def test_HLA_B4604():
    result = parse('HLA-B4604')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4604"): %s' % (result,)

def test_HLA_B4605():
    result = parse('HLA-B4605')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4605"): %s' % (result,)

def test_HLA_B4606():
    result = parse('HLA-B4606')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4606"): %s' % (result,)

def test_HLA_B4608():
    result = parse('HLA-B4608')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4608"): %s' % (result,)

def test_HLA_B4609():
    result = parse('HLA-B4609')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4609"): %s' % (result,)

def test_HLA_B4610():
    result = parse('HLA-B4610')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4610"): %s' % (result,)

def test_HLA_B4611():
    result = parse('HLA-B4611')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4611"): %s' % (result,)

def test_HLA_B4701():
    result = parse('HLA-B4701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4701"): %s' % (result,)

def test_HLA_B4702():
    result = parse('HLA-B4702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4702"): %s' % (result,)

def test_HLA_B4703():
    result = parse('HLA-B4703')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4703"): %s' % (result,)

def test_HLA_B4704():
    result = parse('HLA-B4704')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4704"): %s' % (result,)

def test_HLA_B4705():
    result = parse('HLA-B4705')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4705"): %s' % (result,)

def test_HLA_B4801():
    result = parse('HLA-B4801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4801"): %s' % (result,)

def test_HLA_B4802():
    result = parse('HLA-B4802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4802"): %s' % (result,)

def test_HLA_B4803():
    result = parse('HLA-B4803')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4803"): %s' % (result,)

def test_HLA_B4804():
    result = parse('HLA-B4804')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4804"): %s' % (result,)

def test_HLA_B4805():
    result = parse('HLA-B4805')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4805"): %s' % (result,)

def test_HLA_B4806():
    result = parse('HLA-B4806')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4806"): %s' % (result,)

def test_HLA_B4807():
    result = parse('HLA-B4807')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4807"): %s' % (result,)

def test_HLA_B4808():
    result = parse('HLA-B4808')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4808"): %s' % (result,)

def test_HLA_B4809():
    result = parse('HLA-B4809')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4809"): %s' % (result,)

def test_HLA_B4810():
    result = parse('HLA-B4810')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4810"): %s' % (result,)

def test_HLA_B4811():
    result = parse('HLA-B4811')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4811"): %s' % (result,)

def test_HLA_B4812():
    result = parse('HLA-B4812')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4812"): %s' % (result,)

def test_HLA_B4813():
    result = parse('HLA-B4813')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4813"): %s' % (result,)

def test_HLA_B4814():
    result = parse('HLA-B4814')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4814"): %s' % (result,)

def test_HLA_B4815():
    result = parse('HLA-B4815')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4815"): %s' % (result,)

def test_HLA_B4816():
    result = parse('HLA-B4816')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4816"): %s' % (result,)

def test_HLA_B4817():
    result = parse('HLA-B4817')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4817"): %s' % (result,)

def test_HLA_B4818():
    result = parse('HLA-B4818')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4818"): %s' % (result,)

def test_HLA_B4901():
    result = parse('HLA-B4901')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4901"): %s' % (result,)

def test_HLA_B4902():
    result = parse('HLA-B4902')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4902"): %s' % (result,)

def test_HLA_B4903():
    result = parse('HLA-B4903')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4903"): %s' % (result,)

def test_HLA_B4904():
    result = parse('HLA-B4904')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4904"): %s' % (result,)

def test_HLA_B4905():
    result = parse('HLA-B4905')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B4905"): %s' % (result,)

def test_HLA_B5001():
    result = parse('HLA-B5001')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5001"): %s' % (result,)

def test_HLA_B5002():
    result = parse('HLA-B5002')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5002"): %s' % (result,)

def test_HLA_B5004():
    result = parse('HLA-B5004')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5004"): %s' % (result,)

def test_HLA_B5101():
    result = parse('HLA-B5101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5101"): %s' % (result,)

def test_HLA_B5102():
    result = parse('HLA-B5102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5102"): %s' % (result,)

def test_HLA_B5103():
    result = parse('HLA-B5103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5103"): %s' % (result,)

def test_HLA_B5104():
    result = parse('HLA-B5104')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5104"): %s' % (result,)

def test_HLA_B5105():
    result = parse('HLA-B5105')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5105"): %s' % (result,)

def test_HLA_B5106():
    result = parse('HLA-B5106')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5106"): %s' % (result,)

def test_HLA_B5107():
    result = parse('HLA-B5107')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5107"): %s' % (result,)

def test_HLA_B5108():
    result = parse('HLA-B5108')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5108"): %s' % (result,)

def test_HLA_B5109():
    result = parse('HLA-B5109')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5109"): %s' % (result,)

def test_HLA_B5111():
    result = parse('HLA-B5111')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5111"): %s' % (result,)

def test_HLA_B5112():
    result = parse('HLA-B5112')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5112"): %s' % (result,)

def test_HLA_B5113():
    result = parse('HLA-B5113')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5113"): %s' % (result,)

def test_HLA_B5114():
    result = parse('HLA-B5114')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5114"): %s' % (result,)

def test_HLA_B5115():
    result = parse('HLA-B5115')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5115"): %s' % (result,)

def test_HLA_B5116():
    result = parse('HLA-B5116')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5116"): %s' % (result,)

def test_HLA_B5117():
    result = parse('HLA-B5117')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5117"): %s' % (result,)

def test_HLA_B5118():
    result = parse('HLA-B5118')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5118"): %s' % (result,)

def test_HLA_B5119():
    result = parse('HLA-B5119')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5119"): %s' % (result,)

def test_HLA_B5120():
    result = parse('HLA-B5120')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5120"): %s' % (result,)

def test_HLA_B5121():
    result = parse('HLA-B5121')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5121"): %s' % (result,)

def test_HLA_B5122():
    result = parse('HLA-B5122')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5122"): %s' % (result,)

def test_HLA_B5123():
    result = parse('HLA-B5123')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5123"): %s' % (result,)

def test_HLA_B5124():
    result = parse('HLA-B5124')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5124"): %s' % (result,)

def test_HLA_B5126():
    result = parse('HLA-B5126')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5126"): %s' % (result,)

def test_HLA_B5128():
    result = parse('HLA-B5128')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5128"): %s' % (result,)

def test_HLA_B5129():
    result = parse('HLA-B5129')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5129"): %s' % (result,)

def test_HLA_B5130():
    result = parse('HLA-B5130')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5130"): %s' % (result,)

def test_HLA_B5131():
    result = parse('HLA-B5131')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5131"): %s' % (result,)

def test_HLA_B5132():
    result = parse('HLA-B5132')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5132"): %s' % (result,)

def test_HLA_B5133():
    result = parse('HLA-B5133')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5133"): %s' % (result,)

def test_HLA_B5134():
    result = parse('HLA-B5134')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5134"): %s' % (result,)

def test_HLA_B5135():
    result = parse('HLA-B5135')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5135"): %s' % (result,)

def test_HLA_B5136():
    result = parse('HLA-B5136')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5136"): %s' % (result,)

def test_HLA_B5137():
    result = parse('HLA-B5137')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5137"): %s' % (result,)

def test_HLA_B5138():
    result = parse('HLA-B5138')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5138"): %s' % (result,)

def test_HLA_B5139():
    result = parse('HLA-B5139')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5139"): %s' % (result,)

def test_HLA_B5140():
    result = parse('HLA-B5140')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5140"): %s' % (result,)

def test_HLA_B5142():
    result = parse('HLA-B5142')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5142"): %s' % (result,)

def test_HLA_B5143():
    result = parse('HLA-B5143')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5143"): %s' % (result,)

def test_HLA_B5145():
    result = parse('HLA-B5145')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5145"): %s' % (result,)

def test_HLA_B5146():
    result = parse('HLA-B5146')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5146"): %s' % (result,)

def test_HLA_B5147():
    result = parse('HLA-B5147')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5147"): %s' % (result,)

def test_HLA_B5148():
    result = parse('HLA-B5148')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5148"): %s' % (result,)

def test_HLA_B5149():
    result = parse('HLA-B5149')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5149"): %s' % (result,)

def test_HLA_B5201():
    result = parse('HLA-B5201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5201"): %s' % (result,)

def test_HLA_B5202():
    result = parse('HLA-B5202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5202"): %s' % (result,)

def test_HLA_B5203():
    result = parse('HLA-B5203')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5203"): %s' % (result,)

def test_HLA_B5204():
    result = parse('HLA-B5204')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5204"): %s' % (result,)

def test_HLA_B5205():
    result = parse('HLA-B5205')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5205"): %s' % (result,)

def test_HLA_B5206():
    result = parse('HLA-B5206')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5206"): %s' % (result,)

def test_HLA_B5207():
    result = parse('HLA-B5207')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5207"): %s' % (result,)

def test_HLA_B5208():
    result = parse('HLA-B5208')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5208"): %s' % (result,)

def test_HLA_B5209():
    result = parse('HLA-B5209')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5209"): %s' % (result,)

def test_HLA_B5210():
    result = parse('HLA-B5210')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5210"): %s' % (result,)

def test_HLA_B5211():
    result = parse('HLA-B5211')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5211"): %s' % (result,)

def test_HLA_B5301():
    result = parse('HLA-B5301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5301"): %s' % (result,)

def test_HLA_B5302():
    result = parse('HLA-B5302')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5302"): %s' % (result,)

def test_HLA_B5303():
    result = parse('HLA-B5303')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5303"): %s' % (result,)

def test_HLA_B5304():
    result = parse('HLA-B5304')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5304"): %s' % (result,)

def test_HLA_B5305():
    result = parse('HLA-B5305')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5305"): %s' % (result,)

def test_HLA_B5306():
    result = parse('HLA-B5306')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5306"): %s' % (result,)

def test_HLA_B5307():
    result = parse('HLA-B5307')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5307"): %s' % (result,)

def test_HLA_B5308():
    result = parse('HLA-B5308')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5308"): %s' % (result,)

def test_HLA_B5309():
    result = parse('HLA-B5309')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5309"): %s' % (result,)

def test_HLA_B5310():
    result = parse('HLA-B5310')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5310"): %s' % (result,)

def test_HLA_B5311():
    result = parse('HLA-B5311')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5311"): %s' % (result,)

def test_HLA_B5312():
    result = parse('HLA-B5312')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5312"): %s' % (result,)

def test_HLA_B5313():
    result = parse('HLA-B5313')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5313"): %s' % (result,)

def test_HLA_B5401():
    result = parse('HLA-B5401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5401"): %s' % (result,)

def test_HLA_B5402():
    result = parse('HLA-B5402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5402"): %s' % (result,)

def test_HLA_B5403():
    result = parse('HLA-B5403')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5403"): %s' % (result,)

def test_HLA_B5404():
    result = parse('HLA-B5404')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5404"): %s' % (result,)

def test_HLA_B5405():
    result = parse('HLA-B5405')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5405"): %s' % (result,)

def test_HLA_B5406():
    result = parse('HLA-B5406')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5406"): %s' % (result,)

def test_HLA_B5407():
    result = parse('HLA-B5407')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5407"): %s' % (result,)

def test_HLA_B5409():
    result = parse('HLA-B5409')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5409"): %s' % (result,)

def test_HLA_B5410():
    result = parse('HLA-B5410')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5410"): %s' % (result,)

def test_HLA_B5411():
    result = parse('HLA-B5411')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5411"): %s' % (result,)

def test_HLA_B5412():
    result = parse('HLA-B5412')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5412"): %s' % (result,)

def test_HLA_B5413():
    result = parse('HLA-B5413')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5413"): %s' % (result,)

def test_HLA_B5501():
    result = parse('HLA-B5501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5501"): %s' % (result,)

def test_HLA_B5502():
    result = parse('HLA-B5502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5502"): %s' % (result,)

def test_HLA_B5503():
    result = parse('HLA-B5503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5503"): %s' % (result,)

def test_HLA_B5504():
    result = parse('HLA-B5504')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5504"): %s' % (result,)

def test_HLA_B5505():
    result = parse('HLA-B5505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5505"): %s' % (result,)

def test_HLA_B5507():
    result = parse('HLA-B5507')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5507"): %s' % (result,)

def test_HLA_B5508():
    result = parse('HLA-B5508')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5508"): %s' % (result,)

def test_HLA_B5509():
    result = parse('HLA-B5509')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5509"): %s' % (result,)

def test_HLA_B5510():
    result = parse('HLA-B5510')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5510"): %s' % (result,)

def test_HLA_B5511():
    result = parse('HLA-B5511')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5511"): %s' % (result,)

def test_HLA_B5512():
    result = parse('HLA-B5512')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5512"): %s' % (result,)

def test_HLA_B5513():
    result = parse('HLA-B5513')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5513"): %s' % (result,)

def test_HLA_B5514():
    result = parse('HLA-B5514')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5514"): %s' % (result,)

def test_HLA_B5515():
    result = parse('HLA-B5515')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5515"): %s' % (result,)

def test_HLA_B5516():
    result = parse('HLA-B5516')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5516"): %s' % (result,)

def test_HLA_B5517():
    result = parse('HLA-B5517')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5517"): %s' % (result,)

def test_HLA_B5518():
    result = parse('HLA-B5518')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5518"): %s' % (result,)

def test_HLA_B5519():
    result = parse('HLA-B5519')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5519"): %s' % (result,)

def test_HLA_B5520():
    result = parse('HLA-B5520')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5520"): %s' % (result,)

def test_HLA_B5521():
    result = parse('HLA-B5521')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5521"): %s' % (result,)

def test_HLA_B5522():
    result = parse('HLA-B5522')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5522"): %s' % (result,)

def test_HLA_B5523():
    result = parse('HLA-B5523')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5523"): %s' % (result,)

def test_HLA_B5524():
    result = parse('HLA-B5524')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5524"): %s' % (result,)

def test_HLA_B5525():
    result = parse('HLA-B5525')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5525"): %s' % (result,)

def test_HLA_B5526():
    result = parse('HLA-B5526')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5526"): %s' % (result,)

def test_HLA_B5527():
    result = parse('HLA-B5527')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5527"): %s' % (result,)

def test_HLA_B5601():
    result = parse('HLA-B5601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5601"): %s' % (result,)

def test_HLA_B5602():
    result = parse('HLA-B5602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5602"): %s' % (result,)

def test_HLA_B5603():
    result = parse('HLA-B5603')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5603"): %s' % (result,)

def test_HLA_B5604():
    result = parse('HLA-B5604')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5604"): %s' % (result,)

def test_HLA_B5605():
    result = parse('HLA-B5605')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5605"): %s' % (result,)

def test_HLA_B5606():
    result = parse('HLA-B5606')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5606"): %s' % (result,)

def test_HLA_B5607():
    result = parse('HLA-B5607')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5607"): %s' % (result,)

def test_HLA_B5608():
    result = parse('HLA-B5608')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5608"): %s' % (result,)

def test_HLA_B5609():
    result = parse('HLA-B5609')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5609"): %s' % (result,)

def test_HLA_B5610():
    result = parse('HLA-B5610')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5610"): %s' % (result,)

def test_HLA_B5611():
    result = parse('HLA-B5611')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5611"): %s' % (result,)

def test_HLA_B5612():
    result = parse('HLA-B5612')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5612"): %s' % (result,)

def test_HLA_B5613():
    result = parse('HLA-B5613')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5613"): %s' % (result,)

def test_HLA_B5614():
    result = parse('HLA-B5614')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5614"): %s' % (result,)

def test_HLA_B5615():
    result = parse('HLA-B5615')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5615"): %s' % (result,)

def test_HLA_B5616():
    result = parse('HLA-B5616')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5616"): %s' % (result,)

def test_HLA_B5617():
    result = parse('HLA-B5617')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5617"): %s' % (result,)

def test_HLA_B5618():
    result = parse('HLA-B5618')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5618"): %s' % (result,)

def test_HLA_B5620():
    result = parse('HLA-B5620')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5620"): %s' % (result,)

def test_HLA_B5701():
    result = parse('HLA-B5701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5701"): %s' % (result,)

def test_HLA_B5702():
    result = parse('HLA-B5702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5702"): %s' % (result,)

def test_HLA_B5703():
    result = parse('HLA-B5703')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5703"): %s' % (result,)

def test_HLA_B5704():
    result = parse('HLA-B5704')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5704"): %s' % (result,)

def test_HLA_B5705():
    result = parse('HLA-B5705')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5705"): %s' % (result,)

def test_HLA_B5706():
    result = parse('HLA-B5706')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5706"): %s' % (result,)

def test_HLA_B5707():
    result = parse('HLA-B5707')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5707"): %s' % (result,)

def test_HLA_B5708():
    result = parse('HLA-B5708')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5708"): %s' % (result,)

def test_HLA_B5709():
    result = parse('HLA-B5709')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5709"): %s' % (result,)

def test_HLA_B5710():
    result = parse('HLA-B5710')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5710"): %s' % (result,)

def test_HLA_B5711():
    result = parse('HLA-B5711')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5711"): %s' % (result,)

def test_HLA_B5712():
    result = parse('HLA-B5712')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5712"): %s' % (result,)

def test_HLA_B5713():
    result = parse('HLA-B5713')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5713"): %s' % (result,)

def test_HLA_B5801():
    result = parse('HLA-B5801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5801"): %s' % (result,)

def test_HLA_B5802():
    result = parse('HLA-B5802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5802"): %s' % (result,)

def test_HLA_B5804():
    result = parse('HLA-B5804')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5804"): %s' % (result,)

def test_HLA_B5805():
    result = parse('HLA-B5805')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5805"): %s' % (result,)

def test_HLA_B5806():
    result = parse('HLA-B5806')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5806"): %s' % (result,)

def test_HLA_B5807():
    result = parse('HLA-B5807')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5807"): %s' % (result,)

def test_HLA_B5808():
    result = parse('HLA-B5808')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5808"): %s' % (result,)

def test_HLA_B5809():
    result = parse('HLA-B5809')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5809"): %s' % (result,)

def test_HLA_B5811():
    result = parse('HLA-B5811')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5811"): %s' % (result,)

def test_HLA_B5812():
    result = parse('HLA-B5812')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5812"): %s' % (result,)

def test_HLA_B5813():
    result = parse('HLA-B5813')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5813"): %s' % (result,)

def test_HLA_B5814():
    result = parse('HLA-B5814')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5814"): %s' % (result,)

def test_HLA_B5815():
    result = parse('HLA-B5815')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5815"): %s' % (result,)

def test_HLA_B5901():
    result = parse('HLA-B5901')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5901"): %s' % (result,)

def test_HLA_B5902():
    result = parse('HLA-B5902')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B5902"): %s' % (result,)

def test_HLA_B6701():
    result = parse('HLA-B6701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B6701"): %s' % (result,)

def test_HLA_B6702():
    result = parse('HLA-B6702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B6702"): %s' % (result,)

def test_HLA_B7301():
    result = parse('HLA-B7301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B7301"): %s' % (result,)

def test_HLA_B7801():
    result = parse('HLA-B7801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B7801"): %s' % (result,)

def test_HLA_B7802():
    result = parse('HLA-B7802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B7802"): %s' % (result,)

def test_HLA_B7803():
    result = parse('HLA-B7803')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B7803"): %s' % (result,)

def test_HLA_B7804():
    result = parse('HLA-B7804')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B7804"): %s' % (result,)

def test_HLA_B7805():
    result = parse('HLA-B7805')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B7805"): %s' % (result,)

def test_HLA_B8101():
    result = parse('HLA-B8101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B8101"): %s' % (result,)

def test_HLA_B8102():
    result = parse('HLA-B8102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B8102"): %s' % (result,)

def test_HLA_B8201():
    result = parse('HLA-B8201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B8201"): %s' % (result,)

def test_HLA_B8202():
    result = parse('HLA-B8202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B8202"): %s' % (result,)

def test_HLA_B8301():
    result = parse('HLA-B8301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B8301"): %s' % (result,)

def test_HLA_B9501():
    result = parse('HLA-B9501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9501"): %s' % (result,)

def test_HLA_B9502():
    result = parse('HLA-B9502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9502"): %s' % (result,)

def test_HLA_B9503():
    result = parse('HLA-B9503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9503"): %s' % (result,)

def test_HLA_B9504():
    result = parse('HLA-B9504')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9504"): %s' % (result,)

def test_HLA_B9505():
    result = parse('HLA-B9505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9505"): %s' % (result,)

def test_HLA_B9506():
    result = parse('HLA-B9506')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9506"): %s' % (result,)

def test_HLA_B9507():
    result = parse('HLA-B9507')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9507"): %s' % (result,)

def test_HLA_B9508():
    result = parse('HLA-B9508')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9508"): %s' % (result,)

def test_HLA_B9509():
    result = parse('HLA-B9509')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9509"): %s' % (result,)

def test_HLA_B9510():
    result = parse('HLA-B9510')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9510"): %s' % (result,)

def test_HLA_B9512():
    result = parse('HLA-B9512')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9512"): %s' % (result,)

def test_HLA_B9513():
    result = parse('HLA-B9513')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9513"): %s' % (result,)

def test_HLA_B9514():
    result = parse('HLA-B9514')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9514"): %s' % (result,)

def test_HLA_B9515():
    result = parse('HLA-B9515')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9515"): %s' % (result,)

def test_HLA_B9516():
    result = parse('HLA-B9516')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9516"): %s' % (result,)

def test_HLA_B9517():
    result = parse('HLA-B9517')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9517"): %s' % (result,)

def test_HLA_B9518():
    result = parse('HLA-B9518')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9518"): %s' % (result,)

def test_HLA_B9519():
    result = parse('HLA-B9519')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9519"): %s' % (result,)

def test_HLA_B9520():
    result = parse('HLA-B9520')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9520"): %s' % (result,)

def test_HLA_B9521():
    result = parse('HLA-B9521')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9521"): %s' % (result,)

def test_HLA_B9522():
    result = parse('HLA-B9522')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9522"): %s' % (result,)

def test_HLA_B9523():
    result = parse('HLA-B9523')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9523"): %s' % (result,)

def test_HLA_B9524():
    result = parse('HLA-B9524')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9524"): %s' % (result,)

def test_HLA_B9525():
    result = parse('HLA-B9525')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9525"): %s' % (result,)

def test_HLA_B9526():
    result = parse('HLA-B9526')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9526"): %s' % (result,)

def test_HLA_B9527():
    result = parse('HLA-B9527')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9527"): %s' % (result,)

def test_HLA_B9528():
    result = parse('HLA-B9528')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9528"): %s' % (result,)

def test_HLA_B9529():
    result = parse('HLA-B9529')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9529"): %s' % (result,)

def test_HLA_B9530():
    result = parse('HLA-B9530')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9530"): %s' % (result,)

def test_HLA_B9532():
    result = parse('HLA-B9532')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-B9532"): %s' % (result,)

def test_HLA_C0102():
    result = parse('HLA-C0102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0102"): %s' % (result,)

def test_HLA_C0103():
    result = parse('HLA-C0103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0103"): %s' % (result,)

def test_HLA_C0104():
    result = parse('HLA-C0104')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0104"): %s' % (result,)

def test_HLA_C0105():
    result = parse('HLA-C0105')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0105"): %s' % (result,)

def test_HLA_C0106():
    result = parse('HLA-C0106')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0106"): %s' % (result,)

def test_HLA_C0107():
    result = parse('HLA-C0107')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0107"): %s' % (result,)

def test_HLA_C0108():
    result = parse('HLA-C0108')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0108"): %s' % (result,)

def test_HLA_C0109():
    result = parse('HLA-C0109')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0109"): %s' % (result,)

def test_HLA_C0110():
    result = parse('HLA-C0110')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0110"): %s' % (result,)

def test_HLA_C0111():
    result = parse('HLA-C0111')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0111"): %s' % (result,)

def test_HLA_C0112():
    result = parse('HLA-C0112')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0112"): %s' % (result,)

def test_HLA_C0113():
    result = parse('HLA-C0113')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0113"): %s' % (result,)

def test_HLA_C0202():
    result = parse('HLA-C0202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0202"): %s' % (result,)

def test_HLA_C0203():
    result = parse('HLA-C0203')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0203"): %s' % (result,)

def test_HLA_C0204():
    result = parse('HLA-C0204')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0204"): %s' % (result,)

def test_HLA_C0205():
    result = parse('HLA-C0205')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0205"): %s' % (result,)

def test_HLA_C0206():
    result = parse('HLA-C0206')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0206"): %s' % (result,)

def test_HLA_C0207():
    result = parse('HLA-C0207')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0207"): %s' % (result,)

def test_HLA_C0208():
    result = parse('HLA-C0208')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0208"): %s' % (result,)

def test_HLA_C0209():
    result = parse('HLA-C0209')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0209"): %s' % (result,)

def test_HLA_C0210():
    result = parse('HLA-C0210')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0210"): %s' % (result,)

def test_HLA_C0211():
    result = parse('HLA-C0211')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0211"): %s' % (result,)

def test_HLA_C0212():
    result = parse('HLA-C0212')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0212"): %s' % (result,)

def test_HLA_C0213():
    result = parse('HLA-C0213')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0213"): %s' % (result,)

def test_HLA_C0214():
    result = parse('HLA-C0214')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0214"): %s' % (result,)

def test_HLA_C0301():
    result = parse('HLA-C0301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0301"): %s' % (result,)

def test_HLA_C0302():
    result = parse('HLA-C0302')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0302"): %s' % (result,)

def test_HLA_C0303():
    result = parse('HLA-C0303')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0303"): %s' % (result,)

def test_HLA_C0304():
    result = parse('HLA-C0304')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0304"): %s' % (result,)

def test_HLA_C0305():
    result = parse('HLA-C0305')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0305"): %s' % (result,)

def test_HLA_C0306():
    result = parse('HLA-C0306')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0306"): %s' % (result,)

def test_HLA_C0307():
    result = parse('HLA-C0307')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0307"): %s' % (result,)

def test_HLA_C0308():
    result = parse('HLA-C0308')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0308"): %s' % (result,)

def test_HLA_C0309():
    result = parse('HLA-C0309')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0309"): %s' % (result,)

def test_HLA_C0310():
    result = parse('HLA-C0310')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0310"): %s' % (result,)

def test_HLA_C0311():
    result = parse('HLA-C0311')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0311"): %s' % (result,)

def test_HLA_C0312():
    result = parse('HLA-C0312')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0312"): %s' % (result,)

def test_HLA_C0313():
    result = parse('HLA-C0313')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0313"): %s' % (result,)

def test_HLA_C0314():
    result = parse('HLA-C0314')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0314"): %s' % (result,)

def test_HLA_C0315():
    result = parse('HLA-C0315')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0315"): %s' % (result,)

def test_HLA_C0316():
    result = parse('HLA-C0316')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0316"): %s' % (result,)

def test_HLA_C0317():
    result = parse('HLA-C0317')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0317"): %s' % (result,)

def test_HLA_C0318():
    result = parse('HLA-C0318')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0318"): %s' % (result,)

def test_HLA_C0319():
    result = parse('HLA-C0319')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0319"): %s' % (result,)

def test_HLA_C0321():
    result = parse('HLA-C0321')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0321"): %s' % (result,)

def test_HLA_C0322():
    result = parse('HLA-C0322')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0322"): %s' % (result,)

def test_HLA_C0323():
    result = parse('HLA-C0323')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0323"): %s' % (result,)

def test_HLA_C0324():
    result = parse('HLA-C0324')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0324"): %s' % (result,)

def test_HLA_C0325():
    result = parse('HLA-C0325')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0325"): %s' % (result,)

def test_HLA_C0401():
    result = parse('HLA-C0401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0401"): %s' % (result,)

def test_HLA_C0403():
    result = parse('HLA-C0403')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0403"): %s' % (result,)

def test_HLA_C0404():
    result = parse('HLA-C0404')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0404"): %s' % (result,)

def test_HLA_C0405():
    result = parse('HLA-C0405')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0405"): %s' % (result,)

def test_HLA_C0406():
    result = parse('HLA-C0406')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0406"): %s' % (result,)

def test_HLA_C0407():
    result = parse('HLA-C0407')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0407"): %s' % (result,)

def test_HLA_C0408():
    result = parse('HLA-C0408')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0408"): %s' % (result,)

def test_HLA_C0409():
    result = parse('HLA-C0409')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0409"): %s' % (result,)

def test_HLA_C0410():
    result = parse('HLA-C0410')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0410"): %s' % (result,)

def test_HLA_C0411():
    result = parse('HLA-C0411')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0411"): %s' % (result,)

def test_HLA_C0412():
    result = parse('HLA-C0412')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0412"): %s' % (result,)

def test_HLA_C0413():
    result = parse('HLA-C0413')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0413"): %s' % (result,)

def test_HLA_C0414():
    result = parse('HLA-C0414')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0414"): %s' % (result,)

def test_HLA_C0415():
    result = parse('HLA-C0415')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0415"): %s' % (result,)

def test_HLA_C0416():
    result = parse('HLA-C0416')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0416"): %s' % (result,)

def test_HLA_C0417():
    result = parse('HLA-C0417')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0417"): %s' % (result,)

def test_HLA_C0418():
    result = parse('HLA-C0418')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0418"): %s' % (result,)

def test_HLA_C0501():
    result = parse('HLA-C0501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0501"): %s' % (result,)

def test_HLA_C0502():
    result = parse('HLA-C0502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0502"): %s' % (result,)

def test_HLA_C0503():
    result = parse('HLA-C0503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0503"): %s' % (result,)

def test_HLA_C0504():
    result = parse('HLA-C0504')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0504"): %s' % (result,)

def test_HLA_C0505():
    result = parse('HLA-C0505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0505"): %s' % (result,)

def test_HLA_C0506():
    result = parse('HLA-C0506')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0506"): %s' % (result,)

def test_HLA_C0508():
    result = parse('HLA-C0508')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0508"): %s' % (result,)

def test_HLA_C0509():
    result = parse('HLA-C0509')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0509"): %s' % (result,)

def test_HLA_C0510():
    result = parse('HLA-C0510')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0510"): %s' % (result,)

def test_HLA_C0511():
    result = parse('HLA-C0511')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0511"): %s' % (result,)

def test_HLA_C0512():
    result = parse('HLA-C0512')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0512"): %s' % (result,)

def test_HLA_C0513():
    result = parse('HLA-C0513')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0513"): %s' % (result,)

def test_HLA_C0602():
    result = parse('HLA-C0602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0602"): %s' % (result,)

def test_HLA_C0603():
    result = parse('HLA-C0603')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0603"): %s' % (result,)

def test_HLA_C0604():
    result = parse('HLA-C0604')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0604"): %s' % (result,)

def test_HLA_C0605():
    result = parse('HLA-C0605')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0605"): %s' % (result,)

def test_HLA_C0606():
    result = parse('HLA-C0606')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0606"): %s' % (result,)

def test_HLA_C0607():
    result = parse('HLA-C0607')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0607"): %s' % (result,)

def test_HLA_C0608():
    result = parse('HLA-C0608')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0608"): %s' % (result,)

def test_HLA_C0609():
    result = parse('HLA-C0609')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0609"): %s' % (result,)

def test_HLA_C0610():
    result = parse('HLA-C0610')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0610"): %s' % (result,)

def test_HLA_C0611():
    result = parse('HLA-C0611')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0611"): %s' % (result,)

def test_HLA_C0612():
    result = parse('HLA-C0612')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0612"): %s' % (result,)

def test_HLA_C0613():
    result = parse('HLA-C0613')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0613"): %s' % (result,)

def test_HLA_C0701():
    result = parse('HLA-C0701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0701"): %s' % (result,)

def test_HLA_C0702():
    result = parse('HLA-C0702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0702"): %s' % (result,)

def test_HLA_C0703():
    result = parse('HLA-C0703')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0703"): %s' % (result,)

def test_HLA_C0704():
    result = parse('HLA-C0704')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0704"): %s' % (result,)

def test_HLA_C0705():
    result = parse('HLA-C0705')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0705"): %s' % (result,)

def test_HLA_C0706():
    result = parse('HLA-C0706')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0706"): %s' % (result,)

def test_HLA_C0707():
    result = parse('HLA-C0707')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0707"): %s' % (result,)

def test_HLA_C0708():
    result = parse('HLA-C0708')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0708"): %s' % (result,)

def test_HLA_C0709():
    result = parse('HLA-C0709')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0709"): %s' % (result,)

def test_HLA_C0710():
    result = parse('HLA-C0710')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0710"): %s' % (result,)

def test_HLA_C0711():
    result = parse('HLA-C0711')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0711"): %s' % (result,)

def test_HLA_C0712():
    result = parse('HLA-C0712')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0712"): %s' % (result,)

def test_HLA_C0713():
    result = parse('HLA-C0713')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0713"): %s' % (result,)

def test_HLA_C0714():
    result = parse('HLA-C0714')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0714"): %s' % (result,)

def test_HLA_C0715():
    result = parse('HLA-C0715')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0715"): %s' % (result,)

def test_HLA_C0716():
    result = parse('HLA-C0716')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0716"): %s' % (result,)

def test_HLA_C0717():
    result = parse('HLA-C0717')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0717"): %s' % (result,)

def test_HLA_C0718():
    result = parse('HLA-C0718')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0718"): %s' % (result,)

def test_HLA_C0719():
    result = parse('HLA-C0719')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0719"): %s' % (result,)

def test_HLA_C0720():
    result = parse('HLA-C0720')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0720"): %s' % (result,)

def test_HLA_C0721():
    result = parse('HLA-C0721')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0721"): %s' % (result,)

def test_HLA_C0722():
    result = parse('HLA-C0722')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0722"): %s' % (result,)

def test_HLA_C0723():
    result = parse('HLA-C0723')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0723"): %s' % (result,)

def test_HLA_C0724():
    result = parse('HLA-C0724')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0724"): %s' % (result,)

def test_HLA_C0725():
    result = parse('HLA-C0725')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0725"): %s' % (result,)

def test_HLA_C0726():
    result = parse('HLA-C0726')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0726"): %s' % (result,)

def test_HLA_C0727():
    result = parse('HLA-C0727')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0727"): %s' % (result,)

def test_HLA_C0728():
    result = parse('HLA-C0728')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0728"): %s' % (result,)

def test_HLA_C0729():
    result = parse('HLA-C0729')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0729"): %s' % (result,)

def test_HLA_C0730():
    result = parse('HLA-C0730')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0730"): %s' % (result,)

def test_HLA_C0731():
    result = parse('HLA-C0731')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0731"): %s' % (result,)

def test_HLA_C0732():
    result = parse('HLA-C0732')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0732"): %s' % (result,)

def test_HLA_C0734():
    result = parse('HLA-C0734')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0734"): %s' % (result,)

def test_HLA_C0735():
    result = parse('HLA-C0735')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0735"): %s' % (result,)

def test_HLA_C0736():
    result = parse('HLA-C0736')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0736"): %s' % (result,)

def test_HLA_C0737():
    result = parse('HLA-C0737')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0737"): %s' % (result,)

def test_HLA_C0738():
    result = parse('HLA-C0738')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0738"): %s' % (result,)

def test_HLA_C0801():
    result = parse('HLA-C0801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0801"): %s' % (result,)

def test_HLA_C0802():
    result = parse('HLA-C0802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0802"): %s' % (result,)

def test_HLA_C0803():
    result = parse('HLA-C0803')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0803"): %s' % (result,)

def test_HLA_C0804():
    result = parse('HLA-C0804')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0804"): %s' % (result,)

def test_HLA_C0805():
    result = parse('HLA-C0805')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0805"): %s' % (result,)

def test_HLA_C0806():
    result = parse('HLA-C0806')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0806"): %s' % (result,)

def test_HLA_C0807():
    result = parse('HLA-C0807')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0807"): %s' % (result,)

def test_HLA_C0808():
    result = parse('HLA-C0808')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0808"): %s' % (result,)

def test_HLA_C0809():
    result = parse('HLA-C0809')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0809"): %s' % (result,)

def test_HLA_C0810():
    result = parse('HLA-C0810')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0810"): %s' % (result,)

def test_HLA_C0811():
    result = parse('HLA-C0811')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0811"): %s' % (result,)

def test_HLA_C0812():
    result = parse('HLA-C0812')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0812"): %s' % (result,)

def test_HLA_C0813():
    result = parse('HLA-C0813')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0813"): %s' % (result,)

def test_HLA_C0814():
    result = parse('HLA-C0814')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C0814"): %s' % (result,)

def test_HLA_C1202():
    result = parse('HLA-C1202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1202"): %s' % (result,)

def test_HLA_C1203():
    result = parse('HLA-C1203')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1203"): %s' % (result,)

def test_HLA_C1204():
    result = parse('HLA-C1204')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1204"): %s' % (result,)

def test_HLA_C1205():
    result = parse('HLA-C1205')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1205"): %s' % (result,)

def test_HLA_C1206():
    result = parse('HLA-C1206')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1206"): %s' % (result,)

def test_HLA_C1207():
    result = parse('HLA-C1207')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1207"): %s' % (result,)

def test_HLA_C1208():
    result = parse('HLA-C1208')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1208"): %s' % (result,)

def test_HLA_C1209():
    result = parse('HLA-C1209')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1209"): %s' % (result,)

def test_HLA_C1210():
    result = parse('HLA-C1210')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1210"): %s' % (result,)

def test_HLA_C1211():
    result = parse('HLA-C1211')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1211"): %s' % (result,)

def test_HLA_C1212():
    result = parse('HLA-C1212')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1212"): %s' % (result,)

def test_HLA_C1213():
    result = parse('HLA-C1213')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1213"): %s' % (result,)

def test_HLA_C1214():
    result = parse('HLA-C1214')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1214"): %s' % (result,)

def test_HLA_C1215():
    result = parse('HLA-C1215')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1215"): %s' % (result,)

def test_HLA_C1216():
    result = parse('HLA-C1216')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1216"): %s' % (result,)

def test_HLA_C1217():
    result = parse('HLA-C1217')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1217"): %s' % (result,)

def test_HLA_C1402():
    result = parse('HLA-C1402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1402"): %s' % (result,)

def test_HLA_C1403():
    result = parse('HLA-C1403')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1403"): %s' % (result,)

def test_HLA_C1404():
    result = parse('HLA-C1404')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1404"): %s' % (result,)

def test_HLA_C1405():
    result = parse('HLA-C1405')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1405"): %s' % (result,)

def test_HLA_C1406():
    result = parse('HLA-C1406')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1406"): %s' % (result,)

def test_HLA_C1407():
    result = parse('HLA-C1407')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1407"): %s' % (result,)

def test_HLA_C1502():
    result = parse('HLA-C1502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1502"): %s' % (result,)

def test_HLA_C1503():
    result = parse('HLA-C1503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1503"): %s' % (result,)

def test_HLA_C1504():
    result = parse('HLA-C1504')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1504"): %s' % (result,)

def test_HLA_C1505():
    result = parse('HLA-C1505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1505"): %s' % (result,)

def test_HLA_C1506():
    result = parse('HLA-C1506')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1506"): %s' % (result,)

def test_HLA_C1507():
    result = parse('HLA-C1507')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1507"): %s' % (result,)

def test_HLA_C1508():
    result = parse('HLA-C1508')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1508"): %s' % (result,)

def test_HLA_C1509():
    result = parse('HLA-C1509')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1509"): %s' % (result,)

def test_HLA_C1510():
    result = parse('HLA-C1510')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1510"): %s' % (result,)

def test_HLA_C1511():
    result = parse('HLA-C1511')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1511"): %s' % (result,)

def test_HLA_C1512():
    result = parse('HLA-C1512')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1512"): %s' % (result,)

def test_HLA_C1513():
    result = parse('HLA-C1513')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1513"): %s' % (result,)

def test_HLA_C1514():
    result = parse('HLA-C1514')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1514"): %s' % (result,)

def test_HLA_C1515():
    result = parse('HLA-C1515')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1515"): %s' % (result,)

def test_HLA_C1516():
    result = parse('HLA-C1516')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1516"): %s' % (result,)

def test_HLA_C1517():
    result = parse('HLA-C1517')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1517"): %s' % (result,)

def test_HLA_C1601():
    result = parse('HLA-C1601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1601"): %s' % (result,)

def test_HLA_C1602():
    result = parse('HLA-C1602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1602"): %s' % (result,)

def test_HLA_C1604():
    result = parse('HLA-C1604')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1604"): %s' % (result,)

def test_HLA_C1606():
    result = parse('HLA-C1606')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1606"): %s' % (result,)

def test_HLA_C1607():
    result = parse('HLA-C1607')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1607"): %s' % (result,)

def test_HLA_C1608():
    result = parse('HLA-C1608')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1608"): %s' % (result,)

def test_HLA_C1701():
    result = parse('HLA-C1701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1701"): %s' % (result,)

def test_HLA_C1702():
    result = parse('HLA-C1702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1702"): %s' % (result,)

def test_HLA_C1703():
    result = parse('HLA-C1703')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1703"): %s' % (result,)

def test_HLA_C1704():
    result = parse('HLA-C1704')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1704"): %s' % (result,)

def test_HLA_C1801():
    result = parse('HLA-C1801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1801"): %s' % (result,)

def test_HLA_C1802():
    result = parse('HLA-C1802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-C1802"): %s' % (result,)

def test_HLA_E0101():
    result = parse('HLA-E0101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-E0101"): %s' % (result,)

def test_HLA_E0103():
    result = parse('HLA-E0103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-E0103"): %s' % (result,)

def test_HLA_E01_03():
    result = parse('HLA-E01:03')
    assert result.__class__ is Allele, \
                                'Expected parse("HLA-E01:03") to be Allele but got %s' % (result,)

def test_HLA_G0101():
    result = parse('HLA-G0101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-G0101"): %s' % (result,)

def test_HLA_G0102():
    result = parse('HLA-G0102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-G0102"): %s' % (result,)

def test_HLA_G0103():
    result = parse('HLA-G0103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-G0103"): %s' % (result,)

def test_HLA_G0104():
    result = parse('HLA-G0104')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-G0104"): %s' % (result,)

def test_HLA_G0106():
    result = parse('HLA-G0106')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-G0106"): %s' % (result,)

def test_HLA_G0107():
    result = parse('HLA-G0107')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-G0107"): %s' % (result,)

def test_HLA_G0108():
    result = parse('HLA-G0108')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-G0108"): %s' % (result,)

def test_HLA_G0109():
    result = parse('HLA-G0109')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("HLA-G0109"): %s' % (result,)

def test_Mamu_A01():
    result = parse('Mamu-A01')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A01"): %s' % (result,)

def test_Mamu_A02():
    result = parse('Mamu-A02')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A02"): %s' % (result,)

def test_Mamu_A03():
    result = parse('Mamu-A03')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A03"): %s' % (result,)

def test_Mamu_A04():
    result = parse('Mamu-A04')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A04"): %s' % (result,)

def test_Mamu_A0505():
    result = parse('Mamu-A0505')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A0505"): %s' % (result,)

def test_Mamu_A0506():
    result = parse('Mamu-A0506')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A0506"): %s' % (result,)

def test_Mamu_A0507():
    result = parse('Mamu-A0507')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A0507"): %s' % (result,)

def test_Mamu_A0509():
    result = parse('Mamu-A0509')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A0509"): %s' % (result,)

def test_Mamu_A0510():
    result = parse('Mamu-A0510')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A0510"): %s' % (result,)

def test_Mamu_A0511():
    result = parse('Mamu-A0511')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A0511"): %s' % (result,)

def test_Mamu_A06():
    result = parse('Mamu-A06')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A06"): %s' % (result,)

def test_Mamu_A0602():
    result = parse('Mamu-A0602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A0602"): %s' % (result,)

def test_Mamu_A07():
    result = parse('Mamu-A07')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A07"): %s' % (result,)

def test_Mamu_A0703():
    result = parse('Mamu-A0703')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A0703"): %s' % (result,)

def test_Mamu_A11():
    result = parse('Mamu-A11')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A11"): %s' % (result,)

def test_Mamu_A1305():
    result = parse('Mamu-A1305')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A1305"): %s' % (result,)

def test_Mamu_A1306():
    result = parse('Mamu-A1306')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A1306"): %s' % (result,)

def test_Mamu_A1602():
    result = parse('Mamu-A1602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A1602"): %s' % (result,)

def test_Mamu_A19():
    result = parse('Mamu-A19')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A19"): %s' % (result,)

def test_Mamu_A20101():
    result = parse('Mamu-A20101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A20101"): %s' % (result,)

def test_Mamu_A20102():
    result = parse('Mamu-A20102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A20102"): %s' % (result,)

def test_Mamu_A21():
    result = parse('Mamu-A21')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A21"): %s' % (result,)

def test_Mamu_A2201():
    result = parse('Mamu-A2201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A2201"): %s' % (result,)

def test_Mamu_A23():
    result = parse('Mamu-A23')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A23"): %s' % (result,)

def test_Mamu_A24():
    result = parse('Mamu-A24')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A24"): %s' % (result,)

def test_Mamu_A25():
    result = parse('Mamu-A25')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A25"): %s' % (result,)

def test_Mamu_A26():
    result = parse('Mamu-A26')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A26"): %s' % (result,)

def test_Mamu_A2601():
    result = parse('Mamu-A2601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A2601"): %s' % (result,)

def test_Mamu_A28():
    result = parse('Mamu-A28')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A28"): %s' % (result,)

def test_Mamu_A70103():
    result = parse('Mamu-A70103')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-A70103"): %s' % (result,)

def test_Mamu_B008_01():
    result = parse('Mamu-B008:01')
    assert result.__class__ is Allele, \
                                'Expected parse("Mamu-B008:01") to be Allele but got %s' % (result,)

def test_Mamu_B01():
    result = parse('Mamu-B01')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B01"): %s' % (result,)

def test_Mamu_B02():
    result = parse('Mamu-B02')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B02"): %s' % (result,)

def test_Mamu_B03():
    result = parse('Mamu-B03')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B03"): %s' % (result,)

def test_Mamu_B03901():
    result = parse('Mamu-B03901')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B03901"): %s' % (result,)

def test_Mamu_B04():
    result = parse('Mamu-B04')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B04"): %s' % (result,)

def test_Mamu_B05():
    result = parse('Mamu-B05')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B05"): %s' % (result,)

def test_Mamu_B07():
    result = parse('Mamu-B07')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B07"): %s' % (result,)

def test_Mamu_B08():
    result = parse('Mamu-B08')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B08"): %s' % (result,)

def test_Mamu_B1001():
    result = parse('Mamu-B1001')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B1001"): %s' % (result,)

def test_Mamu_B12():
    result = parse('Mamu-B12')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B12"): %s' % (result,)

def test_Mamu_B17():
    result = parse('Mamu-B17')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B17"): %s' % (result,)

def test_Mamu_B19():
    result = parse('Mamu-B19')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B19"): %s' % (result,)

def test_Mamu_B20():
    result = parse('Mamu-B20')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B20"): %s' % (result,)

def test_Mamu_B21():
    result = parse('Mamu-B21')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B21"): %s' % (result,)

def test_Mamu_B22():
    result = parse('Mamu-B22')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B22"): %s' % (result,)

def test_Mamu_B24():
    result = parse('Mamu-B24')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B24"): %s' % (result,)

def test_Mamu_B27():
    result = parse('Mamu-B27')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B27"): %s' % (result,)

def test_Mamu_B28():
    result = parse('Mamu-B28')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B28"): %s' % (result,)

def test_Mamu_B3002():
    result = parse('Mamu-B3002')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B3002"): %s' % (result,)

def test_Mamu_B36():
    result = parse('Mamu-B36')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B36"): %s' % (result,)

def test_Mamu_B37():
    result = parse('Mamu-B37')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B37"): %s' % (result,)

def test_Mamu_B38():
    result = parse('Mamu-B38')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B38"): %s' % (result,)

def test_Mamu_B39():
    result = parse('Mamu-B39')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B39"): %s' % (result,)

def test_Mamu_B3901():
    result = parse('Mamu-B3901')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B3901"): %s' % (result,)

def test_Mamu_B40():
    result = parse('Mamu-B40')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B40"): %s' % (result,)

def test_Mamu_B41():
    result = parse('Mamu-B41')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B41"): %s' % (result,)

def test_Mamu_B43():
    result = parse('Mamu-B43')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B43"): %s' % (result,)

def test_Mamu_B44():
    result = parse('Mamu-B44')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B44"): %s' % (result,)

def test_Mamu_B45():
    result = parse('Mamu-B45')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B45"): %s' % (result,)

def test_Mamu_B46():
    result = parse('Mamu-B46')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B46"): %s' % (result,)

def test_Mamu_B47():
    result = parse('Mamu-B47')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B47"): %s' % (result,)

def test_Mamu_B48():
    result = parse('Mamu-B48')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B48"): %s' % (result,)

def test_Mamu_B49():
    result = parse('Mamu-B49')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B49"): %s' % (result,)

def test_Mamu_B5002():
    result = parse('Mamu-B5002')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B5002"): %s' % (result,)

def test_Mamu_B52():
    result = parse('Mamu-B52')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B52"): %s' % (result,)

def test_Mamu_B53():
    result = parse('Mamu-B53')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B53"): %s' % (result,)

def test_Mamu_B55():
    result = parse('Mamu-B55')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B55"): %s' % (result,)

def test_Mamu_B57():
    result = parse('Mamu-B57')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B57"): %s' % (result,)

def test_Mamu_B5802():
    result = parse('Mamu-B5802')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B5802"): %s' % (result,)

def test_Mamu_B6002():
    result = parse('Mamu-B6002')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B6002"): %s' % (result,)

def test_Mamu_B61():
    result = parse('Mamu-B61')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B61"): %s' % (result,)

def test_Mamu_B63():
    result = parse('Mamu-B63')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B63"): %s' % (result,)

def test_Mamu_B64():
    result = parse('Mamu-B64')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B64"): %s' % (result,)

def test_Mamu_B65():
    result = parse('Mamu-B65')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B65"): %s' % (result,)

def test_Mamu_B66():
    result = parse('Mamu-B66')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B66"): %s' % (result,)

def test_Mamu_B6601():
    result = parse('Mamu-B6601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B6601"): %s' % (result,)

def test_Mamu_B67():
    result = parse('Mamu-B67')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B67"): %s' % (result,)

def test_Mamu_B69():
    result = parse('Mamu-B69')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B69"): %s' % (result,)

def test_Mamu_B70():
    result = parse('Mamu-B70')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B70"): %s' % (result,)

def test_Mamu_B71():
    result = parse('Mamu-B71')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B71"): %s' % (result,)

def test_Mamu_B8301():
    result = parse('Mamu-B8301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B8301"): %s' % (result,)

def test_Mamu_B8701():
    result = parse('Mamu-B8701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("Mamu-B8701"): %s' % (result,)

def test_SLA_10101():
    result = parse('SLA-10101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10101"): %s' % (result,)

def test_SLA_10201():
    result = parse('SLA-10201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10201"): %s' % (result,)

def test_SLA_10202():
    result = parse('SLA-10202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10202"): %s' % (result,)

def test_SLA_10401():
    result = parse('SLA-10401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10401"): %s' % (result,)

def test_SLA_10501():
    result = parse('SLA-10501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10501"): %s' % (result,)

def test_SLA_10601():
    result = parse('SLA-10601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10601"): %s' % (result,)

def test_SLA_10701():
    result = parse('SLA-10701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10701"): %s' % (result,)

def test_SLA_10702():
    result = parse('SLA-10702')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10702"): %s' % (result,)

def test_SLA_10801():
    result = parse('SLA-10801')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-10801"): %s' % (result,)

def test_SLA_11101():
    result = parse('SLA-11101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-11101"): %s' % (result,)

def test_SLA_11201():
    result = parse('SLA-11201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-11201"): %s' % (result,)

def test_SLA_11301():
    result = parse('SLA-11301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-11301"): %s' % (result,)

def test_SLA_20101():
    result = parse('SLA-20101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20101"): %s' % (result,)

def test_SLA_20102():
    result = parse('SLA-20102')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20102"): %s' % (result,)

def test_SLA_20201():
    result = parse('SLA-20201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20201"): %s' % (result,)

def test_SLA_20202():
    result = parse('SLA-20202')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20202"): %s' % (result,)

def test_SLA_20301():
    result = parse('SLA-20301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20301"): %s' % (result,)

def test_SLA_20302():
    result = parse('SLA-20302')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20302"): %s' % (result,)

def test_SLA_20401():
    result = parse('SLA-20401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20401"): %s' % (result,)

def test_SLA_20402():
    result = parse('SLA-20402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20402"): %s' % (result,)

def test_SLA_20501():
    result = parse('SLA-20501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20501"): %s' % (result,)

def test_SLA_20502():
    result = parse('SLA-20502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20502"): %s' % (result,)

def test_SLA_20601():
    result = parse('SLA-20601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20601"): %s' % (result,)

def test_SLA_20701():
    result = parse('SLA-20701')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-20701"): %s' % (result,)

def test_SLA_21001():
    result = parse('SLA-21001')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-21001"): %s' % (result,)

def test_SLA_21002():
    result = parse('SLA-21002')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-21002"): %s' % (result,)

def test_SLA_21201():
    result = parse('SLA-21201')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-21201"): %s' % (result,)

def test_SLA_30101():
    result = parse('SLA-30101')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30101"): %s' % (result,)

def test_SLA_30301():
    result = parse('SLA-30301')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30301"): %s' % (result,)

def test_SLA_30302():
    result = parse('SLA-30302')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30302"): %s' % (result,)

def test_SLA_30303():
    result = parse('SLA-30303')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30303"): %s' % (result,)

def test_SLA_30304():
    result = parse('SLA-30304')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30304"): %s' % (result,)

def test_SLA_30401():
    result = parse('SLA-30401')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30401"): %s' % (result,)

def test_SLA_30402():
    result = parse('SLA-30402')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30402"): %s' % (result,)

def test_SLA_30501():
    result = parse('SLA-30501')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30501"): %s' % (result,)

def test_SLA_30502():
    result = parse('SLA-30502')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30502"): %s' % (result,)

def test_SLA_30503():
    result = parse('SLA-30503')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30503"): %s' % (result,)

def test_SLA_30601():
    result = parse('SLA-30601')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30601"): %s' % (result,)

def test_SLA_30602():
    result = parse('SLA-30602')
    assert result.__class__ in (Gene, Allele, AlleleWithoutGene), \
                                'Unexpected type for parse("SLA-30602"): %s' % (result,)
