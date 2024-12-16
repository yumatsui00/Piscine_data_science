import os
import stat

csv_dir = "./subject/customer"
initsql = "./subject/customer/init.sql"
maintable = "customers"
def generate_init():
	with open(initsql, 'w') as f:
		#maintable作成
		f.write(f"""
		CREATE TABLE IF NOT EXISTS {maintable} (
			event_time TIMESTAMP,
			event_type TEXT,
			product_id INTEGER,
			price NUMERIC,
			user_id NUMERIC,
			user_session TEXT
		);\n""")
		# 個別のテーブル作成
		for file in os.listdir(csv_dir):
			if not file.endswith('.csv'):
				continue
			table_name = file[:-4] # .csvを除く
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

		INSERT INTO {maintable} (event_time, event_type, product_id, price, user_id, user_session)
		SELECT event_time, event_type, product_id, price, user_id, user_session
		FROM {table_name};
		\n""")

	st = os.stat(initsql)
	os.chmod(initsql, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
	print("init.sql生成完了")



if __name__ == '__main__':
	generate_init()