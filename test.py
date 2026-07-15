import subprocess, time, urllib.request
p = subprocess.Popen(['python', 'server.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(2)
try:
    urllib.request.urlopen('http://localhost:8000/api/stats')
except Exception as e:
    print('Err:', e)
time.sleep(1)
p.kill()
out, err = p.communicate()
print('STDOUT:', out.decode())
print('STDERR:', err.decode())
