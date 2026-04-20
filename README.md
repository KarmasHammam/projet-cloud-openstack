
# Projet Cloud et Edge Computing - Infrastructure OpenStack Complete

![OpenStack](https://img.shields.io/badge/OpenStack-DevStack-red)
![Terraform](https://img.shields.io/badge/Terraform-v1.14.8-purple)
![Ansible](https://img.shields.io/badge/Ansible-2.10.8-red)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green)
![Python](https://img.shields.io/badge/Python-3.10-blue)

## Description

Deploiement d'une infrastructure Cloud privee complete utilisant OpenStack DevStack, avec automatisation via Terraform et Ansible, surveillance SLA et developpement d'une application SaaS Help Desk.

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

---

## Structure du projet

    projet-cloud-openstack/
    |
    |-- partie1-openstack/
    |   |-- helpdesk/
    |   |   |-- app.py
    |   |   |-- database.py
    |   |   `-- templates/
    |   `-- cloudtasks/
    |       `-- app.py
    |
    |-- partie2-terraform/
    |   `-- main.tf
    |
    |-- partie3-sla/
    |   |-- sla.json
    |   |-- monitor.py
    |   `-- rapport_disponibilite.json
    |
    `-- ansible/
        |-- inventory.ini
        `-- playbook.yml

---

## Partie 1 - OpenStack + SaaS

### Infrastructure deployee
- OpenStack DevStack installe sur Ubuntu 22.04 via VirtualBox
- Services deployes : Nova, Neutron, Keystone, Glance, Horizon
- Instance CirrOS (IaaS) avec cle SSH et regles de securite
- Instance Ubuntu (SaaS) avec application Flask deployee

### Application Help Desk
- Systeme de gestion de tickets de support technique
- 3 roles : Admin / Technicien / Utilisateur
- Backend SQLite avec operations CRUD completes
- Authentification avec sessions Flask et passwords haches
- API REST disponible sur /api/tickets
- Accessible via : http://172.24.4.154:8080

---

## Partie 2 - Terraform Infrastructure as Code

```hcl
resource "openstack_compute_instance_v2" "centos_vm" {
  name         = "centos-terraform"
  image_name   = "centos-7"
  flavor_name  = "m1.centos"
  key_pair     = "my-k"
  config_drive = true
  network {
    name = "private"
  }
}
```

```bash
terraform init    # Telecharge provider OpenStack v2.1.0
terraform plan    # Plan: 1 to add
terraform apply   # VM creee en 33 secondes
```

---

## Partie 3 - SLA et Supervision

### Objectif SLA
```json
{
  "disponibilite_cible": 99.5,
  "periode_evaluation": "journaliere",
  "frequence_surveillance": "5 minutes"
}
```

### Resultat monitoring
instance-cirros   : ACTIVE
instance-ubuntu   : ACTIVE
centos-terraform  : ACTIVE
Disponibilite     : 100.0% - SLA RESPECTE

### Execution automatique
```bash
*/5 * * * * python3 /home/stack/monitor.py >> /home/stack/monitor.log 2>&1
```

---

## Bonus - Ansible Configuration as Code

```yaml
tasks:
  - name: Creer dossier web
  - name: Deployer page HTML
  - name: Lancer serveur Python HTTP
  - name: Verifier reponse HTTP 200
```

```bash
ansible -i inventory.ini centos_servers -m ping
# centos-terraform | SUCCESS => pong

ansible-playbook -i inventory.ini playbook.yml
# failed=0 - Serveur web ACTIF http://172.24.4.24:8888
```

---

## Competences demontrees

- **Cloud Computing** : Deploiement infrastructure privee OpenStack
- **Infrastructure as Code** : Terraform pour automatiser creation VMs
- **Configuration as Code** : Ansible pour automatiser configuration
- **Developpement Python** : Application Flask avec SQLite
- **Monitoring et SLA** : Surveillance automatique et rapports
- **Securite** : SSH, groupes de securite, authentification
- **Reseau** : OVN, IP flottantes, regles pare-feu

---

## Contact

**GitHub** : [KarmasHammam](https://github.com/KarmasHammam)

