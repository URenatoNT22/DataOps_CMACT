-- Control de migraciones de datos: qué script de la carpeta migraciones/ ya se ejecutó en esta base.
-- Lo usa el pipeline para ejecutar cada script UNA sola vez. No modificar a mano.
CREATE TABLE [ctl].[SCRIPTS_EJECUTADOS]
(
    [NOMBRE]          VARCHAR(200)  NOT NULL,
    [HASH_SHA256]     CHAR(64)      NOT NULL,
    [TIPO]            VARCHAR(20)   NOT NULL,
    [DESCRIPCION]     NVARCHAR(500) NULL,
    [FILAS_AFECTADAS] INT           NULL,
    [VERSION]         VARCHAR(30)   NULL,
    [EJECUTADO_POR]   VARCHAR(100)  NOT NULL,
    [URL_EJECUCION]   VARCHAR(400)  NULL,
    [FECHA_EJECUCION] DATETIME2(0)  NOT NULL CONSTRAINT [DF_SCRIPTS_EJECUTADOS_FECHA] DEFAULT (SYSDATETIME()),
    CONSTRAINT [PK_SCRIPTS_EJECUTADOS] PRIMARY KEY CLUSTERED ([NOMBRE])
);
GO
