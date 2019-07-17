from zipfile import ZipFile
from hashlib import sha256
from collections import defaultdict as dd
import requests
import json
import sys
import os
import re

class PTMerger:
    def __init__(self, data_id, input_dir='data', extract_dir='csv', output_dir='output', log_dir='log'):
        self.data_id = data_id
        self.input_dir = input_dir 
        self.extract_dir = extract_dir
        self.output_dir = output_dir
        self.log_dir = log_dir

    def extract(self):
        data_dir = os.path.join(self.input_dir, self.data_id)
        data_ext_dir = os.path.join(self.extract_dir, self.data_id)
        data_log_dir = os.path.join(self.log_dir, self.data_id)

        try:
            os.mkdir(self.extract_dir)
        except FileExistsError:
            print('[-] Extract dir exists already. Skipping creation...')

        try:
            os.mkdir(data_ext_dir)
        except FileExistsError:
            print('[-] Data outdir exists already. Skipping creation...')
        
        try:
            os.mkdir(self.log_dir)
        except FileExistsError:
            print('[-] Logdir exists already. Skipping creation...')

        try:
            os.mkdir(data_log_dir)
        except FileExistsError:
            print('[-] Data logdir exists already. Skipping creation...')

        try:
            os.mkdir(self.output_dir)
        except FileExistsError:
            print('[-] Output dir exists already. Skipping creation...')

        try:
            extract_logfile = os.path.join(self.log_dir, self.data_id, 'extract.log')
            with open(extract_logfile) as f:
                extracted_files = set(map(lambda x: x.rstrip(), f.readlines()))
        except FileNotFoundError:
            extracted_files = []

        extracted_now = []
        for f in os.listdir(data_dir):
            if f in extracted_files:
                continue

            zip_file = os.path.join(data_dir, f)

            try:
                with ZipFile(zip_file) as zip_ref:
                    print('[+] Extract', zip_file, 'to', data_ext_dir)
                    zip_ref.extractall(data_ext_dir)
                    extracted_now.append(f)
            except Exception as e:
                print('[x]', e)

        print('[-] Writing extraction logfile.')
        with open(extract_logfile, 'a+') as f:
            f.write('\n'.join(extracted_now))
                
    def merge(self, remove_csv=False):
        data_output_dir = os.path.join(self.output_dir, self.data_id)
        try:
            os.mkdir(data_output_dir)
        except FileExistsError:
            print('[-] Data output dir exists already. Skipping creation...')

        csv_dir = os.path.join(self.extract_dir, self.data_id)
        schemas = dd(list)
        schemas_map = dict()

        for filename in os.listdir(csv_dir):
            schema_hash = sha256()
            with open(os.path.join(csv_dir, filename), errors='ignore') as f:
                header = f.readline().rstrip().encode('utf-8')
            schema_hash.update(header)
            schema_id = schema_hash.hexdigest()

            schemas[schema_id].append(filename)
            schemas_map[schema_id] = header

        print('[-] Distinct schemas:', len(schemas.keys()))

        def sanitize_schema(x):
            return x.replace(b'"', b'').replace(b' ', b'_')

        for schema_id in schemas:
            outfile_path = os.path.join(data_output_dir, schema_id + '.csv')
            with open(outfile_path, 'wb') as outfile:
                schema_cols = list(map(sanitize_schema, schemas_map[schema_id].split(b';')))
                schema_cols.append(b'FONTE')

                outfile.write(b'"' + b'";"'.join(schema_cols) + b'"\n')

                for filename in schemas[schema_id]:
                    print('[+] Processing:', filename)
                    with open(os.path.join(csv_dir, filename), 'rb') as infile:
                        infile.readline()
                        for line in infile:
                            line = line.rstrip()
                            outfile.write(line + b';"' + filename.encode('utf-8') + b'"\n')

                    if remove_csv:
                        os.remove(os.path.join(csv_dir, filename))

if __name__ == '__main__':
    merger = PTMerger(sys.argv[1])
    merger.extract()
    merger.merge()
