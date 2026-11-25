module.exports = {
    port: process.env.PORT || 3000,
    dbUser: process.env.DB_USER || "admin_master",
    dbPass: process.env.DB_PASS || "dev_secret_pass",
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "pk_test_1234567890abcdef",
    smtpUser: process.env.SMTP_USER || "no-reply@fullcycle.com.br"
};
