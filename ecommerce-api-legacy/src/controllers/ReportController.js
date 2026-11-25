const CourseModel = require('../models/CourseModel');

class ReportController {
    static async getFinancialReport(req, res) {
        try {
            const report = await CourseModel.getFinancialReport();
            return res.json(report);
        } catch (error) {
            console.error("[ERROR] Falha ao gerar relatório financeiro:", error);
            return res.status(500).send("Erro DB");
        }
    }
}

module.exports = ReportController;
