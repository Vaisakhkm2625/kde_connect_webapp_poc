sudo ip netns add ns-app1
sudo ip link add veth-app1 type veth peer name veth-app1-h
sudo ip link set veth-app1 netns ns-app1
sudo ip netns exec ns-app1 ip addr add 192.168.77.2/24 dev veth-app1
sudo ip netns exec ns-app1 ip link set veth-app1 up
sudo ip netns exec ns-app1 ip link set lo up

# Run tailscale inside the namespace (userspace mode is easiest)
sudo ip netns exec ns-app1 \
  tailscaled --tun=userspace-networking --state=/var/lib/tailscale/app1.state --socket=/var/run/tailscale/app1.sock &
