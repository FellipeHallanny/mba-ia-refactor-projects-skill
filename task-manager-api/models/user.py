from database import db
from datetime import datetime, timezone
import hashlib
import os
import hmac

def get_utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_utc_now)

    def to_dict(self):
        # Proteção de segurança: nunca expõe a senha/hash na serialização
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at)
        }

    def set_password(self, pwd):
        salt = os.urandom(16).hex()
        digest = hashlib.sha256((salt + pwd).encode("utf-8")).hexdigest()
        self.password = f"{salt}:{digest}"

    def check_password(self, pwd):
        if not self.password:
            return False
        if ":" not in self.password:
            # Retrocompatibilidade com senhas migradas/seeds legados em MD5
            legacy_md5 = hashlib.md5(pwd.encode()).hexdigest()
            return hmac.compare_digest(self.password, legacy_md5)
        salt, original_digest = self.password.split(":", 1)
        new_digest = hashlib.sha256((salt + pwd).encode("utf-8")).hexdigest()
        return hmac.compare_digest(original_digest, new_digest)

    def is_admin(self):
        return self.role == 'admin'
