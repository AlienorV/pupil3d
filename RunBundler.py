import logging
import bundle_methods
from time import time

logging.basicConfig(level=logging.INFO, format="%(message)s")

# initialize OsmBundler manager class
t = time()

manager = bundle_methods.Bundler()

start_time = time()

manager.prepare_photos()

current_time = time()
prep_t = current_time-start_time
print "\nPrepare Photos & Feature Extraction took: %s seconds\nElapsed Time: %s\n" %(prep_t, current_time-t)

start_time = time()

manager.match_features()

current_time = time()
match_t = current_time-start_time
print "\nPairwise Feature matching took: %s seconds\nElapsed Time: %s\n" %(match_t, current_time-t)

start_time = time()

manager.run_bundle_adjustment()

current_time = time()
bundle_t = current_time-start_time
print "\nBundle adjustment took: %s seconds\nElapsed Time: %s\n" %(bundle_t, current_time-t)

manager.open_result()

print "\nTiming Report:\n\
		\tPrepare Photos: %s\n\
		\tMatch Features: %s\n\
		\tBundle Adjustment: %s\n\
		\tTotal Elapsed Time: %s\n" %(prep_t, match_t, bundle_t, current_time-t)

