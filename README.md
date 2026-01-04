# <img src="https://github.com/user-attachments/assets/bfe58e17-99f6-4ad7-af1a-ce25b21cbc6a" alt="PoKéDeX" width="50"/> Pokédex: AI assistant to a world of dreams and adventures
<img width="350" align="right" alt="pokedex" src="https://github.com/user-attachments/assets/e82bf2f9-559e-459f-86ec-394022fbd346" />

The goal of this application is to provide an AI assistant to the world of Pokémon.

It consists in a stack of services orchestrated by Kubernetes. In a nutshell, it encompasses an UI and an inference service. A middleware intercepts the requests between these services, processes them, and augments them with information from a vector DB. The answer is then streamed back to the user.

The project has been set-up such as the European official languages (en, es, fr, de, it) of the game are supported by the assistant. Depending on the request, the assistant uses the appropriate translation of the Pokémon names.

## 📱 Utilization

Interact with the assistant directly from the web UI:

<br>
<div align="center">
<img width="900" alt="Illustration" src="https://github.com/user-attachments/assets/44947d80-fe17-46c2-b064-514eb24ef8f1" />
</div>
<br>

As examplified, the app covers 2 use cases:

- Identify Pokémons from given features.
- Get the features of Pokémons given their name.

## 📋 Specifications

The project is designed to run on a gaming computer with a Nvidia GPU.

It is compatible with GNU/Linux and Windows WSL.

It has been succesfully run on 12Go VRAM + 32Go RAM. It may run with more limited resources with lighter models.

## 🚀 Launch the project

Start by cloning the repo:

```sh
git clone https://github.com/almarch/pokedex.git
cd pokedex
```

The project is designed to run with [k3s](https://github.com/k3s-io/k3s), a light distribution of kubernetes. The [Nvidia container toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) is needed.

</br>
<details><summary>🐋 Nvidia container toolkit installation</summary>

```sh
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
&& curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
sed "s/\$(ARCH)/$(dpkg --print-architecture)/g" | \
sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update
sudo apt install -y nvidia-container-toolkit
```
</details>
</br>

<details><summary>🛞 Set-up Kubernetes</summary>

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
</details>
</br>

<details><summary>🪟 WSL specificities</summary>

In `C:/Users/myUser`, create: `.wslconfig` with:

```conf
[wsl2]
kernelCommandLine = cgroup_no_v1=all systemd.unified_cgroup_hierarchy=1
```

Then, from the WSL, in `/etc/wsl.conf`:

```conf
[boot]
systemd=true
command="/etc/startup.sh"
```

And in `/etc/startup.sh`:

```sh
#!/bin/bash
mount --make-rshared /

if [ ! -e /dev/nvidia0 ]; then
    mkdir -p /dev/nvidia-uvm
    mknod -m 666 /dev/nvidia0 c 195 0
    mknod -m 666 /dev/nvidiactl c 195 255
    mknod -m 666 /dev/nvidia-modeset c 195 254
    mknod -m 666 /dev/nvidia-uvm c 510 0
    mknod -m 666 /dev/nvidia-uvm-tools c 510 1
fi
```

Make it executable:

```sh
sudo chmod +x /etc/startup.sh
```

Restart the WSL. From PowerShell:

```sh
wsl --shutdown
bash
sudo systemctl restart k3s
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
```
</details>
</br>

<details><summary>🗺️ App deployment</summary>

To interact with Kubernetes:

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

Mount the log & notebook volumes:

```sh
sudo mkdir -p /mnt/k3s/logs
sudo mkdir -p /mnt/k3s/notebook
sudo mount --bind "$(pwd)/logs" /mnt/k3s/logs
sudo mount --bind "$(pwd)/notebook" /mnt/k3s/notebook
```

Build the custom images and provide them to k3s:

```sh
docker build -t poke-agent:latest -f dockerfiles/dockerfile.agent .
docker build -t poke-notebook:latest -f dockerfiles/dockerfile.notebook .

docker save poke-agent:latest | sudo k3s ctr images import -
docker save poke-notebook:latest | sudo k3s ctr images import -
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

</details>
</br>

## 🦙 Collect Ollama models

An [Ollama](https://github.com/ollama/ollama) inference service is included in the stack.

```sh
kubectl get pods
```

Pull the models from the agent pod:

```sh
kubectl exec -it <pod-name> -- python -c "from agent.ollama import pull; pull()"
```

The inference is realised by 3 models:

- [Mistral-Nemo](https://huggingface.co/mistralai/Mistral-Nemo-Instruct-2407) is a smart, clean and multilinguistic LLM that understands instructions and tool calling. It is optimized for quantization, and is fast enough on 12 Go VRAM.
- [Embedding-Gemma](https://huggingface.co/google/embeddinggemma-300m) is a state-of-the-art multilinguistic embedding model. It is used for the vector database indexation & retrieval.
- [llama3.2-3B](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct) is a small and performant model with instruction and multilingual capabilities. It is used for the reranking task.

Nemo & Llama are quantized (q8) whereas the embedding model is full-weight. The models can be changed with `agent/agent/config.yaml`.

## 🧩 Fill the Vector DB

A [Qdrant](https://github.com/qdrant/qdrant) vector DB is included in the stack.

It must be filled using the [Jupyter Notebook](https://github.com/jupyter/notebook) service, accessible at https://localhost:8888/lab/workspaces/auto-n/tree/pokemons.ipynb.

To access the notebook, forward the port to localhost:

```sh
kubectl port-forward svc/notebook 8888:8888
```

The Pokémon data come from [this repo](https://github.com/PokeAPI/pokeapi).

<br>
<div align="center">
<img src="notebook/pca.png" width="800" alt="PCA">
</div>
<br>

On this figure, we can have a glance at how a few of the Pokémon records have been ordered on a 2D plane from the embedding space of the English collection.

## 🎮 Access the WebUI

[Open-WebUI](https://github.com/open-webui/open-webui) is included in the stack.

Reach https://localhost and parameterize the interface. Deactivate the user access to the encoder model, and make the LLM accessible to all users.

If needed, set up accounts to the family & friends you would like to share the app with.

<details><summary>🕳️ Tunneling</summary>

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

</details>

## 🔀 Adaptation to other projects

This framework can readily adapt to other RAG/agentic projects.

- The data base should be filled with relevant collections.
- The custom logic is centralised in `agent/agent/Agent.py`.

## ⚖️ License

This work is licensed under GPL-2.0.
