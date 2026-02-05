# Remove leftover veth interfaces (if they exist)
sudo ip link delete veth-host 
sudo ip link delete veth-ns   

# Also clean up the namespace if it was partially created
sudo ip netns delete addedtailscalefunnel8 

# Remove any leftover iptables rule (just in case)
sudo iptables -t nat -D POSTROUTING -s 192.168.200.0/24 -j MASQUERADE 
