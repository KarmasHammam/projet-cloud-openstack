from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db, init_db
import datetime
import os

app = Flask(__name__)
app.secret_key = 'helpdesk_openstack_2026'

init_db()

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def get_current_user():
    if 'user_id' in session:
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
        conn.close()
        return user
    return None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('dashboard'))
        error = 'Identifiants incorrects !'
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    user = get_current_user()
    if session['role'] == 'admin':
        tickets = conn.execute('''
            SELECT t.*, u1.username as creator, u2.username as assignee
            FROM tickets t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.assigned_to = u2.id
            ORDER BY t.created_at DESC LIMIT 5
        ''').fetchall()
        total = conn.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
        ouverts = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="ouvert"').fetchone()[0]
        en_cours = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="en_cours"').fetchone()[0]
        resolus = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="resolu"').fetchone()[0]
    elif session['role'] == 'technicien':
        tickets = conn.execute('''
            SELECT t.*, u1.username as creator, u2.username as assignee
            FROM tickets t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.assigned_to = u2.id
            WHERE t.assigned_to=?
            ORDER BY t.created_at DESC LIMIT 5
        ''', (session['user_id'],)).fetchall()
        total = conn.execute('SELECT COUNT(*) FROM tickets WHERE assigned_to=?', (session['user_id'],)).fetchone()[0]
        ouverts = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="ouvert" AND assigned_to=?', (session['user_id'],)).fetchone()[0]
        en_cours = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="en_cours" AND assigned_to=?', (session['user_id'],)).fetchone()[0]
        resolus = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="resolu" AND assigned_to=?', (session['user_id'],)).fetchone()[0]
    else:
        tickets = conn.execute('''
            SELECT t.*, u1.username as creator, u2.username as assignee
            FROM tickets t
            LEFT JOIN users u1 ON t.created_by = u1.id
            LEFT JOIN users u2 ON t.assigned_to = u2.id
            WHERE t.created_by=?
            ORDER BY t.created_at DESC LIMIT 5
        ''', (session['user_id'],)).fetchall()
        total = conn.execute('SELECT COUNT(*) FROM tickets WHERE created_by=?', (session['user_id'],)).fetchone()[0]
        ouverts = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="ouvert" AND created_by=?', (session['user_id'],)).fetchone()[0]
        en_cours = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="en_cours" AND created_by=?', (session['user_id'],)).fetchone()[0]
        resolus = conn.execute('SELECT COUNT(*) FROM tickets WHERE statut="resolu" AND created_by=?', (session['user_id'],)).fetchone()[0]
    conn.close()
    return render_template('dashboard.html', user=user, tickets=tickets,
        total=total, ouverts=ouverts, en_cours=en_cours, resolus=resolus)

@app.route('/tickets')
@login_required
def tickets():
    conn = get_db()
    user = get_current_user()
    filtre_statut = request.args.get('statut', '')
    filtre_priorite = request.args.get('priorite', '')
    query = '''
        SELECT t.*, u1.username as creator, u2.username as assignee
        FROM tickets t
        LEFT JOIN users u1 ON t.created_by = u1.id
        LEFT JOIN users u2 ON t.assigned_to = u2.id
    '''
    conditions = []
    params = []
    if session['role'] == 'utilisateur':
        conditions.append('t.created_by=?')
        params.append(session['user_id'])
    elif session['role'] == 'technicien':
        conditions.append('t.assigned_to=?')
        params.append(session['user_id'])
    if filtre_statut:
        conditions.append('t.statut=?')
        params.append(filtre_statut)
    if filtre_priorite:
        conditions.append('t.priorite=?')
        params.append(filtre_priorite)
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    query += ' ORDER BY t.created_at DESC'
    tickets = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('tickets.html', user=user, tickets=tickets,
                         filtre_statut=filtre_statut, filtre_priorite=filtre_priorite)

@app.route('/ticket/new', methods=['GET', 'POST'])
@login_required
def new_ticket():
    user = get_current_user()
    msg = None
    if request.method == 'POST':
        titre = request.form.get('titre', '').strip()
        description = request.form.get('description', '').strip()
        priorite = request.form.get('priorite', 'moyenne')
        if titre and description:
            conn = get_db()
            conn.execute('INSERT INTO tickets (titre, description, priorite, created_by) VALUES (?,?,?,?)',
                (titre, description, priorite, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(url_for('tickets'))
        msg = 'Titre et description obligatoires !'
    return render_template('new_ticket.html', user=user, msg=msg)

@app.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def ticket_detail(ticket_id):
    conn = get_db()
    user = get_current_user()
    ticket = conn.execute('''
        SELECT t.*, u1.username as creator, u2.username as assignee
        FROM tickets t
        LEFT JOIN users u1 ON t.created_by = u1.id
        LEFT JOIN users u2 ON t.assigned_to = u2.id
        WHERE t.id=?
    ''', (ticket_id,)).fetchone()
    commentaires = conn.execute('''
        SELECT c.*, u.username FROM commentaires c
        JOIN users u ON c.user_id = u.id
        WHERE c.ticket_id=? ORDER BY c.created_at ASC
    ''', (ticket_id,)).fetchall()
    techniciens = conn.execute('SELECT * FROM users WHERE role="technicien"').fetchall()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'commentaire':
            contenu = request.form.get('contenu', '').strip()
            if contenu:
                conn.execute('INSERT INTO commentaires (ticket_id, user_id, contenu) VALUES (?,?,?)',
                    (ticket_id, session['user_id'], contenu))
                conn.commit()
        elif action == 'statut' and session['role'] in ['admin', 'technicien']:
            statut = request.form.get('statut')
            conn.execute('UPDATE tickets SET statut=? WHERE id=?', (statut, ticket_id))
            conn.commit()
        elif action == 'assigner' and session['role'] == 'admin':
            assigned_to = request.form.get('assigned_to')
            conn.execute('UPDATE tickets SET assigned_to=? WHERE id=?', (assigned_to, ticket_id))
            conn.commit()
        conn.close()
        return redirect(url_for('ticket_detail', ticket_id=ticket_id))
    conn.close()
    return render_template('ticket_detail.html', user=user, ticket=ticket,
        commentaires=commentaires, techniciens=techniciens)

@app.route('/ticket/delete/<int:ticket_id>', methods=['POST'])
@admin_required
def delete_ticket(ticket_id):
    conn = get_db()
    conn.execute('DELETE FROM commentaires WHERE ticket_id=?', (ticket_id,))
    conn.execute('DELETE FROM tickets WHERE id=?', (ticket_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('tickets'))

@app.route('/admin')
@admin_required
def admin():
    conn = get_db()
    user = get_current_user()
    users = conn.execute('SELECT * FROM users ORDER BY role').fetchall()
    total_tickets = conn.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    tickets_urgents = conn.execute('SELECT COUNT(*) FROM tickets WHERE priorite="haute" AND statut!="resolu"').fetchone()[0]
    conn.close()
    return render_template('admin.html', user=user, users=users,
        total_tickets=total_tickets, total_users=total_users, tickets_urgents=tickets_urgents)

@app.route('/admin/user/add', methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', 'utilisateur')
    if username and password:
        conn = get_db()
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?,?,?)',
                (username, generate_password_hash(password), role))
            conn.commit()
        except:
            pass
        conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/user/delete/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    if user_id != session['user_id']:
        conn = get_db()
        conn.execute('DELETE FROM users WHERE id=?', (user_id,))
        conn.commit()
        conn.close()
    return redirect(url_for('admin'))

@app.route('/api/tickets')
def api_tickets():
    conn = get_db()
    tickets = conn.execute('SELECT * FROM tickets').fetchall()
    conn.close()
    return jsonify({
        'status': 'success',
        'total': len(tickets),
        'tickets': [dict(t) for t in tickets],
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/status')
def status():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]
    users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()
    return jsonify({
        'status': 'running',
        'service': 'Help Desk SaaS',
        'platform': 'OpenStack DevStack',
        'tickets': total,
        'users': users,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

