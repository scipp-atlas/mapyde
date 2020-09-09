import json
import pathlib

config = {
    "General": {
        "Measurement": "main",
        "POI": "mu",
        "HistogramFolder": "histograms/",
        "InputPath": "/home/mhance/mario-mapyde/output/{SamplePath}/analysis/histograms.root",
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
    "medMET": "(MET >= 200) && (MET < 300)",
    "higMET": "(MET >=300)",
}

variable = "mjj"
binning = [200, 300, 400, 500, 600]

for jet_name, jet_selection in jet_selections.items():
    for met_name, met_selection in met_selections.items():
        config["Regions"].append(
            {
                "Name": f"SR_{met_name}_{jet_name}",
                "Filter": f"(nLep == 0) && (abs(j1Eta - j2Eta) > 3.0) && {jet_selection} && {met_selection}",
                "Variable": variable,
                "Binning": binning,
            }
        )

        config["Regions"].append(
            {
                "Name": f"CRW_{met_name}_{jet_name}",
                "Filter": f"(nLep == 1) && (abs(j1Eta - j2Eta) > 3.0) && {jet_selection} && {met_selection}",
                "Variable": variable,
                "Binning": binning,
            }
        )

        config["Regions"].append(
            {
                "Name": f"CRZ_{met_name}_{jet_name}",
                "Filter": f"(nLep == 2) && (abs(j1Eta - j2Eta) > 3.0) && {jet_selection} && {met_selection}",
                "Variable": variable,
                "Binning": binning,
            }
        )

samples = []
# Define Samples
for path in pathlib.Path("/home/mhance/mario-mapyde/output/").glob("*"):
    samples.append(path.name)
    config["Samples"].append(
        {
            "Name": path.name,
            "Tree": "SR/hftree",
            "SamplePath": path.name,
            "Weight": "weight",
            "Data": False,
        }
    )

# Add a "Data" Sample (just use last one in)
config["Samples"].append(
    {"Name": "data", "Tree": "SR/hftree", "SamplePath": samples[-1], "Data": True}
)

# Define Systematics
config["Systematics"].append(
    {
        "Name": "Luminosity",
        "Up": {"Normalization": 0.05},
        "Down": {"Normalization": -0.05},
        "Samples": samples,
        "Type": "Normalization",
    },
)

config["Systematics"].append(
    {
        "Name": "flat_uncertainty",
        "Up": {"Normalization": 0.3},
        "Down": {"Normalization": -0.3},
        "Samples": samples,
        "Type": "Normalization",
    },
)

config["NormFactors"].append(
    {
        "Name": "mu",
        "Samples": [sample for sample in samples if sample.startswith("VBFSUSY")],
        "Nominal": 1,
        "Bounds": [0, 5],
    }
)

pathlib.Path("cabinetry.yml").write_text(json.dumps(config, indent=4, sort_keys=True))
