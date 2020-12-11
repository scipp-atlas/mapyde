import cabinetry
import sys

cabinetry_config = cabinetry.configuration.load(sys.argv[1])

# create template histograms
cabinetry.template_builder.create_histograms(cabinetry_config)

# perform histogram post-processing
cabinetry.template_postprocessor.run(cabinetry_config)

# visualize templates and data
cabinetry.visualize.data_MC_from_histograms(cabinetry_config, "figures/")

# build a workspace
ws = cabinetry.workspace.build(cabinetry_config)
cabinetry.workspace.save(ws, sys.argv[1].replace(".yml", ".json"))
