# KrishiParampara

A Flask and MySQL 8.0 project for documenting traditional Indian agriculture and managing farms, crops, cultivation, harvests, and seed inventory. The project has 13 application tables and 329 attributes.

The public catalogue exposes crops, seed varieties, fertilizer entries, and public knowledge records. Operator sign-in unlocks the dashboard and editing. All demo farms, growers, accessions, measured values, and knowledge entries are fictional. Crop names are real, and catalogue classifications of region and season are illustrative.

## Windows and VS Code

1. Install Python 3.12, VS Code with the Python extension, and Docker Desktop with Linux containers. Open this repository in VS Code and use its PowerShell terminal.
2. Start a disposable MySQL 8.0 database. The following credentials are for local demonstrations only. Docker binds the database to loopback.

   ```powershell
   docker run -d --name kp-mysql -p 127.0.0.1:3307:3306 -e MYSQL_RANDOM_ROOT_PASSWORD=yes -e MYSQL_DATABASE=krishiparampara -e MYSQL_USER=krishi -e MYSQL_PASSWORD=local-db-demo mysql:8.0 --skip-log-bin
   ```

   Wait for a successful login before installing. PowerShell prompts for the database password.

   ```powershell
   docker exec -it kp-mysql mysql -h 127.0.0.1 -u krishi -p -D krishiparampara -e "SELECT VERSION();"
   ```

   With an existing MySQL 8.0.16+ server, have its administrator create an empty UTF-8 database and provide a user with DDL, view, trigger, and routine permissions for installation. On a binary-logged server the administrator may need to install the trigger. The disposable Docker command disables binary logging for the classroom instance.

3. Create a virtual environment and install dependencies. Select `.venv\Scripts\python.exe` in **Python: Select Interpreter**.

   ```powershell
   py -3.12 -m venv .venv
   $py = ".\.venv\Scripts\python.exe"
   & $py -m pip install -r requirements.txt
   $env:DB_HOST = "127.0.0.1"
   $env:DB_PORT = "3307"
   $env:DB_NAME = "krishiparampara"
   $env:DB_USER = "krishi"
   $env:DB_PASSWORD = "local-db-demo"
   $env:APP_PASSWORD = "local-operator-demo"
   $env:FLASK_SECRET_KEY = (& $py -c "import secrets; print(secrets.token_hex(32))")
   & $py -m database.install
   & $py -m database.validate_schema
   & $py -m database.seed_data
   & $py -m flask --app app run --port 8000
   ```

4. Open `http://127.0.0.1:8000`. Use **Operator sign in** with `APP_PASSWORD`. In VS Code you can debug Flask using the installed interpreter and the same environment variables. For Bash, use `python3.12 -m venv .venv`, run `source .venv/bin/activate`, and set credentials with `export NAME=value`. The Python module commands are the same.

On later runs, start an existing stopped container with `docker start kp-mysql`, set the environment variables, and run Flask. Bootstrap and Chart.js are bundled locally. The installer and demo seeder each expect an empty database and refuse to overwrite existing data. MySQL DDL commits implicitly, so if installation fails partway, diagnose it and use a new empty database to try again.

## Demonstration and tests

Open the dashboard, add or edit a record, filter the crop catalogue, and review the harvest report or download its CSV. To demonstrate a transaction, open **Seed Storage → Allocate seed**, pick an available batch, choose a sowing date within the batch's storage window, and submit a new cultivation code. The seed quantity and cultivation change together. Open the batch to inspect its quantity audit. To demonstrate rollback, reuse the same cultivation code and verify the quantity and audit are unchanged.

Run tests against a disposable, freshly seeded database with the same environment variables.

```powershell
& $py -m pytest -q
```

Run `database/queries.sql` in MySQL Workbench against that database for the full SQL demonstration. The **DBMS Demonstration** page runs a smaller allowlisted set interactively.

## Project documentation

- [Relational schema and attribute dictionary](docs/relational_schema.md)
- [Complete and presentation Mermaid ER diagrams](docs/er_diagram.md)
- [Functional dependencies, keys and normalization](docs/normalization.md)
- [Project report and screenshot checklist](docs/project_report.md)
- [Viva preparation](docs/viva_questions.md)

The app targets a local, single-operator classroom setup. Use synthetic data for demos. Real deployment requires individual accounts, HTTPS, separate migration and runtime database privileges, backups, and an agreed policy for farmer data and community knowledge.
