mass=400
splitting=399

./run_VBFSUSY_standalone.sh -r -M ${mass} -S ${splitting} -N 10000 -c 8 -a -C lowlevelAna.py -a

tag="SUSY_13_GluinoBino_${mass}_${splitting}_ttbar_and_gluino_"
#./test/wrapper_root2hdf5.sh ${tag}
python3 scripts/root2hdf5.py /data/users/mhance/SUSY/${tag}/analysis/lowlevelAna.root:allev/lowleveltree
