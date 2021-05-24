import json
import pathlib
import copy

SIGNAL_SAMPLE_PREFIX = "VBFSUSY"

base_config = {
    "General": {
        "Measurement": "main",
        "POI": "mu",
        "HistogramFolder": "histograms/",
        "InputPath": "{SamplePaths}",
    },
    "Regions": [],
    "Samples": [],
    "Systematics": [],
    "NormFactors": [],
}

# Define Regions
jet_selections = {
    "lownJets": "(njet == 2)",
    "mednJets": "(njet == 3)",
    "hignJets": "(njet == 4)",
}

met_selections = {
    "lowMET": "(MET < 200)",
    "medMET": "(MET >= 200) & (MET < 300)",
    "higMET": "(MET >=300)",
}

variable = "mjj"
binning = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]

for jet_name, jet_selection in jet_selections.items():
    for met_name, met_selection in met_selections.items():
        base_config["Regions"].append(
            {
                "Name": f"SR_{met_name}_{jet_name}",
                "Filter": f"(nMuon == 0) & (abs(j1Eta - j2Eta) > 3.0) & {jet_selection} & {met_selection}",
                "Variable": variable,
                "Binning": binning,
            }
        )

        base_config["Regions"].append(
            {
                "Name": f"CRW_{met_name}_{jet_name}",
                "Filter": f"(nMuon == 1) & (abs(j1Eta - j2Eta) > 3.0) & {jet_selection} & {met_selection}",
                "Variable": variable,
                "Binning": binning,
            }
        )

        base_config["Regions"].append(
            {
                "Name": f"CRZ_{met_name}_{jet_name}",
                "Filter": f"(nMuon == 2) & (abs(j1Eta - j2Eta) > 3.0) & {jet_selection} & {met_selection.replace('MET','MET_invismu')}",
                "Variable": variable,
                "Binning": binning,
            }
        )


for center_of_mass in ["13", "14", "100"]:
    for sig_path in pathlib.Path("/data/users/mhance/SUSY").glob(
        f"{SIGNAL_SAMPLE_PREFIX}_{center_of_mass}_*mjj_all.root"
    ):
        config = copy.deepcopy(base_config)
        # Define Samples
        config["Samples"].append(
            {
                "Name": sig_path.name.replace(".root", "").split("/")[-1],
                "Tree": "presel/hftree",
                "SamplePaths": str(sig_path.resolve()),
                "Weight": "weight",
                "Data": False,
            }
        )
        for path in pathlib.Path("/data/users/mhance/SUSY").glob(f"Vjj*_{center_of_mass}*.root"):
            config["Samples"].append(
                {
                    "Name": path.name.replace(".root", "").split("/")[-1],
                    "Tree": "presel/hftree",
                    "SamplePaths": str(path.resolve()),
                    "Weight": "weight",
                    "Data": False,
                }
            )

        # Add a "Data" Sample (just use signal for now)
        config["Samples"].append(
            {
                "Name": "data",
                "Tree": "presel/hftree",
                "SamplePaths": str(sig_path.resolve()),
                "Data": True,
            }
        )

        # Define Systematics
        config["Systematics"].append(
            {
                "Name": "flat_uncertainty",
                "Up": {"Normalization": 0.3},
                "Down": {"Normalization": -0.3},
                "Samples": [sample["Name"] for sample in config["Samples"]],
                "Type": "Normalization",
            },
        )

        config["NormFactors"].append(
            {
                "Name": "mu",
                "Samples": sig_path.name.replace(".root","").split("/")[-1],
                "Nominal": 1,
                "Bounds": [0, 5],
            }
        )

        pathlib.Path(sig_path.name.replace(".root", ".yml")).write_text(
            json.dumps(config, indent=4, sort_keys=True)
        )
