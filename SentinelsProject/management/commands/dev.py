import os
import sys
import subprocess
import signal
import threading
import webbrowser
import time
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Run Django development server and Tailwind watch simultaneously'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processes = []
        self.stop_event = threading.Event()
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            default='127.0.0.1',
            help='Host to bind Django server to (default: 127.0.0.1)'
        )
        parser.add_argument(
            '--port',
            default='8000',
            help='Port to bind Django server to (default: 8000)'
        )
        parser.add_argument(
            '--no-browser',
            action='store_true',
            help='Skip opening browser automatically'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting development environment...')
        )
        
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start Django development server
            django_cmd = [
                sys.executable, 'manage.py', 'runserver', 
                f"{options['host']}:{options['port']}"
            ]
            
            self.stdout.write('Starting Django development server...')
            django_process = subprocess.Popen(
                django_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(django_process)
            
            # Start Tailwind watch
            tailwind_cmd = [sys.executable, 'manage.py', 'tailwind', 'start']
            
            self.stdout.write('Starting Tailwind watch...')
            tailwind_process = subprocess.Popen(
                tailwind_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            self.processes.append(tailwind_process)
            
            # Start threads to handle output
            django_thread = threading.Thread(
                target=self.stream_output,
                args=(django_process, 'DJANGO', self.style.SUCCESS)
            )
            tailwind_thread = threading.Thread(
                target=self.stream_output,
                args=(tailwind_process, 'TAILWIND', self.style.WARNING)
            )
            
            django_thread.daemon = True
            tailwind_thread.daemon = True
            
            django_thread.start()
            tailwind_thread.start()
            
            # Open browser after a short delay to ensure server is running
            if not options.get('no_browser'):
                browser_thread = threading.Thread(
                    target=self.open_browser_delayed,
                    args=(options['host'], options['port'])
                )
                browser_thread.daemon = True
                browser_thread.start()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Development environment started!'
                    f'\n✓ Django server: http://{options["host"]}:{options["port"]}'
                    f'\n✓ Tailwind watch: Active'
                    f'\n✓ Browser: {"Opening automatically" if not options.get("no_browser") else "Not opening (--no-browser flag)"}'
                    f'\n\nPress Ctrl+C to stop both processes...\n'
                )
            )
            
            # Wait for processes to complete or be interrupted
            while not self.stop_event.is_set():
                # Check if any process has terminated
                django_poll = django_process.poll()
                tailwind_poll = tailwind_process.poll()
                
                if django_poll is not None:
                    self.stdout.write(
                        self.style.ERROR('Django process terminated unexpectedly')
                    )
                    break
                    
                if tailwind_poll is not None:
                    self.stdout.write(
                        self.style.ERROR('Tailwind process terminated unexpectedly')
                    )
                    break
                
                self.stop_event.wait(1)  # Check every second
                
        except KeyboardInterrupt:
            pass
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting development environment: {e}')
            )
        finally:
            self.cleanup()
    
    def stream_output(self, process, prefix, style_func):
        """Stream output from a subprocess with prefix"""
        try:
            for line in iter(process.stdout.readline, ''):
                if line.strip() and not self.stop_event.is_set():
                    formatted_line = f'[{prefix}] {line.strip()}'
                    self.stdout.write(style_func(formatted_line))
        except Exception:
            pass
    
    def open_browser_delayed(self, host, port):
        """Open browser after a delay to ensure server is ready"""
        try:
            # Wait a bit for the Django server to fully start
            time.sleep(3)
            
            if not self.stop_event.is_set():
                url = f'http://{host}:{port}'
                self.stdout.write(
                    self.style.SUCCESS(f'🌐 Opening browser: {url}')
                )
                webbrowser.open(url)
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not open browser automatically: {e}')
            )
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.stdout.write(
            self.style.WARNING('\n\nShutting down development environment...')
        )
        self.stop_event.set()
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Clean up all processes"""
        for process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    process.terminate()
                    # Wait a bit for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()  # Force kill if it doesn't terminate gracefully
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error terminating process: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('✓ Development environment stopped')
        )
