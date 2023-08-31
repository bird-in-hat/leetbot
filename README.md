# Leetbot

# RUN:
Prod:
docker-compose up --build -d

Dev:
docker-compose -f docker-compose.dev.yml up --build
docker exec -u 0 -it leetbot-app-1  /bin/sh
```

# Logs 
* docker-compose logs -t -f <app_..>

# Install docker

```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
apt-cache policy docker-ce
sudo apt install docker-ce -y
sudo usermod -aG docker ${USER}
sudo chmod 666 /var/run/docker.sock
```

* Install docker-compose
```
sudo su
curl -SL https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
sudo apt install gnome-keyring -y
```