import subprocess
import webbrowser
import time

# Iniciar Streamlit
subprocess.Popen([
    "python",
    "-m",
    "streamlit",
    "run",
    "app.py"
])

# Esperar iniciar
time.sleep(5)

# Abrir navegador
webbrowser.open(
    "http://localhost:8501"
)