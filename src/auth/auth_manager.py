import json
import os
import hashlib

class AuthManager:
    def __init__(self, db_path="gai_pro/data/users.json"):
        self.db_path = db_path
        self._ensure_db_exists()

    def _ensure_db_exists(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, 'w') as f:
                json.dump({}, f)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username, password):
        with open(self.db_path, 'r') as f:
            users = json.load(f)
        
        if username in users:
            return False, "Usuário já existe!"
        
        users[username] = self._hash_password(password)
        
        with open(self.db_path, 'w') as f:
            json.dump(users, f, indent=4)
        return True, "Usuário cadastrado com sucesso!"

    def login(self, username, password):
        if not os.path.exists(self.db_path):
            return False, "Nenhum usuário cadastrado."
            
        with open(self.db_path, 'r') as f:
            users = json.load(f)
            
        hashed = self._hash_password(password)
        if username in users and users[username] == hashed:
            return True, "Login realizado com sucesso!"
        return False, "Usuário ou senha incorretos."
