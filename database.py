# Database Connection
import psycopg2

try:
    conn = psycopg2.connect(host="ec2-18-204-101-137.compute-1.amazonaws.com", database="dcbg9ldkgk967o",
                            user="jajiwoufefsvjp",
                            password="54957ef2d44493ba1523cb285f416666e20ba8939bd31e410cd36fd86a7e7309")
    print('Database Connected')
    cursor = conn.cursor()
except Exception as e:
    print(f'{e}')
# Cursor Database

