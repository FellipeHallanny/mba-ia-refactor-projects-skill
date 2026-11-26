module.exports = {
    port: process.env.PORT || 3000,
    dbUser: process.env.DB_USER || "dev_user",
    // Senhas e chaves reais exigem injeção via ambiente. NUNCA 'senha_super_secreta_prod_123' ou 'pk_live_...' como defaults.
    dbPass: process.env.DB_PASS || "",
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || "pk_test_sample_key",
    smtpUser: process.env.SMTP_USER || ""
};
