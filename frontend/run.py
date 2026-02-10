from livereload import Server
import webbrowser

server = Server()

server.watch('*.html')
server.watch('*.css')
server.watch('*.js')

webbrowser.open('http://localhost:5500')

server.serve(port=5500, host='127.0.0.1')