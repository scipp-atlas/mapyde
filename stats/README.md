# Statistical Analysis

For this purpose, we will use [`cabinetry`](https://pypi.org/project/cabinetry/) to build histograms and make the JSON workspaces needed for the statistical fits.

To set this up, one will need `pip install cabinetry[contrib]` at the minimum.

## hadd

First we need to combine the output background slices with `hadd`, so we'll put them in our local `[output](./output)` directory:

```
docker run \
       --rm \
       -v ~mhance/mario-mapyde/output:/data \
       -v $PWD/output:/output \
       -w /output \
       --user $(id -u):$(id -g) \
       ghcr.io/scipp-atlas/mario-mapyde/delphes:latest \
       'for KIND in EWK QCD; do for COM in 13 14 100; do hadd Vjj${KIND}_${COM}.root /data/Vjj${KIND}_${COM}_*/analysis/histograms.root; done; done'
```

Next, we need to do the same for the signal slices

```
docker run \
       --rm \
       -v ~mhance/mario-mapyde/output:/data \
       -v $PWD/output:/output \
       -w /output \
       --user $(id -u):$(id -g) \
       ghcr.io/scipp-atlas/mario-mapyde/delphes:latest \
       'for KIND in Higgsino WinoBino; do for MASS in 150 250; do for COM in 13 14 100; do hadd VBFSUSY_${COM}_${KIND}_${MASS}.root /data/VBFSUSY_${COM}_${KIND}_${MASS}_*/analysis/histograms.root; done; done; done'
```


## generate cabinetry configs

```
python generate_cabinetry.py
```

## run cabinetry

```
python run_cabinetry.py config.yml
```
