pip install spacy -t .
python -m spacy download es_dep_news_trf -t .

--> con el -t . se instala en el directorio actual y asi puedo generar el zip y subirlo a layers

PowerShell> Compress-Archive -Path * -DestinationPath es_dep_news_trf.zip


