# Imports
import sqlite3
from datetime import datetime
from typing import Optional


def intitialize_table(path: str) -> None:
    '''A function that initializes the database if uninitialized

    Args:
        path: the path to the database
    '''

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


def add_flag(cursor: sqlite3.Cursor, con: sqlite3.Connection, flag: str, challenge_id: str) -> None:
    '''Adds a flag to a challenge in the database

    Args:
        cursor: the cursor used to execute commands
        con: the connection to the database
        flag: the flag of the challenge to add
        challenge_id: the ID of the challenge to add the flag to
    '''

    cursor.execute(f"INSERT INTO flagtable VALUES ('{flag}', '{challenge_id}', '{datetime.now()}')")
    con.commit()


def remove_flag(cursor: sqlite3.Cursor, con: sqlite3.Connection, challenge_id: str) -> None:
    '''Removes all flags from a challenge in the database

    Args:
        cursor: the cursor used to execute commands
        con: the connection to the database
        challenge_id: the ID of the challenge to remove the flags from
    '''

    cursor.execute(f"DELETE FROM flagtable WHERE challenge_id = ?", (challenge_id,))
    con.commit()


def add_solve(cursor: sqlite3.Cursor, con: sqlite3.Connection, challenge_id: str, user_id: str) -> bool:
    '''Adds a user solve for a challenge to the database

    Args:
        cursor: the cursor used to execute commands
        con: the connection to the database
        challenge_id: the ID of the challenge
        user_id: the ID of the user that solved the challenge

    Returns:
        True if successfully added, False if not
    '''

    query = cursor.execute("SELECT user_id FROM solvetable WHERE challenge_id = ?", (challenge_id,))
    result = query.fetchone()

    # Check if the user hasn't already solved the challenge
    if result is None:
        cursor.execute(f"INSERT INTO solvetable VALUES ('{challenge_id}', '{user_id}', '{datetime.now()}')")
        con.commit()
        return True

    return False


def get_challenge_name(cursor: sqlite3.Cursor, con: sqlite3.Connection, challenge_id: str) -> Optional[str]:
    '''Gets a challenge name from the associated ID

    Args:
        cursor: the cursor used to execute commands
        con: the connection to the database
        challenge_id: the ID of the challenge

    Returns:
        the name of the challenge if found, None if not
    '''

    query = cursor.execute("SELECT name FROM challengedata where challenge_id = ?", (challenge_id,))
    result = query.fetchone()

    return result[0] if result else None


def create_challenge(cursor: sqlite3.Cursor, con: sqlite3.Connection, challenge_id: str, challenge_name: str, category: str, description: str) -> None:
    '''Creates a new CTF challenge with an input ID, name, category and description

    Args:
        cursor: the cursor used to execute commands
        con: the connection to the database
        challenge_id: the ID of the challenge
        challenge_name: the name of the challenge
        category: the category of the challenge
        description: the description of the challenge
    '''

    cursor.execute(f"INSERT INTO challengedata VALUES ('{challenge_id}', '{challenge_name}', '{category}', '{description}')")
    con.commit()


def query_solve(cursor: sqlite3.Cursor, con: sqlite3.Connection, flag: str) -> Optional[str]:
    '''Checks if a flag is valid for any CTF challenge

    Args:
        cursor: the cursor used to execute commands
        con: the connection to the database
        flag: the input flag

    Return:
        the ID of the challenge solved if the flag is valid, or None if not
    '''

    query = cursor.execute("SELECT challenge_id FROM flagtable where flag = ?", (flag,))
    result = query.fetchone()

    return result[0] if result else None


if __name__ == '__main__':
    intitialize_table(cursor)
    con.close()
