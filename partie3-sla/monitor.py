#!/usr/bin/env python3
"""
Script de surveillance SLA OpenStack
Projet Cloud et Edge Computing — Prof. C. EL AMRANI
Exécution automatique toutes les 5 minutes
"""

import json
import os
import subprocess
import datetime
import sys

# ─────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────
SLA_FILE = os.path.expanduser('~/sla.json')
RAPPORT_FILE = os.path.expanduser('~/rapport_disponibilite.json')
OPENRC = '/opt/devstack/openrc'
INSTANCES = ['instance-cirros', 'instance-ubuntu', 'centos-terraform']
DISPONIBILITE_CIBLE = 99.5

# ─────────────────────────────────────────
# AUTHENTIFICATION OPENSTACK
# ─────────────────────────────────────────
def get_openstack_env():
    """Récupère les variables d'environnement OpenStack"""
    env = os.environ.copy()
    env['OS_AUTH_URL'] = 'http://192.168.56.101/identity/v3'
    env['OS_USERNAME'] = 'admin'
    env['OS_PASSWORD'] = 'admin'
    env['OS_PROJECT_NAME'] = 'demo'
    env['OS_USER_DOMAIN_ID'] = 'default'
    env['OS_PROJECT_DOMAIN_ID'] = 'default'
    env['OS_IDENTITY_API_VERSION'] = '3'
    env['OS_AUTH_TYPE'] = 'password'
    return env

# ─────────────────────────────────────────
# SURVEILLANCE DES INSTANCES
# ─────────────────────────────────────────
def get_instance_status(instance_name, env):
    """Récupère le statut d'une instance via Nova API"""
    cmd = f'openstack server show {instance_name} -f value -c status'
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, env=env
    )
    status = result.stdout.strip()
    if not status:
        return 'UNKNOWN'
    return status

def check_all_instances(env):
    """Vérifie l'état de toutes les instances"""
    results = []
    active_count = 0
    
    for instance in INSTANCES:
        status = get_instance_status(instance, env)
        is_available = status in ['ACTIVE', 'RUNNING']
        
        if is_available:
            active_count += 1
            
        results.append({
            'instance': instance,
            'status': status,
            'disponible': is_available,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
        print(f"  → {instance}: {status} {'✅' if is_available else '❌'}")
    
    return results, active_count

# ─────────────────────────────────────────
# CALCUL DISPONIBILITÉ
# ─────────────────────────────────────────
def calculer_disponibilite(active_count, total_count):
    """Calcule le taux de disponibilité"""
    if total_count == 0:
        return 0.0
    return round((active_count / total_count) * 100, 2)

# ─────────────────────────────────────────
# MISE À JOUR SLA
# ─────────────────────────────────────────
def mettre_a_jour_sla(disponibilite, results):
    """Met à jour le fichier sla.json avec le rapport"""
    with open(SLA_FILE, 'r') as f:
        sla = json.load(f)
    
    objectif_respecte = disponibilite >= DISPONIBILITE_CIBLE
    
    if disponibilite >= 99.5:
        statut = '✅ NOMINAL'
    elif disponibilite >= 98.0:
        statut = '⚠️ AVERTISSEMENT'
    else:
        statut = '❌ CRITIQUE'
    
    sla['sla']['rapport'] = {
        'derniere_verification': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'disponibilite_calculee': disponibilite,
        'disponibilite_cible': DISPONIBILITE_CIBLE,
        'objectif_respecte': objectif_respecte,
        'statut': statut,
        'details': results
    }
    
    with open(SLA_FILE, 'w') as f:
        json.dump(sla, f, indent=2, ensure_ascii=False)
    
    return objectif_respecte, statut

# ─────────────────────────────────────────
# GÉNÉRATION RAPPORT
# ─────────────────────────────────────────
def generer_rapport(disponibilite, results, objectif_respecte, statut):
    """Génère un rapport détaillé de disponibilité"""
    rapport = {
        'rapport_disponibilite': {
            'titre': 'Rapport de Disponibilité OpenStack',
            'module': 'Cloud et Edge Computing',
            'professeur': 'Prof. C. EL AMRANI',
            'date': datetime.datetime.now().strftime('%Y-%m-%d'),
            'heure': datetime.datetime.now().strftime('%H:%M:%S'),
            'resultats': {
                'disponibilite_calculee': disponibilite,
                'disponibilite_cible': DISPONIBILITE_CIBLE,
                'objectif_respecte': objectif_respecte,
                'statut_global': statut,
                'instances_actives': sum(1 for r in results if r['disponible']),
                'instances_total': len(results),
                'details_instances': results
            },
            'conclusion': (
                f"L'objectif de disponibilité de {DISPONIBILITE_CIBLE}% est RESPECTÉ."
                if objectif_respecte else
                f"L'objectif de disponibilité de {DISPONIBILITE_CIBLE}% N'EST PAS RESPECTÉ."
            )
        }
    }
    
    with open(RAPPORT_FILE, 'w') as f:
        json.dump(rapport, f, indent=2, ensure_ascii=False)
    
    return rapport

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    print("=" * 60)
    print("  SURVEILLANCE SLA OPENSTACK")
    print(f"  {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Authentification
    print("\n📡 Connexion à OpenStack...")
    env = get_openstack_env()
    
    # Vérification instances
    print(f"\n🔍 Vérification de {len(INSTANCES)} instances...")
    results, active_count = check_all_instances(env)
    
    # Calcul disponibilité
    disponibilite = calculer_disponibilite(active_count, len(INSTANCES))
    print(f"\n📊 Disponibilité calculée : {disponibilite}%")
    print(f"   Objectif cible         : {DISPONIBILITE_CIBLE}%")
    
    # Mise à jour SLA
    objectif_respecte, statut = mettre_a_jour_sla(disponibilite, results)
    print(f"   Statut                 : {statut}")
    
    # Génération rapport
    generer_rapport(disponibilite, results, objectif_respecte, statut)
    
    print(f"\n📄 Fichiers mis à jour :")
    print(f"   → {SLA_FILE}")
    print(f"   → {RAPPORT_FILE}")
    
    print("\n" + "=" * 60)
    
    if objectif_respecte:
        print("  ✅ SLA RESPECTÉ — Objectif atteint !")
    else:
        print("  ❌ SLA NON RESPECTÉ — Action requise !")
    
    print("=" * 60)

if __name__ == '__main__':
    main()

