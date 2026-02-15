Installation and usage

1) Generate or copy the unit file to systemd and reload:

```sh
# From the project root, generate the unit (optional):
deployment/generate_service.sh --use-launcher

# Copy the generated unit to systemd and reload:
sudo cp deployment/sample_ollama_chat.service /etc/systemd/system/
sudo systemctl daemon-reload
```

2) Enable and start the service:

```sh
sudo systemctl enable --now sample_ollama_chat.service
```

3) Check status and logs:

```sh
sudo systemctl status sample_ollama_chat.service
sudo journalctl -u sample_ollama_chat.service -f
```

Notes:
- The service runs as the configured `User`/`Group` in the unit. By default the generator assumes a virtualenv at `venv/` (project root) and the app at `backend/app.py`.
- If your environment differs, edit `deployment/sample_ollama_chat.service` (generated) and adjust `User`, `Group`, `WorkingDirectory`, and `ExecStart` accordingly.
- To change port, update `Environment=FLASK_PORT=5000` in the unit file or pass `--port` to `generate_service.sh`.
- To run under a dedicated service user, create the user and adjust `User`/`Group` and filesystem permissions.
