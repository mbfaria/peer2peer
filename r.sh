case "$1" in
    p1) cd test_env/peer_1; python3 peer.py 5001 key-values-files_peer1 10.0.0.3:5003 10.0.0.2:5002;;
    p2) cd test_env/peer_2; python3 peer.py 5002 key-values-files_peer2 10.0.0.1:5001 10.0.0.5:5005;;
    p3) cd test_env/peer_3; python3 peer.py 5003 key-values-files_peer3 10.0.0.1:5001 10.0.0.5:5005;;
    p4) cd test_env/peer_4; python3 peer.py 5004 key-values-files_peer4 10.0.0.5:5005;;
    p5) cd test_env/peer_5; python3 peer.py 5005 key-values-files_peer5 10.0.0.2:5002 10.0.0.3:5003 10.0.0.4:5004;;
    c1) cd test_env/client_1; python3 cliente.py 10.0.0.1:5001 1,3,4,5,9;;
    c2) cd test_env/client_2; python3 cliente.py 10.0.0.4:5004 5,6,7;;
esac