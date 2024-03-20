# Montec ERP
Sistema Odoo ERP para a empresa Montec

### Clone o repositório da seguinte maneira

    git clone --recurse-submodules --remote-submodules https://github.com/sem-titulo/montec-erp.git --branch=master

### Comandos Importes

    # Verificar serviços rodando em portas de interesse
    sudo lsof -i -P -n | grep 80

    # Matar processo rodando em porta de interesse
    sudo service apache2 stop

    # Inicializar submódulos
    git submodule update --init --recursive
    
    # Atualizar repositório remoto dos submodulos
    git submodule update --recursive --remote
    

    # Atualização recursiva dos submódulos
    git submodule update --recursive
    

    # Pull dos submódulos
    git pull --recurse-submodules

    # Levantando containers
    sudo docker-compose up -d
    # Obs: d é de detached, para não deixar o terminal preso

    # Derrubando containers (CUIDADO: apaga as configurações internas do container)
    sudo docker-compose down
    

    # Olhar os logs dos containers
    sudo docker-compose logs --tail=100
    

    # Iniciar, parar e verificar containers, respectivamente
    sudo docker-compose start
    sudo docker-compose stop
    sudo docker-compose ps
    

    # Subir Odoo atualizando módulos
    sudo docker-compose stop odoo && \
    sudo docker-compose run --rm odoo odoo -c /etc/odoo/odoo.conf -u modulos --stop-after-init && \
    sudo docker-compose restart
    

    # Gerar backup do banco de dados
    export DATABASE=jmenegassi && sudo docker-compose run --rm -e PGPASSWORD=odoo -e DATABASE=$DATABASE db pg_dump -h db -U odoo $DATABASE > /tmp/db-${DATABASE}-$(date +%Y%m%d%H%M).dump


    # Restaurar banco de dados usando um backup
    cat nome_arquivo.dump | sudo docker exec -i nome_container psql -U odoo -d nome_banco


    # Copiar arquivos dump do servidor para máquina local
    scp usuario_maquina@link_servidor:/tmp/db-jemengassi.dump ~/Downloads/db-jmenegassi.dump &&
    scp -r usuario_maquina@link_servidor:/home/ubuntu/projects/jmenegassi-erp/odoo-web-data/filestore/jmenegassi ~/Downloads/jemengassi


    # Listar bancos de dados
    docker exec nome_container psql -U odoo -l


    # Deletar um banco de dados
    docker exec nome_container psql -U odoo drop database jmenegassi


# Conceitos

    + O respositório usa o conceito de sumódulos, ou seja, está lincado a outros respositórios
    + Controle os submóbulos usando o arquivo .gitmodules
    + Use Docker Compose para usar o projeto
    + As configurações do Nginx e do Odoo estão na pasta config
