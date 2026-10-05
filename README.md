# Documentazione esercizio docker

## 1. Struttura progetto
1. **Database (`db`)**: Un'istanza MySQL 8.0 che ospita i dati e una tabella di log (`backup_log`) per tracciare lo storico dei backup.
2. **Servizio di Visualizzazione (`visualizzazione`)**: Un'applicazione Python/Flask che espone un'API REST per consultare lo storico dei backup effettuati.
3. **Servizio di Backup (`backup`)**: Un'applicazione Python/Flask che espone un'API REST per generare, comprimere e salvare i dump del database.

## 2. Configurazione dei container
* **Rete (Network)**: È stata creata una rete privata di tipo bridge chiamata `app_network`. Questa scelta permette ai tre container di comunicare tra loro in modo sicuro risolvendo i nomi dei container (es. il servizio Python si collega all'host `db`), senza esporre il database direttamente sulla rete dell'host fisico.
* **Volumi (Volumes)**: Sono stati configurati due volumi per garantire la persistenza dei dati e la condivisione:
    * `db_data`: Montato in `/var/lib/mysql` nel container del database. Garantisce che i dati di MySQL (incluso lo storico dei backup) non vadano persi se il container viene distrutto o riavviato.
    * `shared_backups`: Montato in `/shared_backups` nei container applicativi. Funge da cartella condivisa in cui il servizio di backup salva i file `.zip` generati. 

## 3. Funzionamento dei Servizi REST

Le due applicazioni sono state sviluppate in Python utilizzando il micro-framework Flask.

### Servizio "Backup" (Porta 5001)
* **Endpoint**: `POST /mysqlBackup?fileName=<nome_file>`
* **Flusso logico**:
    1. Riceve la richiesta e legge il parametro `fileName`.
    2. Utilizza il comando di sistema `mysqldump` (installato tramite il pacchetto `default-mysql-client` nel Dockerfile) per estrarre i dati.
    3. Comprime il file `.sql` in un archivio `.zip` utilizzando la libreria nativa `zipfile`.
    4. Salva il file nel volume condiviso `shared_backups`.
    5. Si connette al database MySQL tramite `mysql-connector-python` e inserisce un record nella tabella `backup_log` con il nome del file e il timestamp (generato automaticamente dal DB).
    6. Restituisce all'utente il file `.zip` in download.

### Servizio "Visualizzazione" (Porta 5000)
* **Endpoint**: `GET /viewBackupHistory`
* **Flusso logico**: Si collega al database, esegue una query `SELECT * FROM backup_log` e restituisce i risultati in formato JSON, permettendo all'utente di vedere lo storico di tutti i backup effettuati.
