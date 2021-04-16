
database=/export/share/data/mhance/tthh

proc=$1
ecms=${2:-14}
totjobs=${3:-1}
seedoffset=${4:-0}
tag=""
case $proc in
    tthh | tttt)
	nevents=1000;
	madgraphsherpa="madgraph"
        tag="${proc}_${ecms}_001k_${seedoffset}";;
    
    ttbbz | ttbbh | ttbbjj)
	nevents=1000;
	madgraphsherpa="sherpa"
	tag="${proc}_${ecms}_001k_${seedoffset}";;
esac

dtst="$(date +%Y%m%d%H%M)"
logfiledir=${database}/${tag}/batch_logs/${dtst}
mkdir -p $logfiledir

subfile="${logfiledir}/test.cfg"
rm -f $subfile

echo "universe = vanilla" >> ${subfile}

exe="run_tthh.sh"
cp ${exe} ${logfiledir}

echo "executable = ${logfiledir}/${exe}" >> ${subfile}
echo "Arguments = ${proc} ${ecms} ${madgraphsherpa} ${nevents} ${tag} \$(Process) ${seedoffset}" >> ${subfile}
echo "output = ${logfiledir}/out.\$(Process).out" >> ${subfile}
echo "error  = ${logfiledir}/out.\$(Process).err" >> ${subfile}
echo "Log    = ${logfiledir}/out.\$(Process).log" >> ${subfile}
echo "Requirements = (Machine != \"wrk2prv.ucsc.edu\" && Machine != \"wrk5prv.ucsc.edu\" && Machine != \"atlas01.ucsc.edu\" )" >> ${subfile}
#echo "getenv = True" >> ${subfile}
echo "should_transfer_files = YES" >> ${subfile}
echo "when_to_transfer_output = ON_EXIT" >> ${subfile}

if [[ $totjobs == 1 ]]; then
    echo "stream_output = True" >> ${subfile}
fi

echo "Queue ${totjobs}" >> ${subfile}
echo "" >> ${subfile}
echo "" >> ${subfile}

cat ${subfile}
condor_submit ${subfile}
