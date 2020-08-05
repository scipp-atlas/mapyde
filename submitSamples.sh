## Signal (tau tau, all fermionic benchmark points)
#./submit.sh Gene/Sig-tautau SLHA/HcWh_heavy_ff.slha RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl
#./submit.sh Gene/Sig-tautau SLHA/HcWh_med_ff.slha   RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl
#./submit.sh Gene/Sig-tautau SLHA/HcWh_light_ff.slha RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl

## Bkgs
#./submit.sh Gene/Bkg-ttbar-Nb SM RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl 100
#./submit.sh Gene/Bkg-ttbar-Nj SM RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl 100
#./submit.sh Gene/Bkg-ttbar-V  SM RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl 5
./submit.sh Gene/Bkg-Wjets-1 SM RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl 10
./submit.sh Gene/Bkg-Wjets-2 SM RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl 10
./submit.sh Gene/Bkg-Wjets-3 SM RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl 10
./submit.sh Gene/Bkg-Wjets-4 SM RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl 10

