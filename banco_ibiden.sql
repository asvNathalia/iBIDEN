CREATE DATABASE IBIDEN;

USE IBIDEN;
CREATE TABLE usuario_ibiden(
	usu_id INT IDENTITY,
	usu_nome VARCHAR (150) NOT NULL,
	usu_email VARCHAR (150) NOT NULL UNIQUE, 
	usu_pass VARCHAR (10) NOT NULL,
	estado INT NOT NULL -- 1 = ATIVO // 0 = INATIVO
);


INSERT INTO usuario VALUES ('Nathalia Viana', 'nathalia@gmail.com', '123456', 1);
INSERT INTO usuario VALUES ('Nayra Alencar', 'nayra@gmail.com', '123456', 1);
select * from usuario