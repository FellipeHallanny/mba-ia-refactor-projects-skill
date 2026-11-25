const CourseModel = require('../models/CourseModel');
const UserModel = require('../models/UserModel');
const EnrollmentModel = require('../models/EnrollmentModel');
const PaymentModel = require('../models/PaymentModel');
const { maskCreditCard } = require('../utils/crypto');

class CheckoutController {
    static async processCheckout(req, res) {
        try {
            const userName = req.body.usr;
            const email = req.body.eml;
            const password = req.body.pwd;
            const courseId = req.body.c_id;
            const creditCard = req.body.card;

            if (!userName || !email || !courseId || !creditCard) {
                return res.status(400).send("Bad Request");
            }

            const course = await CourseModel.findActiveById(courseId);
            if (!course) {
                return res.status(404).send("Curso não encontrado");
            }

            // Simulação de gateway seguro: log com máscara
            console.log(`[INFO] Processando transação com cartão ${maskCreditCard(creditCard)} para o curso ${courseId}`);
            const paymentStatus = creditCard.startsWith("4") ? "PAID" : "DENIED";

            if (paymentStatus === "DENIED") {
                return res.status(400).send("Pagamento recusado");
            }

            let user = await UserModel.findByEmail(email);
            if (!user) {
                user = await UserModel.create(userName, email, password || "123456");
            }

            const enrollmentId = await EnrollmentModel.create(user.id, courseId);
            await PaymentModel.create(enrollmentId, course.price, paymentStatus);
            await PaymentModel.recordAuditLog(`Checkout curso ${courseId} por ${user.id}`);

            return res.status(200).json({ msg: "Sucesso", enrollment_id: enrollmentId });
        } catch (error) {
            console.error("[ERROR] Falha no checkout:", error);
            return res.status(500).send("Erro interno ao processar checkout");
        }
    }
}

module.exports = CheckoutController;
