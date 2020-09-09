# Statistical Analysis

For this purpose, we will use [`cabinetry`](https://pypi.org/project/cabinetry/) to build histograms and make the JSON workspaces needed for the statistical fits.

To set this up, one will need `pip install cabinetry[contrib]` at the minimum.

## hadd

First we need to combine the output background slices with `hadd`, so we'll put them in our local `[output](./output)` directory:

```
docker run \
       --log-driver=journald \
       --name "${tag}__hadd" \
       --rm \
       -v ~mhance/mario-mapyde/output:/data \
       -v $PWD/output:/output \
       -w /output \
       --user $(id -u):$(id -g) \
       gitlab-registry.cern.ch/scipp/mario-mapyde/delphes:master \
       'for KIND in EWK QCD; do for COM in 13 14 100; do hadd Vjj${KIND}_${COM}.root /data/Vjj${KIND}_${COM}_*/analysis/histograms.root; done; done'
```

## generate cabinetry configs

```
python generate_cabinetry.py
```

## run cabinetry

```
python run_cabinetry.py config.yml
```
