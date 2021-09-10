# Trabalho prático peer2peer

Trabalho prático da matéria de Redes de Computadores da UFMG.

## How-to-run
```
No peer 1:
peer.py 5001 key-values-files_peer1 10.0.0.3:5003 10.0.0.2:5002

No peer 2:
peer.py 5002 key-values-files_peer2 10.0.0.1:5001 10.0.0.5:5005

No peer 3:
peer.py 5003 key-values-files_peer3 10.0.0.1:5001 10.0.0.5:5005

No peer 4:
peer.py 5004 key-values-files_peer4 10.0.0.5:5005

No peer 5: 
peer.py 5004 key-values-files_peer5 10.0.0.2:5002 10.0.0.3:5003 10.0.0.4:5004

No cliente 1 : 
cliente.py 10.0.0.1:5001 5,6,7

No cliente 2 : 
cliente.py 10.0.0.4:5004 1,3,4,5,9


cd test_env/peer_
```
