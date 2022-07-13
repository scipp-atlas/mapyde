from __future__ import annotations

from array import array

import ROOT


class DelphesEvent:
    def __init__(self, event, highlumi=False):
        self.event = event
        for e in event.Event:
            self.weight = e.Weight
            break  # only one event

        self.leptons = []
        self.elecs = []
        for e in event.Electron:
            if e.PT > 25 and abs(e.Eta) < 2.5:
                self.elecs.append(e)
                self.leptons.append(e)
        self.muons = []
        for m in event.Muon:
            if m.PT > 25 and abs(m.Eta) < 2.5:
                self.muons.append(m)
                self.leptons.append(m)

        self.sortedleptons = sorted(self.leptons, key=lambda lep: lep.PT, reverse=True)

        # self.met=TLorentzVector()
        for met in event.MissingET:
            self.met = met.P4()
            # correct MET for muons
            for m in event.Muon:
                self.met -= m.P4()
            break  # only one MET

        self.jets = []
        self.exclJets = []
        self.tautags = []
        self.btags = []

        self.btageta = 2.5 if not highlumi else 4.0

        for j in event.Jet:
            if j.TauTag:
                self.tautags.append(j)
            if j.BTag and abs(j.Eta) < self.btageta:
                self.btags.append(j)
            if j.PT > 25 and abs(j.Eta) < 4.5:
                self.jets.append(j)
                if not (j.TauTag or j.BTag):
                    self.exclJets.append(j)

        self.sortedjets = sorted(self.jets, key=lambda jet: jet.PT, reverse=True)


class Hists:
    def addbranch(self, bname, btype, blen=1, default=0):
        self.branches[bname] = array(btype, blen * [default])
        bnamemod = bname
        if blen > 1:
            bnamemod = "%s[%d]" % (bname, blen)
        self.tree.Branch(bname, self.branches[bname], f"{bnamemod}/{btype.upper()}")

    def __init__(self, tag, topdir, detaillevel=99):
        self.topdir = topdir
        self.hists = {}
        self.tag = tag

        self.newdir = topdir.mkdir(tag)
        self.newdir.cd()

        self.detaillevel = detaillevel
        self.collections = {}

        # Make all the histograms here (!)

        # Basics
        self.hists["nElec"] = ROOT.TH1F(
            "h_" + tag + "_nElec", tag + "_nElec;Number of Electrons;Events", 10, 0, 10
        )
        self.hists["nMuon"] = ROOT.TH1F(
            "h_" + tag + "_nMuon", tag + "_nMuon;Number of Muons;Events", 10, 0, 10
        )
        self.hists["nTau"] = ROOT.TH1F(
            "h_" + tag + "_nTau", tag + "_nTau;Number of Taus;Events", 10, 0, 10
        )
        self.hists["nbjet"] = ROOT.TH1F(
            "h_" + tag + "_nbjets", tag + "_nbjets;Number of b-jets;Events", 10, 0, 10
        )
        self.hists["njet"] = ROOT.TH1F(
            "h_" + tag + "_njets", tag + "_njets;Number of jets;Events", 10, 0, 10
        )
        self.hists["nLep"] = ROOT.TH1F(
            "h_" + tag + "_nLep",
            tag + "_nLep;Number of Leptons (e/#mu);Events",
            10,
            0,
            10,
        )

        # B-jets
        self.hists["bPT"] = ROOT.TH1F(
            "h_" + tag + "_bPT", tag + "_bPT;p_{T,b-jets};Events/(10GeV)", 50, 0, 500
        )
        self.hists["bPhi"] = ROOT.TH1F(
            "h_" + tag + "_bPhi", tag + "_bPhi;#phi(b-jets);Events/(0.4)", 20, -4, 4
        )
        self.hists["bEta"] = ROOT.TH1F(
            "h_" + tag + "_bEta", tag + "_bEta;#eta(b-jets);Events/(0.5)", 20, -5, 5
        )

        # Jets
        self.hists["jPT"] = ROOT.TH1F(
            "h_" + tag + "_jPT", tag + "_jPT;p_{T,jets};Events/(10GeV)", 50, 0, 500
        )
        self.hists["jPhi"] = ROOT.TH1F(
            "h_" + tag + "_jPhi", tag + "_jPhi;#phi(jets);Events/(0.4)", 20, -4, 4
        )
        self.hists["jEta"] = ROOT.TH1F(
            "h_" + tag + "_jEta", tag + "_jEta;#eta(jets);Events/(0.5)", 20, -5, 5
        )
        self.hists["mjj"] = ROOT.TH1F(
            "h_" + tag + "_mjj", tag + "_mjj;m(jj);Events/(100 GeV)", 100, 0, 10000
        )

        # Electrons
        self.hists["ePT"] = ROOT.TH1F(
            "h_" + tag + "_ePT", tag + "_ePT;p^{e}_{T};Events/(10GeV)", 50, 0, 500
        )
        self.hists["ePhi"] = ROOT.TH1F(
            "h_" + tag + "_ePhi", tag + "_ePhi;#phi(elecs);Events/(0.4)", 20, -4, 4
        )
        self.hists["eEta"] = ROOT.TH1F(
            "h_" + tag + "_eEta", tag + "_eEta;#eta(elecs);Events/(0.5)", 20, -5, 5
        )
        self.hists["lePT"] = ROOT.TH1F(
            "h_" + tag + "_lePT",
            tag + "_lePT;p^{lead-e}_{T};Events/(10GeV)",
            50,
            0,
            500,
        )
        self.hists["lePhi"] = ROOT.TH1F(
            "h_" + tag + "_lePhi",
            tag + "_lePhi;#phi(leading-e);Events/(0.4)",
            20,
            -4,
            4,
        )
        self.hists["leEta"] = ROOT.TH1F(
            "h_" + tag + "_leEta",
            tag + "_leEta;#eta(leading-e);Events/(0.5)",
            20,
            -5,
            5,
        )

        # Muons
        self.hists["mPT"] = ROOT.TH1F(
            "h_" + tag + "_mPT", tag + "_mPT;p^{#mu}_{T};Events/(10GeV)", 50, 0, 500
        )
        self.hists["mPhi"] = ROOT.TH1F(
            "h_" + tag + "_mPhi", tag + "_mPhi;#phi(muons);Events/(0.4)", 20, -4, 4
        )
        self.hists["mEta"] = ROOT.TH1F(
            "h_" + tag + "_mEta", tag + "_mEta;#eta(muons);Events/(0.5)", 20, -5, 5
        )
        self.hists["lmPT"] = ROOT.TH1F(
            "h_" + tag + "_lmPT",
            tag + "_lmPT;p^{lead-#mu}_{T};Events/(10GeV)",
            50,
            0,
            500,
        )
        self.hists["lmPhi"] = ROOT.TH1F(
            "h_" + tag + "_lmPhi",
            tag + "_lmPhi;#phi(leading-#mu);Events/(0.4)",
            20,
            -4,
            4,
        )
        self.hists["lmEta"] = ROOT.TH1F(
            "h_" + tag + "_lmEta",
            tag + "_lmEta;#eta(leading-#mu);Events/(0.5)",
            20,
            -5,
            5,
        )

        # Taus
        self.hists["tPT"] = ROOT.TH1F(
            "h_" + tag + "_tPT", tag + "_tPT;p^{#tau}_{T};Events/(10GeV)", 50, 0, 500
        )
        self.hists["tPhi"] = ROOT.TH1F(
            "h_" + tag + "_tPhi", tag + "_tPhi;#phi(taus);Events/(0.4)", 20, -4, 4
        )
        self.hists["tEta"] = ROOT.TH1F(
            "h_" + tag + "_tEta", tag + "_tEta;#eta(taus);Events/(0.5)", 20, -5, 5
        )
        self.hists["ltPT"] = ROOT.TH1F(
            "h_" + tag + "_ltPT",
            tag + "_ltPT;p^{lead-#tau}_{T};Events/(10GeV)",
            50,
            0,
            500,
        )
        self.hists["ltPhi"] = ROOT.TH1F(
            "h_" + tag + "_ltPhi",
            tag + "_ltPhi;#phi(leading-#tau);Events/(0.4)",
            20,
            -4,
            4,
        )
        self.hists["ltEta"] = ROOT.TH1F(
            "h_" + tag + "_ltEta",
            tag + "_ltEta;#eta(leading-#tau);Events/(0.5)",
            20,
            -5,
            5,
        )

        # MET
        self.hists["MET"] = ROOT.TH1F(
            "h_" + tag + "_MET",
            tag + "_MET;E_{T}^{miss} [GeV];Events/(10 GeV)",
            100,
            0,
            1000,
        )
        self.hists["MET_invismu"] = ROOT.TH1F(
            "h_" + tag + "_MET_invismu",
            tag + "_MET;E_{T}^{miss} [GeV];Events/(10 GeV)",
            100,
            0,
            1000,
        )

        for _, j in self.hists.items():
            j.Sumw2()

        self.branches = {}
        self.tree = ROOT.TTree("hftree", "hftree")
        self.addbranch("MET", "f")
        self.addbranch("METPhi", "f")
        self.addbranch("MET_invismu", "f")
        self.addbranch("METPhi_invismu", "f")

        self.addbranch("nElec", "i")
        self.addbranch("nMuon", "i")
        self.addbranch("nTau", "i")
        self.addbranch("nbjet", "i")
        self.addbranch("njet", "i")
        self.addbranch("nLep", "i")

        self.addbranch("lep1PT", "f")
        self.addbranch("lep1Eta", "f")
        self.addbranch("lep1Phi", "f")

        self.addbranch("lep2PT", "f")
        self.addbranch("lep2Eta", "f")
        self.addbranch("lep2Phi", "f")

        self.addbranch("lep3PT", "f")
        self.addbranch("lep3Eta", "f")
        self.addbranch("lep3Phi", "f")

        self.addbranch("tau1PT", "f")
        self.addbranch("tau1Eta", "f")
        self.addbranch("tau1Phi", "f")

        self.addbranch("j1PT", "f")
        self.addbranch("j1Eta", "f")
        self.addbranch("j1Phi", "f")
        self.addbranch("j2PT", "f")
        self.addbranch("j2Eta", "f")
        self.addbranch("j2Phi", "f")
        self.addbranch("mjj", "f")

        self.addbranch("bj1PT", "f")
        self.addbranch("bj1Eta", "f")
        self.addbranch("bj1Phi", "f")
        self.addbranch("bj2PT", "f")
        self.addbranch("bj2Eta", "f")
        self.addbranch("bj2Phi", "f")

        self.addbranch("weight", "f")

    def write(
        self,
    ):
        self.newdir.cd()
        for _, k in self.hists.items():
            k.Write()
        for _, k in self.collections.items():
            k.write()
        self.tree.Write()
        self.topdir.cd()

    def add(self, coll):
        for i, k in self.hists.items():
            if i in coll.hists:
                k.Add(coll.hists[i])
        for i, k in self.collections.items():
            if i in coll.collections:
                k.add(coll.collections[i])

    def fill(self, event, weight=0):

        defaultfill = -9

        for _, k in self.collections.items():
            k.fill(event, weight)

        self.branches["weight"][0] = weight

        # Do some characterizations
        leadingLep = (
            event.sortedleptons[0].P4() if len(event.sortedleptons) > 0 else None
        )

        subleadingLep = (
            event.sortedleptons[1].P4() if len(event.sortedleptons) > 1 else None
        )

        subsubleadingLep = (
            event.sortedleptons[2].P4() if len(event.sortedleptons) > 2 else None
        )

        muonsmomentum = ROOT.TLorentzVector()
        muonsmomentum.SetPtEtaPhiM(0, 0, 0, 0)
        for m in event.muons:
            muonsmomentum += m.P4()

        # Fill generic hists
        self.hists["nElec"].Fill(len(event.elecs), weight)
        self.hists["nMuon"].Fill(len(event.muons), weight)
        self.hists["nTau"].Fill(len(event.tautags), weight)
        self.hists["nbjet"].Fill(len(event.btags), weight)
        self.hists["njet"].Fill(len(event.jets), weight)
        self.hists["nLep"].Fill(len(event.elecs) + len(event.muons), weight)
        self.hists["MET"].Fill(event.met.Pt(), weight)
        self.hists["MET_invismu"].Fill((event.met + muonsmomentum).Pt(), weight)

        self.branches["MET"][0] = event.met.Pt()
        self.branches["METPhi"][0] = event.met.Phi()
        self.branches["MET_invismu"][0] = (event.met + muonsmomentum).Pt()
        self.branches["METPhi_invismu"][0] = (event.met + muonsmomentum).Phi()
        self.branches["nElec"][0] = len(event.elecs)
        self.branches["nMuon"][0] = len(event.muons)
        self.branches["nTau"][0] = len(event.tautags)
        self.branches["nbjet"][0] = len(event.btags)
        self.branches["njet"][0] = len(event.jets)
        self.branches["nLep"][0] = len(event.elecs) + len(event.muons)

        # B-jets
        for aBJet in event.btags:
            self.hists["bPT"].Fill(aBJet.PT, weight)
            self.hists["bEta"].Fill(aBJet.Eta, weight)
            self.hists["bPhi"].Fill(aBJet.Phi, weight)

        # Jets
        for aJet in event.exclJets:
            self.hists["jPT"].Fill(aJet.PT, weight)
            self.hists["jEta"].Fill(aJet.Eta, weight)
            self.hists["jPhi"].Fill(aJet.Phi, weight)
        if len(event.exclJets) > 1:
            mjj = (event.exclJets[0].P4() + event.exclJets[1].P4()).M()
            self.hists["mjj"].Fill(mjj, weight)
            self.branches["mjj"][0] = mjj
        # Electrons
        for aElec in event.elecs:
            self.hists["ePT"].Fill(aElec.PT, weight)
            self.hists["eEta"].Fill(aElec.Eta, weight)
            self.hists["ePhi"].Fill(aElec.Phi, weight)
        if len(event.elecs) > 0:
            self.hists["lePT"].Fill(event.elecs[0].PT, weight)
            self.hists["leEta"].Fill(event.elecs[0].Eta, weight)
            self.hists["lePhi"].Fill(event.elecs[0].Phi, weight)

        # Muons
        for aMuon in event.muons:
            self.hists["mPT"].Fill(aMuon.PT, weight)
            self.hists["mEta"].Fill(aMuon.Eta, weight)
            self.hists["mPhi"].Fill(aMuon.Phi, weight)
        if len(event.muons) > 0:
            self.hists["lmPT"].Fill(event.muons[0].PT, weight)
            self.hists["lmEta"].Fill(event.muons[0].Eta, weight)
            self.hists["lmPhi"].Fill(event.muons[0].Phi, weight)

        # Taus
        for aTau in event.tautags:
            self.hists["tPT"].Fill(aTau.PT, weight)
            self.hists["tEta"].Fill(aTau.Eta, weight)
            self.hists["tPhi"].Fill(aTau.Phi, weight)
        if len(event.tautags) > 0:
            self.hists["ltPT"].Fill(event.tautags[0].PT, weight)
            self.hists["ltEta"].Fill(event.tautags[0].Eta, weight)
            self.hists["ltPhi"].Fill(event.tautags[0].Phi, weight)
            self.branches["tau1PT"][0] = event.tautags[0].PT
            self.branches["tau1Eta"][0] = event.tautags[0].Eta
            self.branches["tau1Phi"][0] = event.tautags[0].Phi
        else:
            self.branches["tau1PT"][0] = defaultfill
            self.branches["tau1Eta"][0] = defaultfill
            self.branches["tau1Phi"][0] = defaultfill

        # b-jets
        if len(event.btags) > 0:
            self.branches["bj1PT"][0] = event.btags[0].P4().Pt()
            self.branches["bj1Eta"][0] = event.btags[0].P4().Eta()
            self.branches["bj1Phi"][0] = event.btags[0].P4().Phi()
        else:
            self.branches["bj1PT"][0] = defaultfill
            self.branches["bj1Eta"][0] = defaultfill
            self.branches["bj1Phi"][0] = defaultfill
        if len(event.btags) > 1:
            self.branches["bj2PT"][0] = event.btags[1].P4().Pt()
            self.branches["bj2Eta"][0] = event.btags[1].P4().Eta()
            self.branches["bj2Phi"][0] = event.btags[1].P4().Phi()
        else:
            self.branches["bj2PT"][0] = defaultfill
            self.branches["bj2Eta"][0] = defaultfill
            self.branches["bj2Phi"][0] = defaultfill

        # non-b/tau-jets
        if len(event.exclJets) > 0:
            self.branches["j1PT"][0] = event.exclJets[0].P4().Pt()
            self.branches["j1Eta"][0] = event.exclJets[0].P4().Eta()
            self.branches["j1Phi"][0] = event.exclJets[0].P4().Phi()
        else:
            self.branches["j1PT"][0] = defaultfill
            self.branches["j1Eta"][0] = defaultfill
            self.branches["j1Phi"][0] = defaultfill
        if len(event.exclJets) > 1:
            self.branches["j2PT"][0] = event.exclJets[1].P4().Pt()
            self.branches["j2Eta"][0] = event.exclJets[1].P4().Eta()
            self.branches["j2Phi"][0] = event.exclJets[1].P4().Phi()
        else:
            self.branches["j2PT"][0] = defaultfill
            self.branches["j2Eta"][0] = defaultfill
            self.branches["j2Phi"][0] = defaultfill

        # Leptons
        if leadingLep:
            self.branches["lep1PT"][0] = leadingLep.Pt()
            self.branches["lep1Eta"][0] = leadingLep.Eta()
            self.branches["lep1Phi"][0] = leadingLep.Phi()
        else:
            self.branches["lep1PT"][0] = defaultfill
            self.branches["lep1Eta"][0] = defaultfill
            self.branches["lep1Phi"][0] = defaultfill

        if subleadingLep:
            self.branches["lep2PT"][0] = subleadingLep.Pt()
            self.branches["lep2Eta"][0] = subleadingLep.Eta()
            self.branches["lep2Phi"][0] = subleadingLep.Phi()
        else:
            self.branches["lep2PT"][0] = defaultfill
            self.branches["lep2Eta"][0] = defaultfill
            self.branches["lep2Phi"][0] = defaultfill

        if subsubleadingLep:
            self.branches["lep3PT"][0] = subsubleadingLep.Pt()
            self.branches["lep3Eta"][0] = subsubleadingLep.Eta()
            self.branches["lep3Phi"][0] = subsubleadingLep.Phi()
        else:
            self.branches["lep3PT"][0] = defaultfill
            self.branches["lep3Eta"][0] = defaultfill
            self.branches["lep3Phi"][0] = defaultfill

        self.tree.Fill()


# =====================================================================


# =====================================================================
class tthhTree:
    def addbranch(self, bname, btype, blen=1, default=0):
        self.branches[bname] = array(btype, blen * [default])
        bnamemod = bname
        if blen > 1:
            bnamemod = "%s[%d]" % (bname, blen)
        self.tree.Branch(bname, self.branches[bname], f"{bnamemod}/{btype.upper()}")

    def __init__(self, tag, topdir, detaillevel=99):
        self.topdir = topdir
        self.hists = {}
        self.tag = tag

        self.newdir = topdir.mkdir(tag)
        self.newdir.cd()

        self.detaillevel = detaillevel
        self.collections = {}

        self.branches = {}
        self.tree = ROOT.TTree("hftree", "hftree")
        for i in (
            "numlep",
            "numjet",
            "btag",
            "srap",
            "cent",
            "m_bb",
            "h_b",
            "chi",
            "met",
            "metphi",
            "weight",
        ):
            self.addbranch(i, "f")

        self.maxleptons = 4
        for j in range(1, self.maxleptons):
            for i in ("pT", "eta", "phi"):
                self.addbranch("lepton%d%s" % (j, i), "f")
            for i in ("mt", "dr"):
                self.addbranch("%s%d" % (i, j), "f")

        self.maxjets = 12
        for j in range(1, self.maxjets):
            for i in ("pT", "eta", "phi", "b"):
                self.addbranch("jet%d%s" % (j, i), "f")

    def write(
        self,
    ):
        self.newdir.cd()
        for _, k in self.hists.items():
            k.Write()
        for _, k in self.collections.items():
            k.write()
        self.tree.Write()
        self.topdir.cd()

    def add(self, coll):
        for i, k in self.hists.items():
            if i in coll.hists:
                k.Add(coll.hists[i])
        for i, k in self.collections.items():
            if i in coll.collections:
                k.add(coll.collections[i])

    def fill(self, event, weight=0):

        defaultfill = -9

        for _, k in self.collections.items():
            k.fill(event, weight)

        self.branches["weight"][0] = weight

        nbjets = len(event.btags)

        # Fill generic hists
        self.branches["met"][0] = event.met.Pt()
        self.branches["metphi"][0] = event.met.Phi()
        self.branches["numlep"][0] = len(event.sortedleptons)
        self.branches["btag"][0] = nbjets
        self.branches["numjet"][0] = len(event.jets)

        # Jets
        jetCount = 1
        cen_sum_E = 0
        cen_sum_Pt = 0
        for aJet in event.sortedjets:
            self.branches["jet%dpT" % jetCount][0] = aJet.PT
            self.branches["jet%deta" % jetCount][0] = aJet.Eta
            self.branches["jet%dphi" % jetCount][0] = aJet.Phi
            self.branches["jet%db" % jetCount][0] = (
                aJet.BTag and aJet.PT > 25 and abs(aJet.Eta) < event.btageta
            )

            # Centrality
            cen_sum_E += aJet.P4().E()
            cen_sum_Pt += aJet.PT

            jetCount = jetCount + 1
            if jetCount >= self.maxjets:
                break

        # fill in dummy values for "missing" jets
        for i in range(jetCount, self.maxjets):
            self.branches["jet%dpT" % i][0] = defaultfill
            self.branches["jet%deta" % i][0] = defaultfill
            self.branches["jet%dphi" % i][0] = defaultfill
            self.branches["jet%db" % i][0] = defaultfill

        # centrality
        if cen_sum_E > 0:
            self.branches["cent"][0] = cen_sum_Pt / cen_sum_E
        else:
            self.branches["cent"][0] = defaultfill

        # btagged jets separately
        HB_sum_Pt = 0
        etasum = 0
        btjmaxPt = 0
        btjmaxM = 0
        for aJet in event.btags:
            HB_sum_Pt += aJet.PT
            for bJet in event.btags:
                if aJet is bJet:
                    continue
                etasum += abs(aJet.Eta - bJet.Eta)
                vec_sum_Pt = (aJet.P4() + bJet.P4()).Pt()
                if vec_sum_Pt > btjmaxPt:
                    btjmaxPt = vec_sum_Pt
                    btjmaxM = (aJet.P4() + bJet.P4()).M()
        # srap
        etasum_N = defaultfill
        if nbjets > 1:
            etasum_N = etasum / (nbjets**2 - nbjets)
        self.branches["srap"][0] = etasum_N

        # mbb
        self.branches["m_bb"][0] = btjmaxM

        # H_b
        self.branches["h_b"][0] = HB_sum_Pt

        # chi^2
        chisq = [defaultfill]
        for i1 in range(0, nbjets):
            for i2 in range(i1 + 1, nbjets):
                for i3 in range(i2 + 1, nbjets):
                    for i4 in range(i3 + 1, nbjets):
                        chisq.append(
                            ((event.btags[i1].P4() + event.btags[i2].P4()).M() - 120.0)
                            ** 2
                            + (
                                (event.btags[i3].P4() + event.btags[i4].P4()).M()
                                - 120.0
                            )
                            ** 2
                        )
                        chisq.append(
                            ((event.btags[i1].P4() + event.btags[i3].P4()).M() - 120.0)
                            ** 2
                            + (
                                (event.btags[i2].P4() + event.btags[i4].P4()).M()
                                - 120.0
                            )
                            ** 2
                        )
                        chisq.append(
                            ((event.btags[i1].P4() + event.btags[i4].P4()).M() - 120.0)
                            ** 2
                            + (
                                (event.btags[i2].P4() + event.btags[i3].P4()).M()
                                - 120.0
                            )
                            ** 2
                        )
        self.branches["chi"][0] = min(chisq)

        # Leptons
        lepCount = 1
        for aLep in event.sortedleptons:
            self.branches["lepton%dpT" % lepCount][0] = aLep.PT
            self.branches["lepton%dpT" % lepCount][0] = aLep.Eta
            self.branches["lepton%dpT" % lepCount][0] = aLep.Phi
            self.branches["mt%d" % lepCount][0] = ROOT.TMath.Sqrt(
                2
                * event.met.Pt()
                * aLep.PT
                * (1 - ROOT.TMath.Cos(aLep.P4().DeltaPhi(event.met)))
            )
            mindr = 999
            for aJet in event.sortedjets:
                mindr = min(mindr, aLep.P4().DrEtaPhi(aJet.P4()))
            self.branches["dr%d" % lepCount][0] = mindr
            lepCount = lepCount + 1
            if lepCount >= self.maxleptons:
                break

        for i in range(lepCount, self.maxleptons):
            self.branches["lepton%dpT" % i][0] = defaultfill
            self.branches["lepton%dpT" % i][0] = defaultfill
            self.branches["lepton%dpT" % i][0] = defaultfill
            self.branches["mt%d" % i][0] = defaultfill
            self.branches["dr%d" % i][0] = defaultfill

        self.tree.Fill()


# =====================================================================


# =====================================================================
class lowlevelTree:
    def addbranch(self, bname, btype, blen=1, default=0):
        self.branches[bname] = array(btype, blen * [default])
        bnamemod = bname
        if blen > 1:
            bnamemod = "%s[%d]" % (bname, blen)
        self.tree.Branch(bname, self.branches[bname], f"{bnamemod}/{btype.upper()}")

    def __init__(self, tag, topdir, detaillevel=99):
        self.topdir = topdir
        self.hists = {}
        self.tag = tag

        self.newdir = topdir.mkdir(tag)
        self.newdir.cd()

        self.detaillevel = detaillevel
        self.collections = {}

        self.branches = {}
        self.tree = ROOT.TTree("lowleveltree", "lowleveltree")
        for i in ("numlepton", "numjet", "numbtagjet", "met", "metphi", "weight"):
            self.addbranch(i, "f")

        self.maxleptons = 4
        for j in range(1, self.maxleptons):
            for i in ("pT", "eta", "phi", "mT", "minjetdr"):
                self.addbranch("lepton%d%s" % (j, i), "f")

        self.maxjets = 12
        for j in range(1, self.maxjets):
            for i in ("pT", "eta", "phi", "b"):
                self.addbranch("jet%d%s" % (j, i), "f")

        # other objects: photons, taus, large-R jets.

    def write(
        self,
    ):
        self.newdir.cd()
        for _, k in self.hists.items():
            k.Write()
        for _, k in self.collections.items():
            k.write()
        self.tree.Write()
        self.topdir.cd()

    def add(self, coll):
        for i, k in self.hists.items():
            if i in coll.hists:
                k.Add(coll.hists[i])
        for i, k in self.collections.items():
            if i in coll.collections:
                k.add(coll.collections[i])

    def fill(self, event, weight=0):

        defaultfill = -9

        for _, k in self.collections.items():
            k.fill(event, weight)

        self.branches["weight"][0] = weight

        nbjets = len(event.btags)

        # Fill generic hists
        self.branches["met"][0] = event.met.Pt()
        self.branches["metphi"][0] = event.met.Phi()
        self.branches["numlepton"][0] = len(event.sortedleptons)
        self.branches["numbtagjet"][0] = nbjets
        self.branches["numjet"][0] = len(event.jets)

        # Jets
        jetCount = 1
        for aJet in event.sortedjets:
            self.branches["jet%dpT" % jetCount][0] = aJet.PT
            self.branches["jet%deta" % jetCount][0] = aJet.Eta
            self.branches["jet%dphi" % jetCount][0] = aJet.Phi
            self.branches["jet%db" % jetCount][0] = (
                aJet.BTag and aJet.PT > 25 and abs(aJet.Eta) < event.btageta
            )

            jetCount = jetCount + 1
            if jetCount >= self.maxjets:
                break

        # fill in dummy values for "missing" jets
        for i in range(jetCount, self.maxjets):
            self.branches["jet%dpT" % i][0] = defaultfill
            self.branches["jet%deta" % i][0] = defaultfill
            self.branches["jet%dphi" % i][0] = defaultfill
            self.branches["jet%db" % i][0] = defaultfill

        # Leptons
        lepCount = 1
        for aLep in event.sortedleptons:
            self.branches["lepton%dpT" % lepCount][0] = aLep.PT
            self.branches["lepton%dpT" % lepCount][0] = aLep.Eta
            self.branches["lepton%dpT" % lepCount][0] = aLep.Phi
            self.branches["lepton%dmT" % lepCount][0] = ROOT.TMath.Sqrt(
                2
                * event.met.Pt()
                * aLep.PT
                * (1 - ROOT.TMath.Cos(aLep.P4().DeltaPhi(event.met)))
            )
            mindr = 999
            for aJet in event.sortedjets:
                mindr = min(mindr, aLep.P4().DrEtaPhi(aJet.P4()))
            self.branches["lepton%dminjetdr" % lepCount][0] = mindr
            lepCount = lepCount + 1
            if lepCount >= self.maxleptons:
                break

        for i in range(lepCount, self.maxleptons):
            self.branches["lepton%dpT" % i][0] = defaultfill
            self.branches["lepton%dpT" % i][0] = defaultfill
            self.branches["lepton%dpT" % i][0] = defaultfill
            self.branches["lepton%dmT" % i][0] = defaultfill
            self.branches["lepton%dminjetdr" % i][0] = defaultfill

        self.tree.Fill()


# =====================================================================


# ======================================================================
#
class HistCollection:
    def __init__(self, tag, topdir, detaillevel=99):
        self.topdir = topdir
        self.tag = tag

        self.newdir = topdir.mkdir(tag)

        self.detaillevel = detaillevel

        self.newdir.cd()

        self.collections = {}

        self.topdir.cd()

    def write(self):
        self.newdir.cd()
        for _, k in self.collections.items():
            k.write()
        self.topdir.cd()

    def addcollection(self, tag):
        self.newdir.cd()
        self.collections[tag] = Hists(
            self.tag + "_" + tag, self.newdir, self.detaillevel
        )
        self.topdir.cd()

    def add(self, coll):
        for i, k in self.collections.items():
            if i in coll:
                k.add(coll[i])

    def fill(self, event, tag=None, weight=0):
        for i, k in self.collections.items():
            if tag is None:
                k.fill(event, weight)
            elif i == tag:
                k.fill(event, weight)
                break


class JetBins:
    def __init__(self, tag, topdir, detaillevel=99):
        self.topdir = topdir
        self.tag = tag

        self.newdir = topdir.mkdir(tag)
        self.newdir.cd()

        self.njets = (0, 1, 2, 3, 4, 5, 6)

        self.collections = {}
        self.collections["njets"] = HistCollection("njets", self.newdir, detaillevel)
        self.collections["njets"].addcollection("inclusive")
        for i in self.njets:
            self.collections["njets"].addcollection(str(i))

        self.topdir.cd()

    def write(self):
        self.newdir.cd()

        # fill the inclusive hist collections here by adding the constituents, should be faster
        # than doing it in 'fill'
        for _, k in self.collections["njets"].collections.items():
            if k.tag == "njets_inclusive":
                continue
            else:
                self.collections["njets"].collections["inclusive"].add(k)

        for _, k in self.collections.items():
            k.write()
        self.topdir.cd()

    def addcollection(self, tag):
        self.newdir.cd()
        self.collections[tag] = Hists(self.tag + "_" + tag, self.topdir, False)
        self.topdir.cd()

    def add(self, coll):
        for i, k in self.collections.items():
            if i in coll:
                k.add(coll[i])

    def fill(self, event, weight=0):
        njets = 0
        for j in event.event.Jet:
            if j.PT > 25 and abs(j.Eta) < 4.5:
                njets += 1
        # print "filling jet bin with njets=%d" % (event.njets())
        # HAZ: Make the last jet bin an overflow
        if njets > max(self.njets):
            njets = max(self.njets)
        self.collections["njets"].fill(event, str(njets), weight)
        # binned results
        # for thresh_i in xrange(len(self.njets)):
        #     if (((thresh_i < len(self.njets)-1) and
        #          njets>=self.njets[thresh_i] and
        #          njets<self.njets[thresh_i+1]) or
        #         ((thresh_i == len(self.njets)-1) and
        #          njets>=self.njets[thresh_i])):
        #         self.collections["njets"].fill(event,str(self.njets[thresh_i]))
        #         break


# ======================================================================
