for id in 1 2 3 4 5
do
    cp peer.py test_env/peer_$id/peer.py   
done

for id in 1 2
do
    cp cliente.py test_env/client_$id/cliente.py   
done

# sudo mn --clean