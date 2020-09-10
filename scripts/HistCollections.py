import ROOT
from ROOT import TLorentzVector
import math
from array import array

class DelphesEvent:
    def __init__(self, event):
        self.event=event
        for e in event.Event:
            self.weight=e.Weight
            break # only one event

        #self.met=TLorentzVector()
        for met in event.MissingET:
            self.met= met.P4()
            break # only one MET

        #self.leptons=[]
        self.elecs=[]
        for e in event.Electron:
            if e.PT>25 and abs(e.Eta)<2.5:
                self.elecs.append(e)
        self.muons=[]
        for m in event.Muon:
            if m.PT>25 and abs(m.Eta)<2.5:
                self.muons.append(m)

        self.jets=[]
        self.exclJets=[]
        self.tautags=[]
        self.btags=[]

        for j in event.Jet:
            if j.TauTag:
                self.tautags.append(j)
            if j.BTag and abs(j.Eta)<2.5:
                self.btags.append(j)
            if j.PT>25 and abs(j.Eta)<4.5:
                self.jets.append(j)
                if not (j.TauTag or j.BTag):
                    self.exclJets.append(j)

class Hists:
    def addbranch(self, bname, btype, blen=1, default=0):
        self.branches[bname] = array(btype,blen*[default])
        bnamemod=bname
        if blen>1:
            bnamemod="%s[%d]" % (bname,blen)
        self.tree.Branch(bname, self.branches[bname], '%s/%s' % (bnamemod,btype.upper()))
            

    def __init__(self, tag, topdir, detaillevel=99): 
        self.topdir=topdir
        self.hists={}
        self.tag=tag

        self.newdir=topdir.mkdir(tag)
        self.newdir.cd()

        self.detaillevel=detaillevel
        self.collections={}
    
        ### Make all the histograms here (!)

        ### Basics
        self.hists["nElec"]=ROOT.TH1F("h_"+tag+"_nElec",tag+"_nElec;Number of Electrons;Events",10,0,10)
        self.hists["nMuon"]=ROOT.TH1F("h_"+tag+"_nMuon",tag+"_nMuon;Number of Muons;Events",10,0,10)
        self.hists["nTau"]=ROOT.TH1F("h_"+tag+"_nTau",tag+"_nTau;Number of Taus;Events",10,0,10)
        self.hists["nbjet"]=ROOT.TH1F("h_"+tag+"_nbjets",tag+"_nbjets;Number of b-jets;Events",10,0,10)
        self.hists["njet"]=ROOT.TH1F("h_"+tag+"_njets",tag+"_njets;Number of jets;Events",10,0,10)
        self.hists["nLep"]=ROOT.TH1F("h_"+tag+"_nLep",tag+"_nLep;Number of Leptons (e/#mu);Events",10,0,10)

        ### B-jets
        self.hists["bPT"]=ROOT.TH1F("h_"+tag+"_bPT",tag+"_bPT;p_{T,b-jets};Events/(10GeV)",50,0,500)
        self.hists["bPhi"]=ROOT.TH1F("h_"+tag+"_bPhi",tag+"_bPhi;#phi(b-jets);Events/(0.4)",20,-4,4)
        self.hists["bEta"]=ROOT.TH1F("h_"+tag+"_bEta",tag+"_bEta;#eta(b-jets);Events/(0.5)",20,-5,5)

        ### Jets
        self.hists["jPT"]=ROOT.TH1F("h_"+tag+"_jPT",tag+"_jPT;p_{T,jets};Events/(10GeV)",50,0,500)
        self.hists["jPhi"]=ROOT.TH1F("h_"+tag+"_jPhi",tag+"_jPhi;#phi(jets);Events/(0.4)",20,-4,4)
        self.hists["jEta"]=ROOT.TH1F("h_"+tag+"_jEta",tag+"_jEta;#eta(jets);Events/(0.5)",20,-5,5)
        self.hists["mjj"]=ROOT.TH1F("h_"+tag+"_mjj",tag+"_mjj;m(jj);Events/(100 GeV)",100,0,10000)

        ### Electrons
        self.hists["ePT"]=ROOT.TH1F("h_"+tag+"_ePT",tag+"_ePT;p^{e}_{T};Events/(10GeV)",50,0,500)
        self.hists["ePhi"]=ROOT.TH1F("h_"+tag+"_ePhi",tag+"_ePhi;#phi(elecs);Events/(0.4)",20,-4,4)
        self.hists["eEta"]=ROOT.TH1F("h_"+tag+"_eEta",tag+"_eEta;#eta(elecs);Events/(0.5)",20,-5,5)
        self.hists["lePT"]=ROOT.TH1F("h_"+tag+"_lePT",tag+"_lePT;p^{lead-e}_{T};Events/(10GeV)",50,0,500)
        self.hists["lePhi"]=ROOT.TH1F("h_"+tag+"_lePhi",tag+"_lePhi;#phi(leading-e);Events/(0.4)",20,-4,4)
        self.hists["leEta"]=ROOT.TH1F("h_"+tag+"_leEta",tag+"_leEta;#eta(leading-e);Events/(0.5)",20,-5,5)

        ### Muons
        self.hists["mPT"]=ROOT.TH1F("h_"+tag+"_mPT",tag+"_mPT;p^{#mu}_{T};Events/(10GeV)",50,0,500)
        self.hists["mPhi"]=ROOT.TH1F("h_"+tag+"_mPhi",tag+"_mPhi;#phi(muons);Events/(0.4)",20,-4,4)
        self.hists["mEta"]=ROOT.TH1F("h_"+tag+"_mEta",tag+"_mEta;#eta(muons);Events/(0.5)",20,-5,5)
        self.hists["lmPT"]=ROOT.TH1F("h_"+tag+"_lmPT",tag+"_lmPT;p^{lead-#mu}_{T};Events/(10GeV)",50,0,500)
        self.hists["lmPhi"]=ROOT.TH1F("h_"+tag+"_lmPhi",tag+"_lmPhi;#phi(leading-#mu);Events/(0.4)",20,-4,4)
        self.hists["lmEta"]=ROOT.TH1F("h_"+tag+"_lmEta",tag+"_lmEta;#eta(leading-#mu);Events/(0.5)",20,-5,5)

        ### Taus
        self.hists["tPT"] =ROOT.TH1F("h_"+tag+"_tPT" ,tag+"_tPT;p^{#tau}_{T};Events/(10GeV)",50,0,500)
        self.hists["tPhi"]=ROOT.TH1F("h_"+tag+"_tPhi",tag+"_tPhi;#phi(taus);Events/(0.4)",20,-4,4)
        self.hists["tEta"]=ROOT.TH1F("h_"+tag+"_tEta",tag+"_tEta;#eta(taus);Events/(0.5)",20,-5,5)
        self.hists["ltPT"] =ROOT.TH1F("h_"+tag+"_ltPT",tag+"_ltPT;p^{lead-#tau}_{T};Events/(10GeV)",50,0,500)
        self.hists["ltPhi"]=ROOT.TH1F("h_"+tag+"_ltPhi",tag+"_ltPhi;#phi(leading-#tau);Events/(0.4)",20,-4,4)
        self.hists["ltEta"]=ROOT.TH1F("h_"+tag+"_ltEta",tag+"_ltEta;#eta(leading-#tau);Events/(0.5)",20,-5,5)

        ### MET
        self.hists["MET"]        =ROOT.TH1F("h_"+tag+"_MET", tag+"_MET;E_{T}^{miss} [GeV];Events/(10 GeV)",100,0,1000)
        self.hists["MET_invismu"]=ROOT.TH1F("h_"+tag+"_MET_invismu", tag+"_MET;E_{T}^{miss} [GeV];Events/(10 GeV)",100,0,1000)

        for i,j in self.hists.iteritems():
            j.Sumw2()

        self.branches={}
        self.tree = ROOT.TTree("hftree","hftree")
        self.addbranch("MET", 'f')
        self.addbranch("METPhi", 'f')
        self.addbranch("MET_invismu", 'f')
        self.addbranch("METPhi_invismu", 'f')
        
        self.addbranch("nElec",'i')
        self.addbranch("nMuon",'i')
        self.addbranch("nTau",'i')
        self.addbranch("nbjet",'i')
        self.addbranch("njet",'i')
        self.addbranch("nLep",'i')

        self.addbranch("lep1PT", 'f')
        self.addbranch("lep1Eta", 'f')
        self.addbranch("lep1Phi", 'f')

        self.addbranch("tau1PT", 'f')
        self.addbranch("tau1Eta", 'f')
        self.addbranch("tau1Phi", 'f')

        self.addbranch("j1PT", 'f')
        self.addbranch("j1Eta", 'f')
        self.addbranch("j1Phi", 'f')
        self.addbranch("j2PT", 'f')
        self.addbranch("j2Eta", 'f')
        self.addbranch("j2Phi", 'f')
        self.addbranch("mjj", 'f')

        self.addbranch("bj1PT", 'f')
        self.addbranch("bj1Eta", 'f')
        self.addbranch("bj1Phi", 'f')
        self.addbranch("bj2PT", 'f')
        self.addbranch("bj2Eta", 'f')
        self.addbranch("bj2Phi", 'f')

        self.addbranch("weight",'f')
        

    def write(self,):
        self.newdir.cd()
        for i,k in self.hists.iteritems():
            k.Write()
        for i,k in self.collections.iteritems():
            k.write()
        self.tree.Write()
        self.topdir.cd()

    def add(self,coll):
        for i,k in self.hists.iteritems():
            if i in coll.hists: k.Add(coll.hists[i])
        for i,k in self.collections.iteritems():
            if i in coll.collections: k.add(coll.collections[i])
    
    def fill(self,event,weight=0):
        
        defaultfill=-999

        for i,k in self.collections.iteritems():
            k.fill(event,weight)

        self.branches["weight"][0] = weight
            
        ### Do some characterizations
        leadingLep = 0
        if ( len(event.elecs) > 0 and len(event.muons) == 0 ):
            leadingLep = event.elecs[0].P4()
        elif ( len(event.elecs) == 0 and len(event.muons) > 0 ):
            leadingLep = event.muons[0].P4()
        elif ( len(event.elecs) > 0 and len(event.muons) > 0 ):
            if ( event.elecs[0].PT > event.muons[0].PT ):
                leadingLep = event.elecs[0].P4()
            else:
                leadingLep = event.muons[0].P4()

        muonsmomentum=ROOT.TLorentzVector()
        muonsmomentum.SetPtEtaPhiM(0,0,0,0)
        for m in event.muons:
            muonsmomentum+=m.P4()
                
        ### Fill generic hists
        self.hists["nElec"].Fill(len(event.elecs),weight)
        self.hists["nMuon"].Fill(len(event.muons),weight)
        self.hists["nTau"].Fill(len(event.tautags),weight)
        self.hists["nbjet"].Fill(len(event.btags),weight)
        self.hists["njet"].Fill(len(event.jets),weight)
        self.hists["nLep"].Fill(len(event.elecs)+len(event.muons),weight)
        self.hists["MET"].Fill(event.met.Pt(),weight)
        self.hists["MET_invismu"].Fill((event.met+muonsmomentum).Pt(),weight)

        self.branches["MET"][0] = event.met.Pt()
        self.branches["METPhi"][0]=event.met.Phi()
        self.branches["MET_invismu"][0] = (event.met+muonsmomentum).Pt()
        self.branches["METPhi_invismu"][0]=(event.met+muonsmomentum).Phi()
        self.branches["nElec"][0] = len(event.elecs)
        self.branches["nMuon"][0] = len(event.muons)
        self.branches["nTau"][0] = len(event.tautags)
        self.branches["nbjet"][0] = len(event.btags)
        self.branches["njet"][0] = len(event.jets)
        self.branches["nLep"][0] = len(event.elecs)+len(event.muons)
        
        ### B-jets
        for aBJet in event.btags:
            self.hists["bPT"].Fill(aBJet.PT,weight)
            self.hists["bEta"].Fill(aBJet.Eta,weight)
            self.hists["bPhi"].Fill(aBJet.Phi,weight)

        ### Jets
        for aJet in event.exclJets:
            self.hists["jPT"].Fill(aJet.PT,weight)
            self.hists["jEta"].Fill(aJet.Eta,weight)
            self.hists["jPhi"].Fill(aJet.Phi,weight)
        if len(event.exclJets) > 1:
            mjj = (event.exclJets[0].P4() + event.exclJets[1].P4()).M()
            self.hists["mjj"].Fill( mjj, weight )
            self.branches["mjj"][0] = mjj
        ### Electrons
        for aElec in event.elecs:
            self.hists["ePT"].Fill(aElec.PT,weight)
            self.hists["eEta"].Fill(aElec.Eta,weight)
            self.hists["ePhi"].Fill(aElec.Phi,weight)
        if len(event.elecs)>0:
            self.hists["lePT"].Fill(event.elecs[0].PT,weight)
            self.hists["leEta"].Fill(event.elecs[0].Eta,weight)
            self.hists["lePhi"].Fill(event.elecs[0].Phi,weight)

        ### Muons
        for aMuon in event.muons:
            self.hists["mPT"].Fill(aMuon.PT,weight)
            self.hists["mEta"].Fill(aMuon.Eta,weight)
            self.hists["mPhi"].Fill(aMuon.Phi,weight)
        if len(event.muons)>0:
            self.hists["lmPT"].Fill(event.muons[0].PT,weight)
            self.hists["lmEta"].Fill(event.muons[0].Eta,weight)
            self.hists["lmPhi"].Fill(event.muons[0].Phi,weight)

        ### Taus
        for aTau in event.tautags:
            self.hists["tPT"].Fill(aTau.PT,weight)
            self.hists["tEta"].Fill(aTau.Eta,weight)
            self.hists["tPhi"].Fill(aTau.Phi,weight)
        if len(event.tautags)>0:
            self.hists["ltPT"].Fill(event.tautags[0].PT,weight)
            self.hists["ltEta"].Fill(event.tautags[0].Eta,weight)
            self.hists["ltPhi"].Fill(event.tautags[0].Phi,weight)
            self.branches["tau1PT"][0]=event.tautags[0].PT
            self.branches["tau1Eta"][0]=event.tautags[0].Eta
            self.branches["tau1Phi"][0]=event.tautags[0].Phi
        else:
            self.branches["tau1PT"][0]=defaultfill
            self.branches["tau1Eta"][0]=defaultfill
            self.branches["tau1Phi"][0]=defaultfill

        ### b-jets
        if len(event.btags) > 0:
            self.branches["bj1PT"][0]=event.btags[0].P4().Pt()
            self.branches["bj1Eta"][0]=event.btags[0].P4().Eta()
            self.branches["bj1Phi"][0]=event.btags[0].P4().Phi()
        else:
            self.branches["bj1PT"][0]=defaultfill
            self.branches["bj1Eta"][0]=defaultfill
            self.branches["bj1Phi"][0]=defaultfill
        if len(event.btags) > 1:
            self.branches["bj2PT"][0]=event.btags[1].P4().Pt()
            self.branches["bj2Eta"][0]=event.btags[1].P4().Eta()
            self.branches["bj2Phi"][0]=event.btags[1].P4().Phi()
        else:
            self.branches["bj2PT"][0]=defaultfill
            self.branches["bj2Eta"][0]=defaultfill
            self.branches["bj2Phi"][0]=defaultfill

        ### non-b/tau-jets
        if len(event.exclJets) > 0:
            self.branches["j1PT"][0]=event.exclJets[0].P4().Pt()
            self.branches["j1Eta"][0]=event.exclJets[0].P4().Eta()
            self.branches["j1Phi"][0]=event.exclJets[0].P4().Phi()
        else:
            self.branches["j1PT"][0]=defaultfill
            self.branches["j1Eta"][0]=defaultfill
            self.branches["j1Phi"][0]=defaultfill
        if len(event.exclJets) > 1:
            self.branches["j2PT"][0]=event.exclJets[1].P4().Pt()
            self.branches["j2Eta"][0]=event.exclJets[1].P4().Eta()
            self.branches["j2Phi"][0]=event.exclJets[1].P4().Phi()
        else:
            self.branches["j2PT"][0]=defaultfill
            self.branches["j2Eta"][0]=defaultfill
            self.branches["j2Phi"][0]=defaultfill

        ### Leptons
        if leadingLep:
            self.branches["lep1PT"][0] = leadingLep.Pt()
            self.branches["lep1Eta"][0] = leadingLep.Eta()
            self.branches["lep1Phi"][0] = leadingLep.Phi()
        else:
            self.branches["lep1PT"][0] = defaultfill
            self.branches["lep1Eta"][0] = defaultfill
            self.branches["lep1Phi"][0] = defaultfill


        self.tree.Fill()

#=====================================================================
        

#======================================================================
#
class HistCollection:
    def __init__(self, tag, topdir, detaillevel=99): 
        self.topdir=topdir
        self.tag=tag

        self.newdir=topdir.mkdir(tag)

        self.detaillevel=detaillevel

        self.newdir.cd()

        self.collections={}
        
        self.topdir.cd()
        
    def write(self):
        self.newdir.cd()
        for i,k in self.collections.iteritems():
            k.write()
        self.topdir.cd()
    
    def addcollection(self,tag):
        self.newdir.cd()
        self.collections[tag]=Hists(self.tag+"_"+tag,self.newdir,self.detaillevel)
        self.topdir.cd()

    def add(self,coll):
        for i,k in self.collections.iteritems():
            if i in coll: k.add(coll[i])

    def fill(self,event,weight=0):
        for i,k in self.collections.iteritems():
            k.fill(event,weight)

    def fill(self,event,tag,weight=0):
        for i,k in self.collections.iteritems():
            if i==tag:
                k.fill(event,weight)
                break


class JetBins:
    def __init__(self, tag, topdir, detaillevel=99): 
        self.topdir=topdir
        self.tag=tag
        
        self.newdir=topdir.mkdir(tag)
        self.newdir.cd()

        self.njets=(0,1,2,3,4,5,6)

        self.collections={}
        self.collections["njets"]=HistCollection("njets",self.newdir, detaillevel)
        self.collections["njets"].addcollection("inclusive")
        for i in self.njets:
            self.collections["njets"].addcollection(str(i))

        self.topdir.cd()
        
    def write(self):
        self.newdir.cd()

        # fill the inclusive hist collections here by adding the constituents, should be faster
        # than doing it in 'fill'
        for i,k in self.collections["njets"].collections.iteritems():
           if k.tag=="njets_inclusive": continue
           else:
               self.collections["njets"].collections["inclusive"].add(k)
            
        for i,k in self.collections.iteritems():
            k.write()
        self.topdir.cd()
    
    def addcollection(self,tag):
        self.newdir.cd()
        self.collections[tag]=Hists(self.tag+"_"+tag,self.topdir,False)
        self.topdir.cd()


    def add(self,coll):
        for i,k in self.collections.iteritems():
            if i in coll: k.add(coll[i])

    def fill(self,event,weight=0):
        njets=0
        for j in event.event.Jet:
            if j.PT>25 and abs(j.Eta)<4.5:
                njets+=1
        #print "filling jet bin with njets=%d" % (event.njets())
        # HAZ: Make the last jet bin an overflow
        if njets > max(self.njets):  njets = max(self.njets)
        self.collections["njets"].fill(event,str(njets),weight)
        # binned results
        # for thresh_i in xrange(len(self.njets)):
        #     if (((thresh_i < len(self.njets)-1) and 
        #          njets>=self.njets[thresh_i] and 
        #          njets<self.njets[thresh_i+1]) or 
        #         ((thresh_i == len(self.njets)-1) and 
        #          njets>=self.njets[thresh_i])):
        #         self.collections["njets"].fill(event,str(self.njets[thresh_i]))
        #         break

#======================================================================
