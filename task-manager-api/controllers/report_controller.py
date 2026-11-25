from flask import jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime, timezone, timedelta
from sqlalchemy import func

def get_utc_now():
    return datetime.now(timezone.utc)

class ReportController:
    @staticmethod
    def summary_report():
        now_utc = get_utc_now()
        total_tasks = Task.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()

        pending = Task.query.filter_by(status='pending').count()
        in_progress = Task.query.filter_by(status='in_progress').count()
        done = Task.query.filter_by(status='done').count()
        cancelled = Task.query.filter_by(status='cancelled').count()

        p1 = Task.query.filter_by(priority=1).count()
        p2 = Task.query.filter_by(priority=2).count()
        p3 = Task.query.filter_by(priority=3).count()
        p4 = Task.query.filter_by(priority=4).count()
        p5 = Task.query.filter_by(priority=5).count()

        # Otimização: tarefas atrasadas sem N+1
        all_tasks = Task.query.filter(Task.due_date.isnot(None)).all()
        overdue_count = 0
        overdue_list = []
        for t in all_tasks:
            target = t.due_date if t.due_date.tzinfo else t.due_date.replace(tzinfo=timezone.utc)
            if target < now_utc and t.status not in ['done', 'cancelled']:
                overdue_count += 1
                days_overdue = (now_utc - target).days
                overdue_list.append({
                    'id': t.id,
                    'title': t.title,
                    'due_date': str(t.due_date),
                    'days_overdue': days_overdue
                })

        seven_days_ago = now_utc - timedelta(days=7)
        recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
        recent_done = Task.query.filter(
            Task.status == 'done',
            Task.updated_at >= seven_days_ago
        ).count()

        # Otimização de produtividade de usuário via agregação SQL direta (eliminando N+1)
        users = User.query.all()
        user_stats = []
        # Mapa de contagens totais por usuário
        total_by_user = dict(db.session.query(Task.user_id, func.count(Task.id)).group_by(Task.user_id).all())
        done_by_user = dict(db.session.query(Task.user_id, func.count(Task.id)).filter(Task.status == 'done').group_by(Task.user_id).all())

        for u in users:
            total = total_by_user.get(u.id, 0)
            completed = done_by_user.get(u.id, 0)
            user_stats.append({
                'user_id': u.id,
                'user_name': u.name,
                'total_tasks': total,
                'completed_tasks': completed,
                'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0
            })

        report = {
            'generated_at': str(now_utc),
            'overview': {
                'total_tasks': total_tasks,
                'total_users': total_users,
                'total_categories': total_categories,
            },
            'tasks_by_status': {
                'pending': pending,
                'in_progress': in_progress,
                'done': done,
                'cancelled': cancelled,
            },
            'tasks_by_priority': {
                'critical': p1,
                'high': p2,
                'medium': p3,
                'low': p4,
                'minimal': p5,
            },
            'overdue': {
                'count': overdue_count,
                'tasks': overdue_list,
            },
            'recent_activity': {
                'tasks_created_last_7_days': recent_tasks,
                'tasks_completed_last_7_days': recent_done,
            },
            'user_productivity': user_stats,
        }

        return jsonify(report), 200
