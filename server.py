from flask import Flask, jsonify, request
import subprocess
import os
import sys

# Inițiem aplicația Flask
app = Flask(__name__)

# Definim o "rută". Aceasta este ca o adresă URL specifică.
# Când cineva accesează adresa principală a serverului ('/'),
# funcția de mai jos va fi executată.
@app.route('/')
def index():
    return "Serverul Flask funcționează!"

@app.route('/run-context-agent')
def run_context_agent():
    try:
        # Obține calea absolută către directorul proiectului
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Calea către virtual environment
        venv_python = os.path.join(project_dir, '.venv', 'Scripts', 'python.exe')
        
        # Verifică dacă virtual environment-ul există
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = 'python'
        
        # Adaugă directorul proiectului la PYTHONPATH
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{project_dir};{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = project_dir

        # Rulează scriptul main.py al agentului ca modul (pentru importurile relative)
        result = subprocess.run(
            [python_executable, '-m', 'context.context_agent.main'],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_dir,  # Asigură-te că scriptul rulează în directorul rădăcină al proiectului
            env=env  # Folosește variabilele de mediu modificate
        )
        
        # Returnează un răspuns JSON cu output-ul scriptului
        return jsonify({
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.CalledProcessError as e:
        # Dacă scriptul returnează un cod de eroare, capturează eroarea
        return jsonify({
            "status": "error",
            "message": "A apărut o eroare la rularea agentului de context.",
            "output": e.stdout,
            "error": e.stderr
        }), 500
    except FileNotFoundError:
        # Dacă scriptul nu este găsit
        return jsonify({
            "status": "error",
            "message": "Scriptul agentului de context nu a fost găsit."
        }), 404
    except Exception as e:
        # Pentru any other excepție
        return jsonify({
            "status": "error",
            "message": f"A apărut o eroare neașteptată: {str(e)}"
        }), 500

@app.route('/run-twitter-agent')
def run_twitter_agent():
    try:
        # Obține calea absolută către directorul proiectului
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Calea către virtual environment
        venv_python = os.path.join(project_dir, '.venv', 'Scripts', 'python.exe')
        
        # Verifică dacă virtual environment-ul există
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = 'python'
        
        # Adaugă directorul proiectului la PYTHONPATH
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{project_dir};{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = project_dir

        # Rulează scriptul main.py al agentului ca modul (pentru importurile relative)
        result = subprocess.run(
            [python_executable, '-m', 'agents.twitter.main'],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_dir,  # Asigură-te că scriptul rulează în directorul rădăcină al proiectului
            env=env  # Folosește variabilele de mediu modificate
        )
        
        # Returnează un răspuns JSON cu output-ul scriptului
        return jsonify({
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.CalledProcessError as e:
        # Dacă scriptul returnează un cod de eroare, capturează eroarea
        return jsonify({
            "status": "error",
            "message": "A apărut o eroare la rularea agentului Twitter.",
            "output": e.stdout,
            "error": e.stderr
        }), 500
    except FileNotFoundError:
        # Dacă scriptul nu este găsit
        return jsonify({
            "status": "error",
            "message": "Scriptul agentului Twitter nu a fost găsit."
        }), 404
    except Exception as e:
        # Pentru orice altă excepție
        return jsonify({
            "status": "error",
            "message": f"A apărut o eroare neașteptată: {str(e)}"
        }), 500

@app.route('/run-twitter-agent-mock')
def run_twitter_agent_mock():
    try:
        # Obține calea absolută către directorul proiectului
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Calea către virtual environment
        venv_python = os.path.join(project_dir, '.venv', 'Scripts', 'python.exe')
        
        # Verifică dacă virtual environment-ul există
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = 'python'
        
        # Adaugă directorul proiectului la PYTHONPATH
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{project_dir};{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = project_dir

        # Rulează agentul mock Twitter (fără scraping)
        result = subprocess.run(
            [python_executable, 'agents/twitter/mock_twitter_agent.py'],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_dir,  # Asigură-te că scriptul rulează în directorul rădăcină al proiectului
            env=env  # Folosește variabilele de mediu modificate
        )
        
        # Returnează un răspuns JSON cu output-ul scriptului
        return jsonify({
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.CalledProcessError as e:
        # Dacă scriptul returnează un cod de eroare, capturează eroarea
        return jsonify({
            "status": "error",
            "message": "A apărut o eroare la rularea agentului Twitter Mock.",
            "output": e.stdout,
            "error": e.stderr
        }), 500
    except FileNotFoundError:
        # Dacă scriptul nu este găsit
        return jsonify({
            "status": "error",
            "message": "Scriptul agentului Twitter Mock nu a fost găsit."
        }), 404
    except Exception as e:
        # Pentru orice altă excepție
        return jsonify({
            "status": "error",
            "message": f"A apărut o eroare neașteptată: {str(e)}"
        }), 500

@app.route('/scrape-tweets')
def scrape_tweets():
    try:
        # Obține calea absolută către directorul proiectului
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Calea către virtual environment
        venv_python = os.path.join(project_dir, '.venv', 'Scripts', 'python.exe')
        
        # Verifică dacă virtual environment-ul există
        if os.path.exists(venv_python):
            python_executable = venv_python
        else:
            python_executable = 'python'
        
        # Adaugă directorul proiectului la PYTHONPATH
        env = os.environ.copy()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{project_dir};{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = project_dir

        # Rulează scriptul twitter_scraper.py al agentului ca modul
        result = subprocess.run(
            [python_executable, '-m', 'agents.twitter.twitter_scraper'],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_dir,
            env=env
        )
        
        # Returnează un răspuns JSON cu output-ul scriptului
        return jsonify({
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.CalledProcessError as e:
        # Dacă scriptul returnează un cod de eroare, capturează eroarea
        return jsonify({
            "status": "error",
            "message": "A apărut o eroare la rularea scraper-ului Twitter.",
            "output": e.stdout,
            "error": e.stderr
        }), 500
    except FileNotFoundError:
        # Dacă scriptul nu este găsit
        return jsonify({
            "status": "error",
            "message": "Scriptul scraper-ului Twitter nu a fost găsit."
        }), 404
    except Exception as e:
        # Pentru orice altă excepție
        return jsonify({
            "status": "error",
            "message": f"A apărut o eroare neașteptată: {str(e)}"
        }), 500

# --- Exemplu pentru cerere GET cu parametru in URL ---
@app.route('/get_client/<client_name>', methods=['GET'])
def get_client_info(client_name):
    """
    Această funcție răspunde la o cerere GET.
    Parametrul 'client_name' este preluat direct din URL.
    """
    return f"GET request pentru clientul: {client_name}"

# --- Exemplu pentru cerere POST cu parametru in URL ---
@app.route('/post_client/<client_name>', methods=['POST'])
def post_client_info(client_name):
    """
    Această funcție răspunde la o cerere POST.
    Chiar dacă metoda este POST, parametrul 'client_name' este tot din URL.
    """
    # Într-un caz real, aici ai prelucra datele trimise în corpul cererii POST,
    # de exemplu: data = request.get_json()
    return f"POST request pentru clientul: {client_name}"

@app.route('/scrape-article', methods=['GET', 'POST'])
def scrape_article():
    try:
        if request.method == 'POST':
            data = request.get_json()
            if not data or 'base_url' not in data or 'client_name' not in data:
                return jsonify({
                    "status": "error",
                    "message": "Request body must contain 'base_url' and 'client_name'"
                }), 400
            base_url = data['base_url']
            client_name = data['client_name']
        else:  # GET request
            base_url = request.args.get('base_url')
            client_name = request.args.get('client_name')
            if not base_url or not client_name:
                return jsonify({
                    "status": "error",
                    "message": "URL parameters must contain 'base_url' and 'client_name'"
                }), 400

        project_dir = os.path.dirname(os.path.abspath(__file__))
        venv_python = os.path.join(project_dir, '.venv', 'Scripts', 'python.exe')
        
        python_executable = venv_python if os.path.exists(venv_python) else 'python'
        
        env = os.environ.copy()
        env['PYTHONPATH'] = project_dir if 'PYTHONPATH' not in env else f"{project_dir};{env['PYTHONPATH']}"

        script_path = os.path.join(project_dir, 'agents', 'website', 'article_scraper.py')

        result = subprocess.run(
            [python_executable, script_path, base_url, client_name],
            capture_output=True,
            text=True,
            check=True,
            cwd=project_dir,
            env=env
        )
        
        return jsonify({
            "status": "success",
            "output": result.stdout,
            "error": result.stderr
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            "status": "error",
            "message": "A apărut o eroare la rularea article_scraper.py.",
            "output": e.stdout,
            "error": e.stderr
        }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"A apărut o eroare neașteptată: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)