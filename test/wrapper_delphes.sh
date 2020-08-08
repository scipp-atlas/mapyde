
tag=$1

if [[ $tag == "" ]]; then
    tag="test_charginos_001"
fi

workdir=${PWD}/output/${tag}
eventsdir=PROC_${tag}/Events/run_01
delphes_card="delphes_card_ATLAS.tcl"
pythiaoutput="tag_1_pythia8_events"

cp DelphesCards/${delphes_card} ${workdir}

docker run \
       --rm \
       -it \
       -v ${workdir}:/input \
       -w /usr/local/share/delphes/delphes \
       mhance/delphes:001 \
       "cd /usr/local/share/delphes/delphes && \
        cp /input/${delphes_card} . && \
        cp /input/${eventsdir}/${pythiaoutput}.hepmc.gz . && \
	gunzip ${pythiaoutput}.hepmc.gz && \
	./DelphesHepMC ${delphes_card} delphes.${tag}.root ${pythiaoutput}.hepmc && \
	cp delphes.${tag}.root /input/${eventsdir}"

