
tag=$1

if [[ $tag == "" ]]; then
    tag="test_charginos_001"
fi

base=${PWD}
workdir=output/${tag}
eventsdir=PROC_${tag}/Events/run_01
delphes_card="delphes_card_ATLAS.tcl"
pythiaoutput="tag_1_pythia8_events"


# to make delphes output
cp DelphesCards/${delphes_card} ${workdir}
docker run \
       --rm \
       -it \
       -v ${base}/${workdir}:/input \
       -w /usr/local/share/delphes/delphes \
       mhance/delphes:001 \
       "cd /usr/local/share/delphes/delphes && \
        cp /input/${delphes_card} . && \
        cp /input/${eventsdir}/${pythiaoutput}.hepmc.gz . && \
	gunzip ${pythiaoutput}.hepmc.gz && \
	./DelphesHepMC ${delphes_card} delphes.${tag}.root ${pythiaoutput}.hepmc && \
	cp delphes.${tag}.root /input/${eventsdir}"


# to analyze delphes output
delphes_path="/usr/local/share/delphes/delphes"
docker run \
       --rm \
       -v ${PWD}:/input \
       -w /input \
       mhance/delphes:001 \
       "cd /input && \
        export DELPHES_PATH=${delphes_path} && \
	export ROOT_INCLUDE_PATH=\$ROOT_INCLUDE_PATH:${delphes_path}:${delphes_path}/external && \
	./SimpleAna.py --input ${workdir}/${eventsdir}/delphes.${tag}.root --output ${workdir}/${eventsdir}/hist.${tag}.root"
