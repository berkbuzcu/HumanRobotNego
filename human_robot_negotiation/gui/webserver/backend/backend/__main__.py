from . import app
from waitress import serve
import logging

logger = logging.getLogger('waitress')
logger.setLevel(logging.INFO)
# app.run(host='0.0.0.0', port=5000, debug=True)
serve(app, listen='*:5000')
