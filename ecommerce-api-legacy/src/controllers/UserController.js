const UserModel = require('../models/UserModel');

class UserController {
    static async deleteUser(req, res) {
        try {
            const { id } = req.params;
            const deleted = await UserModel.deleteWithCascade(id);
            if (!deleted) {
                return res.status(404).send("Usuário não encontrado");
            }
            return res.send("Usuário deletado com sucesso e integridade referencial mantida.");
        } catch (error) {
            console.error("[ERROR] Falha ao deletar usuário:", error);
            return res.status(500).send("Erro DB");
        }
    }
}

module.exports = UserController;
