# O objetivo deste readme é apenas por motivo de estudos

	O projeto consiste em uma api rest que apenas "SIMULA" a criação e verificação de instâncias AWS (GET e POST via curl).
	O fluxo de trabalho, de forma resumida e objetiva, dá-se da seguite forma:

--> DevOps aplica o deploy da aplicação instalada em um container (docker).

--> Commita o novo código no repositório local (Git)

--> Commita o novo código no repositório remoto (GitLab)

--> GitLab através de trigers envia uma notificação para o Jenkins, que por sua vez inicia o processo de automação (CI/CD).

--> Através de "Teste de Dependências", Jenkins verifica se o deploy foi aplicado com sucesso em homolog, se sim, o mesmo inicia o deploy em produção.
OBS: O "Teste de Dependência" é realizado através de duas playbooks (Ansible), previamente configuradas para serem executadas no momento em que recebe-se o envento de atualização de repositório remoto (plugin WebHook + Plugin Ansible).

OBS: Vale lembrar que todo a infraestrutura implementada está alocada em instâncias EC2 confiuguradas numa mesma VPC.

Vamos então às configurações realizadas:

################################
################################


1) Deploy da aplicação

- Criação de instância EC2 com AMI Amazon-Linux que hospedará o container da aplicação (docker)

#yum install update 
#yum install docker-engine

#docker run -dit --name api_homolog --hostname api_homolog -p 8080:8080 --restart always centos /bin/bash

--(longando no container e deploiando a aplicação) 

#docker attach api_homolog

#yum install epel-release
 
#yum install python-pip 
 
#pip install virtualenv 
 
#mkdir /var/tmp/my_app 
 
#cd /var/tmp/my_app 
 
#virtualenv flask
 
#flask/bin/pip install flask
 
#vim my_app.py
-- inserir o conteudo do arquivo my_app (que ja coloquei no repositorio api-python)

#chmod +x my_app.py 


-- Iniciando a aplicação 
#/var/tmp/my_app/my_app.py & 

-- Stopando a aplicação
#kill -15 `ps -ef | grep my_app.py | cut -c12-16`


--> Para simplificar, nosso deploy (atualização da app) consiste apenas em criar uma novo instância, adicionado uma linha como a descrita abaixo no arquivo my_app.py:
{'id': (verificar_ultimo_ID_criado),'titulo': u'EC2 - T2 Large','descricao': u'MEM:64MB PROC:24Vcpu HD:500GB NFS','done': False},

OU 

curl -i -H "Content-Type: application/json" -X POST -d '{"titulo":"EC2 - T2 SMALL", "descricao":"MEM:8Gb PROC:4Vcpu HD:100GB NFS"}' http://$IP_APP:8080/todo/api/v1/tasks/ 

Para criar (apenas simulação) uma nova instância, você pode fazer das duas formas descritas acima (via edição do aquivo ou via POST)


Para visualizar uma instância criada, você também pode fazer de duas formas:

- Todas as instancias: curl -i http://$IP_APP:8080/todo/api/v1/tasks/
- Listar por ID: http://$IP_APP:8080/todo/api/v1/tasks/$ID_DA_INSTANCIA



OBS: Alterar a diretiva PermitRootLogin de "no" para "yes" no arquivo /etc/ssh/sshd_config (configurações para o ansible)



################################
################################


2) Instalação/configuração do Ansible 


-- Instalado no mesmo servidor Jenkins (EC2 - Ubuntu)

#apt-get update -y
 
#apt-get install -y ansible

-- Configurar as chaves para executar os comandos no application server com segurança sem solicitar senha:

#ssh-keygen
(/var/tmp/chave - chave.pem / chave.pub)

#ssh-copy-id -i /var/tmp/chave/chave.pub root@ip_da_app

#ssh -i /var/tmp/chave/chave.pem root@ip_da_app  (apenas para testar o acesso via chaves) 



-- Configurar o ansible

#vim /etc/ansible/ansible.cfg

inventory = /etc/ansible/hosts (voce deve criar o arquivo "hosts" e inserir os hosts a serem controlados pelo ansible) 
private_key_file = /var/tmp/chave/chave.pem (inserir o path da sua chave privada) 



- Criar/configurar as playbooks a serem executadas pelo Jenkins no momento que este, receber do GitLab a notificação de push no repositório da app.

#mkdir -p /etc/ansible/homolog/api-rest/
#mkdir -p /etc/ansible/prod/api-rest/

Para cada diretorio, deve-se criar dois arquivos (main.yml e docker.yml), o conteudo de ambos será postado no repositório "ansible"

Mas pra dar um overview, a playbook de homolog trabalha com ambiente transitório, ou seja, cria sobe a app, testa e se estiver tudo ok, clona o container pra produção e em seguida remove, na proxima versao, o ambiente será recriado do "zero".



################################
################################


3) Armazenar os repositórios remotos GitLab 


--> Criacao/configuracao da instancia ubuntu-server para instalacao/configuracao dos repositorios remotos (GitLab)

#apt-get install curl openssh-server ca-certificates postfix
 
#curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
 
#apt-get install gitlab-ce

- Alterar porta de 80 para 8088 no arquivo /etc/gitlab/gitlab.rb
external_url 'http://ip_do_servidor:8088'

#gitlab-ctl reconfigure

#gitlab-ctl restart 

- A partir daqui, as configura são via interface web do gitlab

- configurar senha inicial root
- a partir da senha de root, criar um usuário para administrar os repositórios (diogo.elias)
- criar novo projeto (api-pyhton) -- http://diogo.elias@meu_ip:8088/diogo.elias/api-python.git
- configurações gerais do respositório:

# (no servidor da aplicação)

#yum install -y git
 
#git config --global user.name "Diogo Elias"
 
#git config --global user.email "diogo.elias@teste.com.br"
 
#cd /var/tmp/my_app/
 
#git init
 
#git remote add origin http://diogo.elias@gitlab:8088/diogo.elias/api-python.git
 
#git add .
 
#git commit
 
#git push -u origin master


-- Configurando gitlab para enviar notificações (hook) para o Jenkins tomar alguma ação

Na pagigna inicial, clique no projeto "api-python" 
--> settings --> Integrations --> Add WebHook --> insira a url que o gitlab vai "chamar" para avisar ao jenkins sobre novos pushs "http://IP_DO_jenkins:8080/gitlab/build_now"


-- Configurado a relação de confiança (SSH) entre gitlab e jenkins 

Na pagigna inicial, clique no projeto "api-python" 
--> settings(canto superior direito) --> ssh keys --> cole o conteudo da chave publica gerada no ansible --> salvar

Pronto, já temos o gitlab "avisando" ao Jenkins e temos a relação de confiança estabelecida entre os dois.

Temos também, repositório local e remoto já estão devidamente configurados



################################
################################


4) Instalação/configuração Jenkins

- Criação de instância EC2 com AMI Amazon-Linux que hospedará os serviços de integracão e entrega contínuas (jenkins) (instalado no mesmo servidor que Ansible)

#wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | sudo apt-key add -
 
#sudo sh -c 'echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list'
 
#sudo apt-get update
 
#sudo apt-get install jenkins
 
#logar no jenkins com a senha inicial informada pelo próprio via web
 
#Alterar a senha por uma de sua preferência

-- Instalação/configuração de plugins (WebHook + ansible plugin + pipeline plugin, este ultimo serve para dar uma visão detalhada do processo executado).

Na tela inicial, clicar em:

--> gerenciar jenkins --> gerenciar plugins --> instalar os plugins "Ansible plugin" + "Build Pipeline Plugin" + "Gitlab Hook Plugin" + "Git Plugin" 
--> marcar a combo: "reiniciar após a instalaçãos dos plugins".

-- Configurar a relação de confiança (via SSH) entre Jenkins e GitLab

Na pagina inicia, clicar em:

--> credentials --> add credentials --> kind: "ssh username with private key" --> scope (global) --> Private Key: "inserir o conteudo da chave privada que voce gerou para o ansible e escolher o usuario que vai "comunicar" com o gitlab" --> username: "git" --> Salvar


-- Configurando as jobs para executarem as playbooks

Na pagina inicial:

--> novo job --> nome: Deploy Homolog --> construir um projeto free-style --> breve descrição --> gerenciamento de codigo fonte: GIT --> repsitory URL --> git@gitlab:diogo.elias/api-python.git --> credentials: git --> Build: Invoke Ansible Playbook --> Playbook path: /etc/ansible/homolog/api-rest/main.yml --> Ações de pós build: Invocar o job "Deploy Produção" em caso de sucesso
