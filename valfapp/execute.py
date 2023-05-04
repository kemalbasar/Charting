import index
import warnings
import os
from werkzeug.middleware.profiler import ProfilerMiddleware
PROF_DIR = r'F:\pycarhm projects\Charting\valfapp\profs'
warnings.filterwarnings("ignore")

server = index.app.server

if __name__ == '__main__':
    if os.getenv("PROFILER", None):
        index.app.server.config["PROFILE"] = True
        index.app.server.wsgi_app = ProfilerMiddleware(
            index.app.server.wsgi_app,
            sort_by=["cumtime"],
            restrictions=[50],
            stream=None,
            profile_dir=PROF_DIR
        )
    index.app.run_server(debug=True)

