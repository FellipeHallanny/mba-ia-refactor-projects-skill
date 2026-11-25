const db = require('../database/connection');
const { hashPassword } = require('../utils/crypto');

class UserModel {
    static async findByEmail(email) {
        return await db.getAsync("SELECT id, name, email, pass FROM users WHERE email = ?", [email]);
    }

    static async findById(id) {
        return await db.getAsync("SELECT id, name, email FROM users WHERE id = ?", [id]);
    }

    static async create(name, email, plainPassword) {
        const hashedPassword = hashPassword(plainPassword);
        const result = await db.runAsync(
            "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
            [name, email, hashedPassword]
        );
        return { id: result.lastID, name, email };
    }

    static async deleteWithCascade(id) {
        // Remove matrículas e pagamentos em cascata para integridade referencial
        const enrollments = await db.allAsync("SELECT id FROM enrollments WHERE user_id = ?", [id]);
        for (const enr of enrollments) {
            await db.runAsync("DELETE FROM payments WHERE enrollment_id = ?", [enr.id]);
        }
        await db.runAsync("DELETE FROM enrollments WHERE user_id = ?", [id]);
        const result = await db.runAsync("DELETE FROM users WHERE id = ?", [id]);
        return result.changes > 0;
    }
}

module.exports = UserModel;
