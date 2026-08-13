from workers.setup_group import ensure_group
from workers.worker import run

if __name__ == "__main__":
    ensure_group()
    run()
