-- 1. Criar o utilizador (Role) com a password definida
-- Nota: Se o utilizador já existir, este comando falhará. 
-- Podes usar 'DROP ROLE IF EXISTS blog;' antes se quiseres fazer um reset.
CREATE USER blog WITH PASSWORD '1234';

-- 2. Criar a Base de Dados definindo o utilizador "blog" como dono (owner)
-- Isso automaticamente dá-lhe muitos privilégios de gestão.
CREATE DATABASE blog OWNER blog;

-- 3. Conceder privilégios de ligação e gestão na base de dados
GRANT ALL PRIVILEGES ON DATABASE blog TO blog;

-- 4. Ajustar permissões no esquema 'public' 
-- (Necessário para versões recentes do PostgreSQL como a 15 e 16)
\c blog
GRANT ALL ON SCHEMA public TO blog;
ALTER SCHEMA public OWNER TO blog;

-- Feedback visual de sucesso
SELECT 'Configuração da base de dados blog concluída com sucesso!' AS status;


-- testtar a partir da consola bash do ubuntu
PGPASSWORD='1234' psql -h localhost -U blog -d blog -c "SELECT 1"



