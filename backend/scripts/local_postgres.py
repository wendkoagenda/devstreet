"""Piloter uniquement le cluster PostgreSQL local deja initialise pour ce depot."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess

from dotenv import dotenv_values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('start', 'stop', 'status'))
    args = parser.parse_args()
    backend = Path(__file__).resolve().parents[1]
    local = (backend / '.local').resolve()
    data = (local / 'postgres').resolve()
    if not data.is_relative_to(local) or not (data / 'PG_VERSION').is_file():
        parser.error('Aucun cluster existant dans backend/.local/postgres.')
    executable = shutil.which('pg_ctl')
    if not executable and os.name == 'nt':
        version = (data / 'PG_VERSION').read_text().strip()
        program_files = os.environ.get('PROGRAMFILES')
        if not program_files:
            parser.error('PROGRAMFILES absent : ajouter pg_ctl au PATH.')
        candidate = Path(program_files) / 'PostgreSQL' / version / 'bin/pg_ctl.exe'
        if candidate.is_file():
            executable = str(candidate)
    if not executable:
        parser.error('pg_ctl introuvable : ajouter PostgreSQL au PATH.')
    command = [executable, '-D', str(data)]
    flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    running = subprocess.run(command + ['status'], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, creationflags=flags).returncode == 0
    if args.action == 'status':
        print('PostgreSQL local demarre.' if running else 'PostgreSQL local arrete.')
        return
    if running == (args.action == 'start'):
        print('PostgreSQL local deja dans cet etat.')
        return
    if args.action == 'start':
        values = dotenv_values(backend / '.env')
        host = values.get('DB_HOST', '127.0.0.1')
        port = str(values.get('DB_PORT', '55432'))
        if host not in ('localhost', '127.0.0.1') or not port.isdigit() or not 1 <= int(port) <= 65535:
            parser.error('Ce script accepte uniquement une base locale et un port valide.')
        command += ['-l', str(local / 'postgres.log'), '-o', f'-p {port} -h 127.0.0.1', 'start']
    else:
        command += ['stop', '-m', 'fast']
    result = subprocess.run(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, creationflags=flags)
    if result.returncode:
        parser.exit(result.returncode, 'Echec : consulter backend/.local/postgres.log.\n')
    print('PostgreSQL local demarre.' if args.action == 'start' else 'PostgreSQL local arrete.')


if __name__ == '__main__':
    main()
