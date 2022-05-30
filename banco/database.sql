-- Deletar
	-- Tabelas
        DROP TABLE IF EXISTS encomenda;
-- Criação das tabelas necessária
	-- Tabela das Encomenda
		CREATE TABLE IF NOT EXISTS encomenda(
			id			 	INTEGER PRIMARY KEY AUTOINCREMENT,
			id_user 		INTEGER NOT NULL,
			codigo			TEXT	NOT NULL,
			nome_rastreio	TEXT	NOT NULL,
			dia 			TEXT	NOT NULL,
			informacoes     TEXT 	NOT NULL
		);
-- Criação de index das tabelas
	-- Tabela das encomendas dos clientes;
		CREATE INDEX index_encomenda_id_user 	ON encomenda(id_user);
		CREATE INDEX index_encomenda_codigo		ON encomenda(codigo);
