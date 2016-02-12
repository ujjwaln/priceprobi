activate_this = '/home/ubuntu/priceprobi/ppenv/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/home/ubuntu/priceprobi')
sys.stdout = sys.stderr
from priceprobi.api.pp_api import app as application