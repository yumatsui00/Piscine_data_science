import os
import stat

csv_dir = "./subject/customer"
initsql = "./subject/customer/init.sql"
maintable = "customers"
import os
import stat

def generate_init():
    with open(initsql, 'w') as f:
        # メインテーブルを作成
        f.write(f"""
        CREATE TABLE IF NOT EXISTS {maintable} (
            event_time TIMESTAMP,
            event_type TEXT,
            product_id INTEGER,
            price NUMERIC,
            user_id NUMERIC,
            user_session TEXT
        );

        -- メインテーブルにインデックスを作成
        CREATE INDEX IF NOT EXISTS idx_maintable
        ON {maintable} (event_type, product_id, price, user_id, user_session, event_time);
        \n""")

        # 個別のテーブル作成とデータ挿入
        for file in os.listdir(csv_dir):
            if not file.endswith('.csv'):
                continue
            table_name = file[:-4]  # .csvを除く
            csv_path = f"/docker-entrypoint-initdb.d/{file}"

            f.write(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            event_time TIMESTAMP,
            event_type TEXT,
            product_id INTEGER,
            price NUMERIC,
            user_id NUMERIC,
            user_session TEXT
        );

        COPY {table_name}(event_time, event_type, product_id, price, user_id, user_session)
        FROM '{csv_path}'
        DELIMITER ','
        CSV HEADER;

        -- メインテーブルにデータを挿入
        INSERT INTO {maintable} (event_time, event_type, product_id, price, user_id, user_session)
        SELECT event_time, event_type, product_id, price, user_id, user_session
        FROM {table_name};

        DO $$
            BEGIN
                RAISE NOTICE '{table_name} done';
            END $$;
        \n""")

        # メインテーブルでの重複削除
        f.write(f"""
        DO $$
        BEGIN
            DELETE FROM customers
            WHERE ctid IN (
                SELECT t1.ctid
                FROM customers t1
                JOIN customers t2
                ON t1.ctid > t2.ctid
                AND t1.event_type = t2.event_type
                AND t1.product_id = t2.product_id
                AND t1.price = t2.price
                AND t1.user_id = t2.user_id
                AND t1.user_session = t2.user_session
                AND ABS(EXTRACT(EPOCH FROM t1.event_time) - EXTRACT(EPOCH FROM t2.event_time)) <= 1
            );

            RAISE NOTICE 'Duplicate removal complete. Remaining rows: %', (SELECT COUNT(*) FROM customers);
        END $$;

        \n""")

    # スクリプトに実行権限を付与
    st = os.stat(initsql)
    os.chmod(initsql, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print("init.sql生成完了")




if __name__ == '__main__':
	generate_init()