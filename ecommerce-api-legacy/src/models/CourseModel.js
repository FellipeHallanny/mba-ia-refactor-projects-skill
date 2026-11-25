const db = require('../database/connection');

class CourseModel {
    static async findActiveById(id) {
        return await db.getAsync("SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
    }

    static async listAll() {
        return await db.allAsync("SELECT * FROM courses", []);
    }

    static async getFinancialReport() {
        // Query otimizada com JOINs para eliminar N+1
        const sql = `
            SELECT 
                c.id AS course_id,
                c.title AS course_title,
                p.amount AS payment_amount,
                p.status AS payment_status,
                u.name AS student_name
            FROM courses c
            LEFT JOIN enrollments e ON c.id = e.course_id
            LEFT JOIN users u ON e.user_id = u.id
            LEFT JOIN payments p ON e.id = p.enrollment_id
            ORDER BY c.id
        `;
        const rows = await db.allAsync(sql, []);
        const reportMap = new Map();

        for (const row of rows) {
            if (!reportMap.has(row.course_id)) {
                reportMap.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: []
                });
            }

            const courseEntry = reportMap.get(row.course_id);
            if (row.student_name) {
                if (row.payment_status === 'PAID') {
                    courseEntry.revenue += row.payment_amount || 0;
                }
                courseEntry.students.push({
                    student: row.student_name,
                    paid: row.payment_amount || 0
                });
            }
        }

        return Array.from(reportMap.values());
    }
}

module.exports = CourseModel;
