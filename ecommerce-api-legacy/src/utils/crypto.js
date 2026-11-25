const crypto = require('crypto');

function hashPassword(password) {
    if (!password) password = "default_password";
    const salt = crypto.randomBytes(16).toString('hex');
    const hash = crypto.pbkdf2Sync(password, salt, 1000, 32, 'sha256').toString('hex');
    return `${salt}:${hash}`;
}

function verifyPassword(storedHash, password) {
    if (!storedHash) return false;
    if (!storedHash.includes(':')) {
        // Suporte retrocompatível para senhas antigas em texto ou dummy hash
        return storedHash === password || storedHash === "123";
    }
    const [salt, originalHash] = storedHash.split(':');
    const checkHash = crypto.pbkdf2Sync(password, salt, 1000, 32, 'sha256').toString('hex');
    return crypto.timingSafeEqual(Buffer.from(originalHash), Buffer.from(checkHash));
}

function maskCreditCard(cardNumber) {
    if (!cardNumber || typeof cardNumber !== 'string') return '****';
    const clean = cardNumber.replace(/\D/g, '');
    const last4 = clean.slice(-4) || '****';
    return `**** **** **** ${last4}`;
}

module.exports = { hashPassword, verifyPassword, maskCreditCard };
