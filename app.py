# app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables from a .env file (optional, see below)
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database Configuration from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = int(os.getenv('DB_PORT', 3306))  # Default to 3306 if not set

def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    Returns the connection object.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

@app.route('/api/pokemon', methods=['GET'])
def get_pokemon():
    """
    Retrieves all Pokémon from the database.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, pokemonName, generation, HP, attributeId, imageURL FROM POKEMON")
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        print(f"Error fetching Pokémon: {e}")
        return jsonify({'error': 'Failed to fetch Pokémon'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/pokeballs', methods=['GET'])
def get_pokeballs():
    """
    Retrieves all Poké Balls from the database.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, pokeballName, typeId, imageURL FROM POKEBALL")
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        print(f"Error fetching Poké Balls: {e}")
        return jsonify({'error': 'Failed to fetch Poké Balls'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/pokemonball', methods=['GET'])
def get_pokemonball_relations():
    """
    Retrieves all Pokémon-Poké Ball relationships from the database.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, pokemonId, pokeballId FROM POKEMONBALL")
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        print(f"Error fetching Pokémon-Poké Ball relations: {e}")
        return jsonify({'error': 'Failed to fetch Pokémon-Poké Ball relations'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/pokemon/<int:pokemon_id>/pokeballs', methods=['GET'])
def get_pokeballs_for_pokemon(pokemon_id):
    """
    Retrieves all compatible Poké Balls for a specific Pokémon.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT pb.id, pb.pokeballName, pb.typeId, pb.imageURL
            FROM POKEBALL pb
            JOIN POKEMONBALL pball ON pb.id = pball.pokeballId
            WHERE pball.pokemonId = %s
        """
        cursor.execute(query, (pokemon_id,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        print(f"Error fetching Poké Balls for Pokémon ID {pokemon_id}: {e}")
        return jsonify({'error': 'Failed to fetch Poké Balls for the specified Pokémon'}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/pokeballs/<int:pokeball_id>/pokemon', methods=['GET'])
def get_pokemon_for_pokeball(pokeball_id):
    """
    Retrieves all compatible Pokémon for a specific Poké Ball.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT p.id, p.pokemonName, p.generation, p.HP, p.attributeId, p.imageURL
            FROM POKEMON p
            JOIN POKEMONBALL pball ON p.id = pball.pokemonId
            WHERE pball.pokeballId = %s
        """
        cursor.execute(query, (pokeball_id,))
        rows = cursor.fetchall()
        return jsonify(rows), 200
    except Error as e:
        print(f"Error fetching Pokémon for Poké Ball ID {pokeball_id}: {e}")
        return jsonify({'error': 'Failed to fetch Pokémon for the specified Poké Ball'}), 500
    finally:
        cursor.close()
        connection.close()

@app.errorhandler(404)
def not_found(e):
    """
    Handles 404 Not Found errors.
    """
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    """
    Handles 500 Internal Server errors.
    """
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
