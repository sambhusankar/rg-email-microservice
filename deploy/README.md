# Deploying to an Oracle Cloud Always Free VM

This worker is a blocking Redis stream consumer (`workers/worker.py`'s `run()`), so it needs
a persistent process, not a serverless function. This runs it as a systemd service on an
Always Free Ampere A1 (or E2.1.Micro) instance.

## 1. Provision the VM
- Create an Always Free instance (Ubuntu 22.04/24.04 recommended).
- No inbound ports need to be opened — the worker only makes outbound connections
  (Redis, Resend API). Leave ingress closed except SSH (22).

## 2. Install base packages
```bash
sudo apt update && sudo apt install -y python3-venv python3-pip git
```

## 3. Get the code onto the VM
```bash
git clone <your-repo-url> rg-email-microservice
cd rg-email-microservice
```

## 4. Set up the virtualenv
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 5. Configure environment
Copy `.env` up separately (never commit it):
```bash
scp -i /path/to/key .env ubuntu@<PUBLIC_IP>:~/rg-email-microservice/.env
```

## 6. Install the systemd service
```bash
sudo cp deploy/rg-email-worker.service /etc/systemd/system/rg-email-worker.service
sudo systemctl daemon-reload
sudo systemctl enable --now rg-email-worker
sudo systemctl status rg-email-worker
journalctl -u rg-email-worker -f   # tail logs
```

The unit file assumes the repo lives at `/home/ubuntu/rg-email-microservice` and runs as
the `ubuntu` user. Edit `WorkingDirectory`, `EnvironmentFile`, `ExecStart`, and `User` in
`rg-email-worker.service` if your path or user differs.

## 7. Updating after a code change
```bash
cd rg-email-microservice
git pull
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart rg-email-worker
```
