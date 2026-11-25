const express = require('express');
const config = require('./config/settings');
const db = require('./database/connection');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

// Registro de rotas desacopladas (MVC)
app.use('/api', checkoutRoutes);
app.use('/api', reportRoutes);
app.use('/api', userRoutes);

// Middleware centralizado de tratamento de erros
app.use(errorHandler);

// Inicialização assíncrona limpa
async function startServer() {
    try {
        await db.init();
        const server = app.listen(config.port, () => {
            console.log(`Frankenstein LMS refatorado rodando na porta ${config.port}...`);
        });
        return server;
    } catch (err) {
        console.error("Falha ao inicializar o banco de dados:", err);
        process.exit(1);
    }
}

if (require.main === module) {
    startServer();
}

module.exports = { app, startServer };
