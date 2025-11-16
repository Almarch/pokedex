# <img src="https://github.com/user-attachments/assets/bfe58e17-99f6-4ad7-af1a-ce25b21cbc6a" alt="PoKéDeX" width="50"/> Pokédex: AI assistant to a world of dreams and adventures
<img width="350" align="right" alt="pokedex" src="https://github.com/user-attachments/assets/e82bf2f9-559e-459f-86ec-394022fbd346" />

The goal of this package is to provide an AI assistant to the world of Pokémon.

It consists in a stack of services orchestrated by k3s.

In a nutshell, it encompasses an UI and an inference service. A custom agentic proxy intercepts the requests between these services, processes them, and eventually augments them with information from a vector DB.

The models have been selected with respect to their minimalism, performance and multilingualism.

The project has been set-up such as French <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Flag_of_France.svg" alt="fr" width="20"/> is the privileged language of the AI assistant.

![Picture1](https://github.com/user-attachments/assets/d3b2aea5-9b25-4bcd-9c53-92093d1b450a)

This project can also be seen as a natural language processing exercice with relatively limited resources, _i.e._ a gaming computer. It requires a Nvidia GPU and it is designed for a Linux server.

To make use of the later, the [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

## 🚀 Launch the project

Start by cloning the repo:

```sh
git clone https://github.com/almarch/pokedex.git
cd pokedex
```

The project is designed to run with a k3s, a light distribution of kubernetes.

```sh
# install brew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.bashrc
eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"

brew install kubectl k9s helm

# install & start k3s
curl -sfL https://get.k3s.io | \
  K3S_KUBECONFIG_MODE=644 \
  INSTALL_K3S_EXEC="--disable traefik" \
  sh -

sudo systemctl stop k3s
sudo systemctl start k3s
```

<!-- Desinstall & reinstall it all:
```sh
sudo /usr/local/bin/k3s-uninstall.sh
sudo rm -rf /var/lib/rancher /var/lib/kubelet
```-->

To load kubectl, k9s & helm:

```sh
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```

Generate all secrets:

```sh
echo "WEBUI_SECRET_KEY=$(cat /dev/urandom | tr -dc 'A-Za-z0-9' | fold -w 32 | head -n 1)" > .env

kubectl create secret generic all-secrets \
  --from-env-file=.env \
  --dry-run=client -o yaml > k8s/secrets.yaml

kubectl apply -f k8s/secrets.yaml
```

Install ingress and cert-manager:

```sh
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add jetstack https://charts.jetstack.io
helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.kind=DaemonSet \
  --set controller.hostNetwork=true \
  --set controller.hostPort.enabled=true \
  --set controller.dnsPolicy=ClusterFirstWithHostNet \
  --set controller.service.type=ClusterIP

helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true
```

Then set-up the nvidia plugin:

```sh
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.14.5/nvidia-device-plugin.yml

kubectl patch daemonset -n kube-system nvidia-device-plugin-daemonset \
  --type merge \
  -p '{"spec":{"template":{"spec":{"runtimeClassName":"nvidia"}}}}'

kubectl rollout restart daemonset/nvidia-device-plugin-daemonset -n kube-system

kubectl describe node | grep -i nvidia
```

Build the init-job images and provide them to k3s:

```sh
docker build -t poke-agent:latest -f dockerfile.agent .
docker build -t poke-notebook:latest -f dockerfile.notebook .

docker save poke-agent:latest | sudo k3s ctr images import -
docker save poke-notebook:latest | sudo k3s ctr images import -
```

Mount the log & notebook volumes:

```sh
sudo mkdir -p /mnt/k3s/logs
sudo mkdir -p /mnt/k3s/notebook
sudo mount --bind "$(pwd)/logs" /mnt/k3s/logs
sudo mount --bind "$(pwd)/notebook" /mnt/k3s/notebook
```

K3s use docker latest images automatically.
Load and deploy all services:

```sh
kubectl apply -R -f k8s/
```

Check the installation status:

```sh
k9s
```

## 🚢 expose the services to localhost

The services need to be exposed to localhost either for local use, either to tunnel them to a VPS. For instance, to expose both the notebook, ollama and qdrant:

```sh
screen

trap "kill 0" SIGINT
kubectl port-forward svc/notebook 8888:8888 &
kubectl port-forward svc/ollama 11434:11434 &
kubectl port-forward svc/qdrant 6333:6333 &
wait
```

<!-- kill all port forward
```sh
pkill -f "kubectl port-forward"
```-->


Then Ctrl+A+D to leave the port-forward screen. The webui should not be port-forwarded as its access is managed by ingress.

## 🦙 Collect Ollama models

Pull the models:

```sh
kubectl get pods
```

From an Ollama pod:

```sh
kubectl exec -it <pod-name> -- ollama pull mistral-nemo:12b-instruct-2407-q4_0
kubectl exec -it <pod-name> -- ollama pull embeddinggemma:300m
```

## 🧩 Fill the Vector DB

A [Qdrant](https://github.com/qdrant/qdrant) vector DB is included in the stack.

It must be filled using the [Jupyter Notebook](https://github.com/jupyter/notebook) service, accessible at https://localhost:8888/lab/workspaces/auto-n/tree/pokemons.ipynb.

Pokémon data come from [this repo](https://github.com/PokeAPI/pokeapi).

<img src="notebook/pca.png" width="1000" alt="PCA">

## 🎮 Access the WebUI

[Open-WebUI](https://github.com/open-webui/open-webui) is included in the stack.

Reach https://localhost and parameterize the interface. Deactivate the encoder model, and make the LLM accessible to all users. If needed, make accounts to the family & friends you would like to share the app with.

## 🔀 Adaptation to other projects

This framework can readily adapt to other agentic projects.

- The data base should be filled with relevant collections.
- The custom agentic logics is centralised in `myAgent/myAgent/Agent.py`.

## 🕳️ Tunneling

<img src="https://github.com/user-attachments/assets/86197798-9039-484b-9874-85f529fba932" width="100px" align="right"/>

Say we need to tunnel the server using a VPS. In other terms, we want some services from the GPU server, let's call it A, to be accessible from anywhere, including from machine C. In the middle, B is the VPS used as a tunnel. 

Name|A  |B  |C  |
---|---|---|---
Description|GPU server  |VPS  |Client  |
Role|Host the services  |Host the tunnel  |Use the Pokédex  | 
User|userA  |root  | doesn't matter   | 
IP|doesn't matter  |11.22.33.44  | doesn't matter  | 

The services we need are:
- The web UI, available at ports 80/443. This port will be exposed on the web.
- The notebook, available at port 8888. This port will remain available for private use only.
- A SSH endpoint. Port 22 of the gaming machine (A) will be exposed through port 2222 of the VPS (B).

### From A) the gaming machine

The VPS must allow gateway ports. In `/etc/ssh/sshd_config`:

```config
AllowTcpForwarding yes
GatewayPorts yes
PermitRootLogin yes
```

Then:

```sh
sudo systemctl restart ssh
```

To access ports 80 and 443, the VPS user must be root. If no root user exists, from the VPS:

```sh
sudo passwd root
```

The ports are then pushed to the VPS from the GPU server:

```sh
screen

sudo ssh -N -R 80:localhost:80 -R 443:localhost:443 -R 8888:localhost:8888 -R 2222:localhost:22 root@11.22.33.44
```

### From B) the VPS

The VPS firewall has to be parameterized:

```sh
sudo ufw allow 2222
sudo ufw allow 443
sudo ufw allow 80
sudo ufw reload
```

The UI is now available world-wide at https://11.22.33.44, using self-signed certificates.

### From C) the client

The jupyter notebook is pulled from the VPS:

```sh
ssh -N -L 8888:localhost:8888 root@11.22.33.44
```

The notebook is now available for the client at https://localhost:8888.

And the VPS is a direct tunnel to the gaming machine A:

```sh
ssh -p 2222 userA@11.22.33.44
```

## ⚖️ License

This work is licensed under GPL-2.0.
