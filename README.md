# ☁️ Projet Cloud & Edge Computing — Infrastructure OpenStack Complète

![OpenStack](https://img.shields.io/badge/OpenStack-DevStack-red)
![Terraform](https://img.shields.io/badge/Terraform-v1.14.8-purple)
![Ansible](https://img.shields.io/badge/Ansible-2.10.8-red)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue)

## Description

Deploiement d'une infrastructure Cloud privee complete utilisant OpenStack DevStack, avec automatisation via Terraform et Ansible, surveillance SLA et developpement d'une application SaaS de gestion de tickets Help Desk.

Module : Cloud et Edge Computing
Professeur : Prof. C. EL AMRANI
Annee : 2026

---

## Technologies utilisees

| Technologie | Version | Usage |
|---|---|---|
| OpenStack DevStack | 2026.1 | Infrastructure Cloud privee |
| Terraform | v1.14.8 | Infrastructure as Code |
| Ansible | 2.10.8 | Configuration as Code |
| Flask | 3.1.3 | Framework web Python |
| SQLite | 3 | Base de donnees |
| Python | 3.10 | Scripting et backend |
| Ubuntu | 22.04 | Instance SaaS |
| CentOS | 7 | Instance Terraform/Ansible |
| VirtualBox | 7.x | Virtualisation locale |

---

## Structure du projet

partie1-openstack/
    helpdesk/
        app.py          - Backend Flask + Routes
        database.py     - Gestion SQLite
        templates/      - Interface HTML
    cloudtasks/
        app.py

partie2-terraform/
    main.tf             - Deploiement VM CentOS

partie3-sla/
    sla.json            - Contrat SLA 99.5%
    monitor.py          - Script surveillance
    rapport_disponibilite.json

ansible/
    inventory.ini       - Serveurs cibles
    playbook.yml        - Deploiement automatique

---

## Partie 1 - OpenStack + SaaS

### Infrastructure deployee
- OpenStack DevStack installe sur Ubuntu 22.04 VirtualBox
- Services : Nova, Neutron, Keystone, Glance, Horizon
- Instance CirrOS IaaS avec cle SSH et regles securite
- Instance Ubuntu SaaS avec application Flask deployee

### Application Help Desk SaaS
- Systeme de gestion de tickets de support
- 3 roles : Admin / Technicien / Utilisateur
- Backend SQLite avec operations CRUD completes
- Authentification avec sessions Flask
- API REST /api/tickets
- Accessible via navigateur http://172.24.4.154:8080

---

## Partie 2 - Terraform Infrastructure as Code

resource openstack_compute_instance_v2 centos_vm
    name        = centos-terraform
    image_name  = centos-7
    flavor_name = m1.centos
    key_pair    = my-k
    config_drive = true

Commandes executees :
terraform init    - Telecharge provider OpenStack v2.1.0
terraform plan    - Previsiualise : Plan 1 to add
terraform apply   - Cree la VM en 33 secondes

---

## Partie 3 - SLA et Supervision

Objectif SLA :
    disponibilite_cible : 99.5%
    periode_evaluation : journaliere
    frequence_surveillance : 5 minutes

Script de surveillance automatique :
    Verifie toutes les 5 minutes via cron
    Interagit avec Nova API OpenStack
    Calcule : instances_actives / total x 100
    Met a jour sla.json et genere rapport

Resultat :
    instance-cirros   : ACTIVE
    instance-ubuntu   : ACTIVE
    centos-terraform  : ACTIVE
    Disponibilite     : 100.0% SLA RESPECTE

---

## Bonus - Ansible Configuration as Code

Playbook execute sur CentOS :
    Tache 1 : Creer dossier web
    Tache 2 : Deployer page HTML
    Tache 3 : Lancer serveur Python HTTP
    Tache 4 : Verifier reponse HTTP 200

Commandes :
    ansible -i inventory.ini centos_servers -m ping
    ansible-playbook -i inventory.ini playbook.yml
    Resultat : failed=0

---

## Competences demontrees

- Cloud Computing : Deploiement infrastructure privee OpenStack
- Infrastructure as Code : Terraform pour automatiser creation VMs
- Configuration as Code : Ansible pour automatiser configuration
- Developpement Python : Application Flask avec SQLite
- Monitoring et SLA : Surveillance automatique et rapports
- Securite : SSH, groupes de securite, authentification
- Reseau : OVN, IP flottantes, regles pare-feu

---

## Installation rapide

Deploiement OpenStack :
    git clone https://opendev.org/openstack/devstack
    cd devstack
    ./stack.sh

Deploiement Terraform :
    cd partie2-terraform
    terraform init
    terraform apply

Surveillance SLA :
    python3 partie3-sla/monitor.py

Deploiement Ansible :
    cd ansible
    ansible-playbook -i inventory.ini playbook.yml

---

Contact GitHub : https://github.com/KarmasHammam

Projet realise dans le cadre du module Cloud et Edge Computing 2026
