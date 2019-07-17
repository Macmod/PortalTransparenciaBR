from collections import defaultdict as dd
import requests
import json
import sys
import os
import re

class PTFetcher:
    BASE_URL = 'http://www.portaltransparencia.gov.br/download-de-dados/'
    MODES = [
        b'DIA', b'MES', b'ANO_MES_DIA', b'ANO_MES_ORIGEM',
        b'ANO_MES', b'ANO', b'ORIGEM_ANO_MES_DIA', b'UNICO'
    ]

    def __init__(self, data_id):
        self.data_id = data_id
        self.data, self.mode = self.get_available_data()
        
    def get_available_data(self):
        url = PTFetcher.BASE_URL + '/' + self.data_id
        download_page = requests.get(url)

        files_text = re.findall(rb'arquivos.push\(([^)]+)\)', download_page.content)
        if not files_text:
            print('Available data not found.')
            return False

        mode = re.search(
            rb'DownloadPlanilhas\("[^"]+", arquivos, "([^)]+)"',
            download_page.content
        )

        if not mode:
            print('Mode not found.')
            return False

        mode = mode.group(1)

        files = map(lambda x: self.get_link(json.loads(x), mode), files_text)
        return list(files), mode

    def get_link(self, metadata, mode):
        if mode == b'DIA':
            link_parts = [metadata['ano'], metadata['mes'], metadata['dia']]
        elif mode == b'MES':
            link_parts = [metadata['ano'], metadata['mes']]
        elif mode == b'ANO_MES_DIA':
            link_parts = [metadata['ano'], metadata['mes'], metadata['dia']]
        elif mode == b'ANO_MES_ORIGEM':
            link_parts = [metadata['ano'], metadata['mes'], '_', metadata['origem']]
        elif mode == b'ANO_MES':
            link_parts = [metadata['ano'], metadata['mes']]
        elif mode == b'ANO':
            link_parts = [metadata['ano']]
        elif mode == b'ORIGEM_ANO_MES_DIA':
            link_parts = [metadata['ano'], metadata['mes'], metadata['dia'], '_', metadata['origem']]
        elif mode == b'UNICO':
            link_parts = ['UNICO']
        else:
            # Last try
            link_parts = metadata.values()

        return ''.join(link_parts)

    def fetch(self, download_dir='data'):
        data_dir = os.path.join(download_dir, self.data_id)
        try:
            os.mkdir(download_dir)
        except FileExistsError as e:
            pass

        try:
            os.mkdir(data_dir)
        except FileExistsError as e:
            print(str(e))

        available_info = fetcher.get_available_data()
        if not available_info:
            return None

        available_data, mode = available_info
        for link_name in available_data:
            file_url = PTFetcher.BASE_URL + self.data_id + '/' + link_name
            print('<=', file_url)

            outfile = os.path.join(data_dir, link_name)
            if os.path.isfile(outfile):
                print('File', outfile, 'exists already. Skipping...')
                continue

            r = requests.get(file_url, stream=True)
            r.raise_for_status()

            with open(outfile, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk:
                        f.write(chunk)

if __name__ == '__main__':
    fetcher = PTFetcher(sys.argv[1])
    print(fetcher.fetch())
