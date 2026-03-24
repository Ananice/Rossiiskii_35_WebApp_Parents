# Исправлено: убран AddField student (student_id уже существует в 0001),
# вместо этого — ALTER COLUMN через SeparateDatabaseAndState

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parents', '0002_parent_user'),
        ('students', '0001_initial'),
    ]

    operations = [
        # 1. Снимаем старый unique_together по student_id
        migrations.AlterUniqueTogether(
            name='parentstudentrelation',
            unique_together=set(),
        ),
        # 2. Синхронизируем состояние Django: говорим что student_id теперь FK
        #    без реального ADD COLUMN в БД (колонка уже есть)
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                        ALTER TABLE parents_parentstudentrelation
                        ALTER COLUMN student_id TYPE bigint;

                        ALTER TABLE parents_parentstudentrelation
                        ADD CONSTRAINT parents_psr_student_fk
                        FOREIGN KEY (student_id)
                        REFERENCES students_student(id)
                        ON DELETE CASCADE
                        DEFERRABLE INITIALLY DEFERRED;
                    """,
                    reverse_sql="""
                        ALTER TABLE parents_parentstudentrelation
                        DROP CONSTRAINT IF EXISTS parents_psr_student_fk;
                    """,
                ),
            ],
            state_operations=[
                migrations.RemoveField(
                    model_name='parentstudentrelation',
                    name='student_id',
                ),
                migrations.AddField(
                    model_name='parentstudentrelation',
                    name='student',
                    field=models.ForeignKey(
                        default=1,
                        help_text='Студент',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='parent_relations',
                        to='students.student',
                    ),
                    preserve_default=False,
                ),
            ],
        ),
        # 3. Устанавливаем новый unique_together по student (FK)
        migrations.AlterUniqueTogether(
            name='parentstudentrelation',
            unique_together={('parent', 'student', 'relation_type')},
        ),
    ]
