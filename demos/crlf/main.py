import multiprocessing
import logging
from app import app, init_db
from tcp_server import start_tcp_server

def run_flask_app():
    init_db()
    app.run(debug=True, use_reloader=False)

def run_tcp_server():
    start_tcp_server()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    flask_process = multiprocessing.Process(target=run_flask_app)
    tcp_process = multiprocessing.Process(target=run_tcp_server)

    flask_process.start()
    tcp_process.start()

    flask_process.join()
    tcp_process.join()
