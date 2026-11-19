"""Use PPSSPP's documented WebSocket debugger for patch runtime tests."""
import websocket,json,uuid,sys,base64
from pathlib import Path
class Debugger:
 def __init__(self):self.w=websocket.create_connection('ws://127.0.0.1:49742/debugger',subprotocols=['debugger.ppsspp.org'],timeout=6)
 def call(self,event,**args):
  ticket=str(uuid.uuid4());self.w.send(json.dumps(dict(event=event,ticket=ticket,**args)))
  while True:
   r=json.loads(self.w.recv())
   if r.get('ticket')==ticket or (event in ('cpu.stepping','cpu.resume') and r.get('event')==event and not r.get('ticket')):
    if r.get('event')=='error':raise RuntimeError(r)
    return r
 def close(self):self.w.shutdown()
 def frame(self,path,resume_after=True,tries=6):
  import time
  for t in range(tries):
   try:
    st=self.call('cpu.status')
    if not st.get('stepping',False): self.call('cpu.stepping')
    r=self.call('gpu.buffer.screenshot',type='uri')
    Path(path).write_bytes(base64.b64decode(r['uri'].split(',',1)[1]))
    if resume_after: self.call('cpu.resume')
    return dict(path=str(path),width=r['width'],height=r['height'])
   except Exception as e:
    self.w.close(); time.sleep(2)
    self.__init__()
    try: self.call('cpu.resume')
    except Exception: pass
    time.sleep(2)
  raise RuntimeError('shot failed')
if __name__=='__main__':
 d=Debugger()
 try:
  if sys.argv[1]=='frame':print(d.frame(sys.argv[2]))
  else:print(json.dumps(d.call(sys.argv[1],**(json.loads(sys.argv[2]) if len(sys.argv)>2 else {}))))
 finally:d.close()

def press(d,btn,n=1,wait=0.6):
    import time
    for _ in range(n):
        d.call('input.buttons.press',button=btn,duration=3); time.sleep(wait)
def readmem(d,addr,size):
    out=b''
    while size>0:
        n=min(size,0x100000)
        r=d.call('memory.read',address=addr,size=n); out+=base64.b64decode(r['base64']); addr+=n; size-=n
    return out
