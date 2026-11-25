// Shim de compatibilidade para código ou testes que instanciem AppManager diretamente
const db = require('./database/connection');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');

class AppManager {
    constructor() {
        this.db = db.db;
    }

    async initDb() {
        await db.init();
    }

    setupRoutes(app) {
        app.use('/api', checkoutRoutes);
        app.use('/api', reportRoutes);
        app.use('/api', userRoutes);
    }
}

module.exports = AppManager;
