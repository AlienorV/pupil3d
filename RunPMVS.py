import logging
import pmvs_methods

logging.basicConfig(level=logging.INFO, format="%(message)s")

# initialize OsmPMVS manager class
manager = pmvs_methods.Pmvs()

# initialize PMVS input from Bundler output
manager.doBundle2PMVS()

# call PMVS
manager.doPMVS()

# show the Result
manager.openResult()