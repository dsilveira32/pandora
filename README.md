# PANDORA - Solução Proposta
TODO: Fazer um README de jeito com documentação  
TODO: Melhorar a descrição e o processo de instalação  
FIXME: Este doc está desatualizado depois da realização do nosso trabalho e das novas funcionalidades, atualizar
## Autores
Alexandre Brigolas, 21803430  
Ricardo Nunes, 21805213  

Orientador: Prof. Dr. Pedro Arroz Serra
## Instalação
A instalação deve ser realizada num sistema Linux.


### Instalar Dependências
```
sudo apt update  
sudo apt install python3 -y  
sudo apt install pipenv -y  
sudo apt install redis-server -y  
sudo apt install mysql-server -y  
sudo apt install libmysqlclient-dev -y  
sudo apt install cmake -y  
sudo apt install git -y  
```
### Configurar Redis
```
sudo nano /etc/redis/redis.conf
```
Localizar (Ctrl+w): supervised no  
Substituir por: supervised systemd
``` 
sudo systemctl restart redis.service
```
### Testar Redis 
```
sudo systemctl status redis
redis-cli
ping
exit
```
Validar se o output é PONG.
### Configuração MYSQL
```
sudo su
mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'admin';
CREATE USER 'django'@'localhost' IDENTIFIED BY 'YOUR_PASSWORD';
GRANT ALL PRIVILEGES ON * . * TO 'django'@'localhost';
FLUSH PRIVILEGES;
CREATE SCHEMA pandora;
EXIT
```
root user pw   : admin  
pandora user   : django  
pandora user pw: YOUR_PASSWORD  
### Instalar a Pandora (branch develop)
```
cd /path/to/pandora/
mkdir data
git clone --branch develop https://github.com/parroz/pandora/tree/develop
pipenv shell
cd pandora/
pip install -r requirements.txt
```
### Configurar a Pandora
```
cd pandora/
mv local_settings_example.py local_settings.py
```
O ficheiro local_settings.py tem de ter este aspecto:
```
import os

SOCIAL_AUTH_GITHUB_KEY = 'YOUR_GITHUB_APP_KEY'
SOCIAL_AUTH_GITHUB_SECRET = 'YOUR_GITHUB_APP_SECRET'

DB_USER = 'django'
DB_PASSWORD = 'YOUR_PASSWORD'
SECRET_KEY = 'YOUR_SECRET_KEY'
ALLOWED_HOSTS = ['']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(file)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pandora',
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': 'localhost',
        'PORT': '3306'
    }
}
```
```
cd ..
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata pandora/inital_data.json
python3 manage.py createsuperuser
cd static
gcc ascii.c -o ascii
mv ascii ../../data
```
### Instalar o Docker
[Documentação oficial docker](https://docs.docker.com/get-docker/)
### Criar as imagens
```
cd path/to/pandora/docker_files
./c/build_docker.sh
./java/build_docker.sh
```

### Executar o pandora
```
cd path/to/pandora/pandora
python3 manage.py runserver
```
### Inicializar workers do Celery
Caso este passo não seja tomado, as submissões não serão processadas
```
celery -A pandora worker --loglevel=INFO
```