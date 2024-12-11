import os
import stat

csv_dir = "./subject/item"
initsql = "./subject/item/init.sql"

def generate_init():
	with open(initsql, 'w') as f:
		for file in os.listdir(csv_dir):
			if not file.endswith('.csv'):
				continue
			table_name = file[:-4] # .csvを除く
			# print(table_name)
			csv_path = f"/docker-entrypoint-initdb.d/{file}"

			f.write(f"""
			CREATE TABLE IF NOT EXISTS {table_name} (
				product_id INTEGER,
				category_id DECIMAL,
				category_code VARCHAR,
				brand VARCHAR
			);

			COPY {table_name}(product_id, category_id, category_code, brand)
			FROM '{csv_path}'
			DELIMITER ','
			CSV HEADER;
			\n""")
	st = os.stat(initsql)
	os.chmod(initsql, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
	print("init.sql生成完了")


if __name__ == '__main__':
	generate_init()