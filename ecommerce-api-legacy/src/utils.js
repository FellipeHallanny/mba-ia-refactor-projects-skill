const config = require('./config/settings');
const { hashPassword } = require('./utils/crypto');

function logAndCache(key, data) {
    console.log(`[LOG] Salvando no cache: ${key}`);
}

function badCrypto(pwd) {
    return hashPassword(pwd);
}

module.exports = { config, logAndCache, badCrypto, globalCache: {}, totalRevenue: 0 };
