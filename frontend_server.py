#!/usr/bin/env python3
import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

class SPAHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        self.directory = '/home/runner/workspace/frontend/dist/frontend/browser'
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def do_GET(self):
        # Parse the URL
        parsed_path = urlparse(self.path)
        file_path = parsed_path.path.lstrip('/')
        
        # If it's a file that exists, serve it
        full_path = os.path.join(self.directory, file_path)
        if os.path.isfile(full_path):
            return super().do_GET()
        
        # For SPA routing, serve index.html for non-existent routes
        if not file_path or not os.path.exists(full_path):
            self.path = '/index.html'
        
        return super().do_GET()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # Change to the build directory
    os.chdir('/home/runner/workspace/frontend/dist/frontend/browser')
    
    with HTTPServer(('0.0.0.0', port), SPAHandler) as httpd:
        print(f"Frontend server running on port {port}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()