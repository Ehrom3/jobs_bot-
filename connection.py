import asyncpg
from dotenv import load_dotenv
import os

load_dotenv()

async def connection():
    try:  
        return await asyncpg.connect(
            user="postgres",
            password=os.getenv("PASSWORD_DB"),
            database="jobs_db",   
            host="localhost",
            port=5432
        )
        print("connect is okay")
    except Exception as er:
        print("Connection is error: ", er)
    
    

async def create_table():
    try:
        conn = await connection()
        await conn.execute("""
            create table if not exists users(
                user_id serial primary key,
                username varchar(100),
                full_name varchar(100) not null,
                telegram_id varchar,
                created_at timestamp default now(),
                is_active boolean default true
        )
        """)
        await conn.execute("""
            create table if not exists cotegory(
                cotegory_id serial primary key,
                cotegory_name varchar(100) not null
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs(
                jobs_id SERIAL PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                discription TEXT,
                salary INT NOT NULL DEFAULT 0,
                cotegory_id INT REFERENCES cotegory(cotegory_id) ON DELETE SET NULL,
                user_id INT REFERENCES users(user_id) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT NOW()
        );""")
        await conn.execute("""
            create table if not exists applications(
                applications_id serial primary key,
                user_id int references users(user_id),
                jobs_id int references jobs(jobs_id),
                created_at timestamp default now()    
        );   
            """)
    except Exception as error:
        print(f"Connection Error: {error}")
    finally:
        await conn.close()
        print("Table created!")


        
