from connection import connection


async def get_user(telegram_id):
    conn = await connection()
    if not conn:
        return None
    try:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1",
            str(telegram_id)
        )
    finally:
        await conn.close()


async def save_user(telegram_id, username, full_name):
    conn = await connection()
    if not conn:
        return False
    try:
        await conn.execute("""
            INSERT INTO users(telegram_id, username, full_name)
            VALUES($1, $2, $3)
            ON CONFLICT (telegram_id) DO UPDATE
            SET username = EXCLUDED.username,
                full_name = EXCLUDED.full_name
        """, str(telegram_id), username, full_name)
        return True
    except Exception as error:
        print(f"save_user error: {error}")
        return False
    finally:
        await conn.close()


async def save_category(category_name):
    conn = await connection()
    if not conn:
        return False
    try:
        await conn.execute(
            "INSERT INTO cotegory(cotegory_name) VALUES($1)",
            category_name
        )
        return True
    except Exception as error:
        print(f"save_category error: {error}")
        return False
    finally:
        await conn.close()


async def get_category():
    conn = await connection()
    if not conn:
        return []
    try:
        return await conn.fetch(
            "SELECT * FROM cotegory ORDER BY cotegory_id"
        )
    finally:
        await conn.close()


async def update_category_service(cat_id, category_name):
    conn = await connection()
    if not conn:
        return False
    try:
        result = await conn.execute("""
            UPDATE cotegory
            SET cotegory_name = $1
            WHERE cotegory_id = $2
        """, category_name, int(cat_id))
        return result != "UPDATE 0"
    except Exception as error:
        print(f"update_category error: {error}")
        return False
    finally:
        await conn.close()


async def delete_category_service(cat_id):
    conn = await connection()
    if not conn:
        return False
    try:
        result = await conn.execute(
            "DELETE FROM cotegory WHERE cotegory_id = $1",
            int(cat_id)
        )
        return result != "DELETE 0"
    except Exception as error:
        print(f"delete_category error: {error}")
        return False
    finally:
        await conn.close()


async def save_job(telegram_id,username,full_name,title,description,salary,category_id):
    conn = await connection()
    if not conn:
        return False
    try:
        user = await conn.fetchrow("""
            SELECT user_id FROM users WHERE telegram_id = $1
        """, str(telegram_id))
        if not user:
            user = await conn.fetchrow("""
                INSERT INTO users(telegram_id, username, full_name)
                VALUES($1, $2, $3) RETURNING user_id
            """,
                str(telegram_id),
                username,
                full_name
            )

        await conn.execute("""
            INSERT INTO jobs( title, discription,salary, cotegory_id, user_id)
            VALUES($1, $2, $3, $4, $5)
        """,
            title,
            description,
            int(salary),
            int(category_id),
            user["user_id"]
        )

        print("ВАКАНСИЯ СОХРАНЕНА")
        return True

    except Exception as error:
        print(f"SAVE_JOB ERROR: {error}")
        return False

    finally:
        await conn.close()

async def get_jobs():
    conn = await connection()
    if not conn:
        return []
    try:
        return await conn.fetch("""
            SELECT j.jobs_id, j.title, j.discription, j.salary,
                   c.cotegory_name, u.full_name, u.username
            FROM jobs j
            LEFT JOIN cotegory c ON c.cotegory_id = j.cotegory_id
            LEFT JOIN users u ON u.user_id = j.user_id
            ORDER BY j.jobs_id DESC
        """)
    finally:
        await conn.close()


async def get_job(job_id):
    conn = await connection()
    if not conn:
        return None
    try:
        return await conn.fetchrow("""
            SELECT j.jobs_id, j.title, j.discription, j.salary,
                   j.user_id AS owner_user_id,
                   c.cotegory_name,
                   u.telegram_id AS owner_telegram_id,
                   u.full_name AS owner_name,
                   u.username AS owner_username
            FROM jobs j
            LEFT JOIN cotegory c ON c.cotegory_id = j.cotegory_id
            LEFT JOIN users u ON u.user_id = j.user_id
            WHERE j.jobs_id = $1
        """, int(job_id))
    finally:
        await conn.close()


async def add_application(telegram_id, job_id):
    conn = await connection()
    if not conn:
        return "error", None
    try:
        user = await conn.fetchrow(
            "SELECT * FROM users WHERE telegram_id = $1",
            str(telegram_id)
        )
        job = await conn.fetchrow("""
            SELECT j.*, u.telegram_id AS owner_telegram_id
            FROM jobs j
            LEFT JOIN users u ON u.user_id = j.user_id
            WHERE j.jobs_id = $1
        """, int(job_id))

        if not user or not job:
            return "error", None

        if job["user_id"] == user["user_id"]:
            return "own_job", job

        exists = await conn.fetchrow("""
            SELECT applications_id FROM applications
            WHERE user_id = $1 AND jobs_id = $2
        """, user["user_id"], int(job_id))

        if exists:
            return "exists", job

        await conn.execute("""
            INSERT INTO applications(user_id, jobs_id)
            VALUES($1, $2)
        """, user["user_id"], int(job_id))

        return "ok", job
    except Exception as error:
        print(f"add_application error: {error}")
        return "error", None
    finally:
        await conn.close()
