import sqlite3
from datetime import datetime

def intitialize_table(path):

    con = sqlite3.connect(path)
    cursor = con.cursor()

    try:
        cursor.execute("""CREATE TABLE flagtable (
            flag TEXT,
            challenge_id TEXT,
            timestamp TEXT
        )""")
    except sqlite3.OperationalError:
        pass
    except Exception as e:
        print(e)
        return

    try:
        cursor.execute("""CREATE TABLE challengedata (
            challenge_id TEXT,
            name TEXT,
            category TEXT,
            description TEXT
        )""")
    except sqlite3.OperationalError:
        pass
    except Exception as e:
        print(e)
        return

    try:
        cursor.execute("""CREATE TABLE solvetable (
            challenge_id TEXT,
            user_id TEXT,
            timestamp TEXT
        )""")
    except sqlite3.OperationalError:
        pass
    except Exception as e:
        print(e)
        return

    con.commit()
    con.close()

def add_flag(cursor, con, flag, challenge_id):

    cursor.execute(f"INSERT INTO flagtable VALUES ('{flag}', '{challenge_id}', '{datetime.now()}')")
    con.commit()

def remove_flag(cursor, con, challenge_id):

    cursor.execute(f"DELETE FROM flagtable WHERE challenge_id = ?", (challenge_id,))
    con.commit()

def add_solve(cursor, con, challenge_id, user_id):

    query = cursor.execute("SELECT user_id FROM solvetable WHERE challenge_id = ?", (challenge_id,))
    result = query.fetchone()

    if result is None:
        cursor.execute(f"INSERT INTO solvetable VALUES ('{challenge_id}', '{user_id}', '{datetime.now()}')")
        con.commit()
        return True

    return False

def get_challenge_name(cursor, con, challenge_id):

    query = cursor.execute("SELECT name FROM challengedata where challenge_id = ?", (challenge_id,))
    result = query.fetchone()

    return result[0] if result else None

def create_challenge(cursor, con, challenge_id, challenge_name, category, description):

    cursor.execute(f"INSERT INTO challengedata VALUES ('{challenge_id}', '{challenge_name}', '{category}', '{description}')")
    con.commit()

def query_solve(cursor, con, flag):

    query = cursor.execute("SELECT challenge_id FROM flagtable where flag = ?", (flag,))
    result = query.fetchone()

    return result[0] if result else None

if __name__ == '__main__':
    intitialize_table(cursor)
    con.close()
