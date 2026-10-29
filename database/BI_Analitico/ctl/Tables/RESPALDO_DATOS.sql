-- Respaldo de filas antes de un UPDATE / DELETE hecho por una migración de datos.
-- Cada fila respaldada se guarda como JSON, así sirve para cualquier tabla.
CREATE TABLE [ctl].[RESPALDO_DATOS]
(
    [ID_RESPALDO]   BIGINT IDENTITY(1,1) NOT NULL,
    [SCRIPT]        VARCHAR(200)   NOT NULL,
    [TABLA]         VARCHAR(256)   NOT NULL,
    [FILA_JSON]     NVARCHAR(MAX)  NOT NULL,
    [FECHA]         DATETIME2(0)   NOT NULL CONSTRAINT [DF_RESPALDO_DATOS_FECHA] DEFAULT (SYSDATETIME()),
    CONSTRAINT [PK_RESPALDO_DATOS] PRIMARY KEY CLUSTERED ([ID_RESPALDO])
);
GO
