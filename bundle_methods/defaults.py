
maxPhotoDimension = 1200
matchingEngine = "bundler"
featureExtractor = "siftvlfeat"

bundlerOptions = (
"--match_table matches.init.txt\n",
"--output bundle.out\n",
"--output_all bundle_\n",
"--output_dir bundle\n",
"--variable_focal_length\n",
"--use_focal_estimate\n",
"--constrain_focal\n",
"--constrain_focal_weight 0.0001\n",
"--estimate_distortion\n",
"--run_bundle\n"
)

# bundler_rerun_options = (
# "--match_table matches.init.txt\n",
# "--output bundle.out\n",
# "--output_all bundle_\n",
# "--output_dir bundle_rerun_\n",
# "--variable_focal_length\n",
# "--use_focal_estimate\n",
# "--constrain_focal\n",
# "--constrain_focal_weight 0.0001\n",
# "--estimate_distortion\n",
# "--run_bundle\n"
# )

# --rerun_bundle

bundler_add_options = (
"--add_images add_list.txt\n"
"--bundle bundle/bundle.out\n"
"--output_dir bundle\n"
)