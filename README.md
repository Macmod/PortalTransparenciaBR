# PortalTransparenciaBR
Extrator de dados do portal da transparência do governo brasileiro.
O propósito desse repositório é facilitar o acesso ao conjunto completo de dados do portal da transparência para fins de análise de dados offline. Se o seu propósito for a obtenção de respostas para pequenas consultas nos dados, utilize a [API do portal](http://www.portaltransparencia.gov.br/api-de-dados) ao invés.

## Categorias
As categorias de dados disponíveis são aquelas listadas na seção [Download de Dados](https://www.portaltransparencia.gov.br/download-de-dados/) do portal e são identificadas pelo nome na URL, como `servidores`, `bolsa-familia-pagamentos`, `licitacoes`, etc.

## Download
Dados de uma categoria podem ser baixados com o seguinte comando:
```bash
$ python ptfetcher.py <CATEGORIA>
```

Os dados comprimidos, como disponibilizados no site, serão baixados para o diretório `data`.

## Desagrupamento
O portal oferece dados agrupados por subcategorias, tais como ano, mês e origem. Para desagrupar os dados já baixados, obtendo um CSV único para cada conjunto de CSVs com as mesmas colunas, execute o comando:
```bash
$ python ptmerger.py <CATEGORIA>
```

Os dados extraídos serão inseridos no diretório `csv` e os dados desagrupados serão inseridos no diretório `output`. O diretório `log` serve apenas para registrar os nomes dos arquivos já extraídos para cada categoria, evitando a extração repetida de arquivos. Caso queira extrair a categoria inteira novamente, remova o diretório `log` e re-execute o comando.
