# https://clalancette.github.io/pycdlib/
# https://github.com/clalancette/pycdlib

from io import BytesIO
import random

import pycdlib

iso = pycdlib.PyCdlib()
iso.new(udf="2.60")
foostr = b'a' *1024000 # * random.randint(100000, 100000) 

iso.add_directory('/FOO', udf_path='/foo')
for n in range(25000):
	if n%1000==0:
		print(n/1000)
	iso.add_fp(BytesIO(foostr), len(foostr), iso_path='/FOO/AA'+str(n), udf_path='/foo/aa'+str(n)+".txt")


iso.add_fp(BytesIO(foostr), len(foostr), iso_path='/FOO.;1', udf_path='/foo')
iso.add_directory('/DIR1', udf_path='/dir1')

print(iso.has_udf(), iso.has_joliet(), iso.has_rock_ridge())

iso.write('new.iso')
iso.close()
