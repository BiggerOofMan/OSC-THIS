import multiprocessing

bind = "0.0.0.0:8000"
worker_class = "gthread"
workers = max(2, multiprocessing.cpu_count() // 2)
threads = 4
timeout = 120
keepalive = 5
preload_app = True
loglevel = "info"
errorlog = "-"  # stderr
accesslog = "-"  # stdout
