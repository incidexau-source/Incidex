#!/usr/bin/env python3
"""
Simple HTTP server for localhost development
Serves the LGBTIQ+ Hate Crime Map project
"""

print("DEBUG: Starting server...")
print("DEBUG: Importing modules...")

import http.server
import socketserver
import socket
import threading
import os
import sys
from pathlib import Path

print("DEBUG: Modules imported successfully")
print("DEBUG: Setting up paths and config...")

# Get the directory where this script is located
BASE_DIR = Path(__file__).parent.absolute()
PORT = 8000

print(f"DEBUG: BASE_DIR = {BASE_DIR}")
print(f"DEBUG: PORT = {PORT}")
print("DEBUG: Configuration complete")

print("DEBUG: Defining ThreadedHTTPServer class...")

class ThreadedHTTPServer(socketserver.TCPServer):
    """Threaded HTTP server with proper socket options"""
    daemon_threads = True
    allow_reuse_address = True
    
    def server_bind(self):
        """Override to set socket options before binding"""
        print("DEBUG: ThreadedHTTPServer.server_bind() called")
        try:
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            print("DEBUG: SO_REUSEADDR set")
            super().server_bind()
            print("DEBUG: server_bind() completed")
        except Exception as e:
            print(f"ERROR in server_bind(): {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise

print("DEBUG: Defining CustomHTTPRequestHandler class...")

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler with CORS support and comprehensive error handling"""
    
    print("DEBUG: RequestHandler class definition started")
    
    def __init__(self, *args, **kwargs):
        print("DEBUG: __init__ called")
        sys.stdout.flush()
        print(f"DEBUG: __init__ args count: {len(args)}")
        print(f"DEBUG: __init__ kwargs keys: {list(kwargs.keys())}")
        sys.stdout.flush()
        try:
            print("DEBUG: About to call super().__init__")
            sys.stdout.flush()
            # Use directory parameter for Python 3.7+
            if sys.version_info >= (3, 7):
                print(f"DEBUG: Python 3.7+, using directory={BASE_DIR}")
                sys.stdout.flush()
                super().__init__(*args, directory=str(BASE_DIR), **kwargs)
            else:
                print("DEBUG: Python < 3.7, using default init")
                sys.stdout.flush()
                super().__init__(*args, **kwargs)
            print("DEBUG: super().__init__ completed successfully")
            sys.stdout.flush()
        except Exception as e:
            print(f"ERROR in __init__: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            raise
    
    def guess_type(self, path):
        """Override to set proper MIME types with error handling"""
        try:
            mimetype, encoding = super().guess_type(path)
            
            # Fix MIME types for common data formats
            if path.endswith('.csv'):
                return 'text/csv', encoding
            elif path.endswith('.geojson'):
                return 'application/geo+json', encoding
            elif path.endswith('.json'):
                return 'application/json', encoding
            
            return mimetype, encoding
        except Exception as e:
            print(f"ERROR in guess_type for path '{path}': {type(e).__name__}: {e}")
            return 'application/octet-stream', None
    
    def setup(self):
        """Override setup() to catch connection setup errors"""
        print("DEBUG: setup() called")
        try:
            super().setup()
            print("DEBUG: setup() completed")
        except Exception as e:
            print(f"ERROR in setup(): {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def end_headers(self):
        """Add CORS headers for local development with error handling"""
        print("DEBUG: end_headers() called")
        try:
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', '*')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            print("DEBUG: About to call super().end_headers()")
            super().end_headers()
            print("DEBUG: super().end_headers() completed")
        except Exception as e:
            print(f"ERROR in end_headers: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            # Try to send basic headers even if CORS fails
            try:
                super().end_headers()
            except Exception as e2:
                print(f"ERROR in fallback end_headers: {type(e2).__name__}: {e2}")
                import traceback
                traceback.print_exc()
    
    def send_response(self, code, message=None):
        """Override send_response() to add debugging"""
        print(f"DEBUG: send_response() called with code={code}, message={message}")
        try:
            super().send_response(code, message)
            print(f"DEBUG: send_response() completed for code={code}")
        except Exception as e:
            print(f"ERROR in send_response: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def send_header(self, keyword, value):
        """Override send_header() to add debugging"""
        print(f"DEBUG: send_header() called: {keyword} = {value}")
        try:
            super().send_header(keyword, value)
        except Exception as e:
            print(f"ERROR in send_header: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def do_OPTIONS(self):
        """Handle preflight CORS requests with error handling"""
        print("DEBUG: do_OPTIONS() called")
        try:
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            print(f"ERROR in do_OPTIONS: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.send_error(500, "Internal Server Error")
            except:
                pass
    
    def handle(self):
        """Override handle() to catch errors before request processing"""
        print("DEBUG: handle() called")
        sys.stdout.flush()
        try:
            print("DEBUG: About to call super().handle()")
            sys.stdout.flush()
            super().handle()
            print("DEBUG: super().handle() completed")
            sys.stdout.flush()
        except BrokenPipeError as e:
            print(f"ERROR: BrokenPipeError in handle() - client disconnected: {e}")
            sys.stdout.flush()
        except ConnectionResetError as e:
            print(f"ERROR: ConnectionResetError in handle() - connection reset: {e}")
            sys.stdout.flush()
        except Exception as e:
            print(f"ERROR in handle(): {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            try:
                self.send_error(500, "Internal Server Error")
            except:
                pass
    
    def handle_one_request(self):
        """Override handle_one_request() to catch errors during request parsing"""
        print("DEBUG: handle_one_request() called")
        sys.stdout.flush()
        try:
            if hasattr(self, 'raw_requestline'):
                print(f"DEBUG: Request line: {self.raw_requestline}")
            else:
                print("DEBUG: raw_requestline not available yet")
            sys.stdout.flush()
            print("DEBUG: About to call super().handle_one_request()")
            sys.stdout.flush()
            super().handle_one_request()
            print("DEBUG: super().handle_one_request() completed")
            sys.stdout.flush()
        except BrokenPipeError as e:
            print(f"ERROR: BrokenPipeError in handle_one_request() - client disconnected: {e}")
            sys.stdout.flush()
        except ConnectionResetError as e:
            print(f"ERROR: ConnectionResetError in handle_one_request() - connection reset: {e}")
            sys.stdout.flush()
        except Exception as e:
            print(f"ERROR in handle_one_request(): {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            try:
                self.send_error(500, "Internal Server Error")
            except:
                pass
    
    def do_GET(self):
        """Handle GET requests with comprehensive error handling"""
        print("DEBUG: do_GET() called")
        print(f"DEBUG: self.path = {self.path}")
        print(f"DEBUG: self.command = {self.command}")
        try:
            # Get the requested path
            print("DEBUG: About to call translate_path()")
            path = self.translate_path(self.path)
            print(f"DEBUG: Handling GET request for: {self.path} -> {path}")
            
            # Check if path is within BASE_DIR (security)
            try:
                path_obj = Path(path).resolve()
                base_obj = Path(BASE_DIR).resolve()
                if not str(path_obj).startswith(str(base_obj)):
                    print(f"ERROR: Path outside base directory: {path}")
                    self.send_error(403, "Forbidden")
                    return
            except Exception as e:
                print(f"ERROR checking path security: {type(e).__name__}: {e}")
                self.send_error(400, "Bad Request")
                return
            
            # Check if file exists
            if not os.path.exists(path):
                print(f"ERROR: File not found: {path}")
                self.send_error(404, "File Not Found")
                return
            
            # Check if it's a directory
            if os.path.isdir(path):
                # Try to serve index.html if it exists
                index_path = os.path.join(path, 'index.html')
                if os.path.exists(index_path):
                    path = index_path
                else:
                    # List directory (if allowed)
                    self.send_error(403, "Directory listing not allowed")
                    return
            
            # Check file permissions
            if not os.access(path, os.R_OK):
                print(f"ERROR: Permission denied: {path}")
                self.send_error(403, "Permission Denied")
                return
            
            # Get file size
            try:
                file_size = os.path.getsize(path)
            except OSError as e:
                print(f"ERROR getting file size for {path}: {type(e).__name__}: {e}")
                self.send_error(500, "Internal Server Error")
                return
            
            # Determine content type (manual detection to fix Python 3.14 bug)
            print(f"DEBUG: Determining MIME type for path: {self.path}")
            if self.path.endswith('.html'):
                content_type = 'text/html; charset=utf-8'
                encoding = 'utf-8'
            elif self.path.endswith('.css'):
                content_type = 'text/css; charset=utf-8'
                encoding = 'utf-8'
            elif self.path.endswith('.js'):
                content_type = 'application/javascript; charset=utf-8'
                encoding = 'utf-8'
            elif self.path.endswith('.json'):
                content_type = 'application/json; charset=utf-8'
                encoding = 'utf-8'
            elif self.path.endswith('.csv'):
                content_type = 'text/csv; charset=utf-8'
                encoding = 'utf-8'
            elif self.path.endswith('.geojson'):
                content_type = 'application/geo+json; charset=utf-8'
                encoding = 'utf-8'
            elif self.path.endswith('.svg'):
                content_type = 'image/svg+xml; charset=utf-8'
                encoding = 'utf-8'
            elif self.path.endswith('.png'):
                content_type = 'image/png'
                encoding = None
            elif self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
                content_type = 'image/jpeg'
                encoding = None
            elif self.path.endswith('.gif'):
                content_type = 'image/gif'
                encoding = None
            elif self.path.endswith('.ico'):
                content_type = 'image/x-icon'
                encoding = None
            else:
                # Fallback: try guess_type() but catch errors
                try:
                    mimetype, encoding = self.guess_type(path)
                    content_type = mimetype
                    if encoding:
                        content_type += f'; charset={encoding}'
                except Exception as e:
                    print(f"ERROR determining MIME type for {path}: {type(e).__name__}: {e}")
                    content_type = 'application/octet-stream'
                    encoding = None
            
            print(f"DEBUG: Content-Type determined: {content_type}")
            
            # Read and send file
            try:
                # Open file with proper encoding handling
                if encoding and encoding.lower() in ['utf-8', 'utf8']:
                    with open(path, 'r', encoding='utf-8', errors='replace') as f:
                        content = f.read()
                    content_bytes = content.encode('utf-8')
                else:
                    # Binary mode for non-text files
                    with open(path, 'rb') as f:
                        content_bytes = f.read()
                
                # Send response
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content_bytes)))
                self.end_headers()
                
                # Send file content
                self.wfile.write(content_bytes)
                
                print(f"DEBUG: Successfully served {self.path} ({len(content_bytes)} bytes)")
                
            except UnicodeDecodeError as e:
                print(f"ERROR: Unicode decode error for {path}: {e}")
                # Try binary mode as fallback
                try:
                    with open(path, 'rb') as f:
                        content_bytes = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/octet-stream')
                    self.send_header('Content-Length', str(len(content_bytes)))
                    self.end_headers()
                    self.wfile.write(content_bytes)
                except Exception as e2:
                    print(f"ERROR in fallback binary read: {type(e2).__name__}: {e2}")
                    self.send_error(500, "Internal Server Error")
                    
            except PermissionError as e:
                print(f"ERROR: Permission error reading {path}: {e}")
                self.send_error(403, "Permission Denied")
                
            except FileNotFoundError as e:
                print(f"ERROR: File not found (race condition?) {path}: {e}")
                self.send_error(404, "File Not Found")
                
            except IOError as e:
                print(f"ERROR: I/O error reading {path}: {type(e).__name__}: {e}")
                self.send_error(500, "Internal Server Error")
                
            except Exception as e:
                print(f"ERROR: Unexpected error serving {path}: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                try:
                    self.send_error(500, "Internal Server Error")
                except:
                    pass
                    
        except Exception as e:
            print(f"ERROR: Critical error in do_GET: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.send_error(500, "Internal Server Error")
            except:
                pass
    
    def do_HEAD(self):
        """Handle HEAD requests with error handling"""
        try:
            # Reuse do_GET logic but don't send body
            path = self.translate_path(self.path)
            
            if not os.path.exists(path):
                self.send_error(404, "File Not Found")
                return
            
            if os.path.isdir(path):
                self.send_error(403, "Directory listing not allowed")
                return
            
            if not os.access(path, os.R_OK):
                self.send_error(403, "Permission Denied")
                return
            
            # Determine content type (same manual detection as do_GET)
            if self.path.endswith('.html'):
                content_type = 'text/html; charset=utf-8'
            elif self.path.endswith('.css'):
                content_type = 'text/css; charset=utf-8'
            elif self.path.endswith('.js'):
                content_type = 'application/javascript; charset=utf-8'
            elif self.path.endswith('.json'):
                content_type = 'application/json; charset=utf-8'
            elif self.path.endswith('.csv'):
                content_type = 'text/csv; charset=utf-8'
            elif self.path.endswith('.geojson'):
                content_type = 'application/geo+json; charset=utf-8'
            elif self.path.endswith('.svg'):
                content_type = 'image/svg+xml; charset=utf-8'
            elif self.path.endswith('.png'):
                content_type = 'image/png'
            elif self.path.endswith('.jpg') or self.path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif self.path.endswith('.gif'):
                content_type = 'image/gif'
            elif self.path.endswith('.ico'):
                content_type = 'image/x-icon'
            else:
                # Fallback: try guess_type() but catch errors
                try:
                    mimetype, encoding = self.guess_type(path)
                    content_type = mimetype
                    if encoding:
                        content_type += f'; charset={encoding}'
                except Exception as e:
                    print(f"ERROR determining MIME type for {path}: {type(e).__name__}: {e}")
                    content_type = 'application/octet-stream'
            
            file_size = os.path.getsize(path)
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(file_size))
            self.end_headers()
            
        except Exception as e:
            print(f"ERROR in do_HEAD: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            try:
                self.send_error(500, "Internal Server Error")
            except:
                pass
    
    def log_message(self, format, *args):
        """Custom logging to show requests"""
        try:
            print(f"[{self.address_string()}] {format % args}")
        except Exception as e:
            print(f"ERROR in log_message: {type(e).__name__}: {e}")
    
    def log_error(self, format, *args):
        """Override to log errors with more detail"""
        try:
            print(f"ERROR [{self.address_string()}] {format % args}")
            import traceback
            traceback.print_exc()
        except Exception as e:
            print(f"ERROR in log_error: {type(e).__name__}: {e}")

def main():
    """Start the localhost server"""
    print("DEBUG: Entering main() function")
    print("DEBUG: Printing startup banner...")
    
    print("=" * 60)
    print("LGBTIQ+ Hate Crime Map - Local Development Server")
    print("=" * 60)
    print(f"\nServing from: {BASE_DIR}")
    print(f"\nServer running at:")
    print(f"  http://localhost:{PORT}/")
    print(f"  http://127.0.0.1:{PORT}/")
    print(f"\nMain pages:")
    print(f"  http://localhost:{PORT}/visualizations/index.html")
    print(f"  http://localhost:{PORT}/visualizations/map.html")
    print(f"  http://localhost:{PORT}/visualizations/statistics.html")
    print(f"\nPress Ctrl+C to stop the server")
    print("=" * 60)
    print()
    
    print("DEBUG: Banner printed")
    print(f"DEBUG: Attempting to create ThreadedHTTPServer on port {PORT}...")
    
    try:
        print("DEBUG: Creating ThreadedHTTPServer instance...")
        with ThreadedHTTPServer(("localhost", PORT), CustomHTTPRequestHandler) as httpd:
            print(f"DEBUG: ThreadedHTTPServer created successfully!")
            print(f"Server started successfully on port {PORT}")
            print("DEBUG: Starting serve_forever()...")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped by user.")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48 or e.errno == 98:  # Address already in use
            print(f"\nError: Port {PORT} is already in use.")
            print(f"Please stop any other server running on port {PORT} or change the PORT variable.")
        else:
            print(f"\nError starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    print("DEBUG: Script executed as main, calling main()...")
    main()
    print("DEBUG: main() returned (should not reach here)")
