import sqlite3
import json
import os

DB_PATH = 'chat_history.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_turns (
            id INTEGER PRIMARY KEY,
            question TEXT,
            agents TEXT,
            synthesize BOOLEAN,
            responses TEXT,
            synthesized TEXT,
            session_id TEXT
        )
    ''')
    try:
        cursor.execute("ALTER TABLE chat_turns ADD COLUMN session_id TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def save_turn(turn_data: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Use REPLACE to handle potential duplicate IDs from frontend
    cursor.execute('''
        INSERT OR REPLACE INTO chat_turns (id, question, agents, synthesize, responses, synthesized, session_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        turn_data.get('id'),
        turn_data.get('question', ''),
        json.dumps(turn_data.get('agents', [])),
        turn_data.get('synthesize', True),
        json.dumps(turn_data.get('responses', {})),
        turn_data.get('synthesized', ''),
        turn_data.get('session_id')
    ))
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, question, agents, synthesize, responses, synthesized, session_id FROM chat_turns ORDER BY id ASC
    ''')
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for row in rows:
        history.append({
            'id': row[0],
            'question': row[1],
            'agents': json.loads(row[2]) if row[2] else [],
            'synthesize': bool(row[3]),
            'responses': json.loads(row[4]) if row[4] else {},
            'synthesized': row[5],
            'session_id': row[6] if len(row) > 6 and row[6] else str(row[0])
        })
    return history

def clear_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_turns')
    conn.commit()
    conn.close()
