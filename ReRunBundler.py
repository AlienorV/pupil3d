import logging
import bundle_methods
from time import time

logging.basicConfig(level=logging.INFO, format="%(message)s")

# initialize OsmBundler manager class
t = time()

manager = bundle_methods.Bundler()

start_time = time()

# only run bundler with given list of images and key list 
manager.re_run_bundle_adjustment()

current_time = time()
bundle_t = current_time-start_time
print "\nBundle adjustment took: %s seconds\nElapsed Time: %s\n" %(bundle_t, current_time-t)

manager.open_result()

print "\nTiming Report:\n\
		\tBundle Adjustment: %s\n\
		\tTotal Elapsed Time: %s\n" %(bundle_t, current_time-t)

