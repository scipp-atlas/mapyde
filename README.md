
The fun stuff happens in ```runGene.sh```.  Sample commands look like:

```
runGene.sh \
	   mg5_aMC                              \  # Binary
	   Gene/Bkg-ttbar-Nj                    \  # Proc Card
           SM                                   \  # Param Card
	   RunCards/default_LO.dat              \ # Run Card
	   DelphesCards/delphes_card_ATLAS.tcl  \ # Delphes card
           $(Process)                           \ # Process number
```

Note that absolute paths may be needed depending on your setup.  Sourcing ```setup.sh``` usually helps.


To submit samples to a condor queue (specifically the UCSC Tier-3), an example command would be:

```
#           proc_card        parm_card   run_card             delphes_card                        number_of_jobs   submission_tag (optional)
./submit.sh Gene/Bkg-Wjets-1 SM          RunCards/default.dat DelphesCards/delphes_card_ATLAS.tcl 10               BkgProd_v2
```
