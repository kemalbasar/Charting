import index
import warnings

warnings.filterwarnings("ignore")

server = index.app.server

if __name__ == '__main__':
    index.app.run_server(debug=True)