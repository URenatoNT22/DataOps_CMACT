-- Bitácora de ejecución de los procesos de carga de tablones.
CREATE TABLE [ctl].[BITACORA_CARGA]
(
    [ID_BITACORA] BIGINT IDENTITY(1,1) NOT NULL,
    [PROCESO] VARCHAR(128) NOT NULL,
    [FECHA_CORTE] DATE NULL,
    [INICIO] DATETIME2(0) NOT NULL,
    [FIN] DATETIME2(0) NULL,
    [ESTADO] VARCHAR(10) NOT NULL,
    [FILAS] INT NULL,
    [MENSAJE] NVARCHAR(4000) NULL,
    [USUARIO] NVARCHAR(128) NOT NULL CONSTRAINT [DF_BITACORA_CARGA_USUARIO] DEFAULT (SUSER_SNAME()),
    CONSTRAINT [PK_BITACORA_CARGA] PRIMARY KEY CLUSTERED ([ID_BITACORA])
);
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Bitácora de ejecución de los procesos de carga de tablones.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Identificador de la ejecución.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'ID_BITACORA';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Proceso ejecutado (esquema.procedimiento).',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'PROCESO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fecha de corte procesada.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'FECHA_CORTE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Inicio de la ejecución.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'INICIO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Fin de la ejecución.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'FIN';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Estado: EN_CURSO, OK, ERROR.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'ESTADO';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Filas cargadas.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'FILAS';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Mensaje de error, si lo hubo.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'MENSAJE';
GO
EXEC sys.sp_addextendedproperty @name = N'MS_Description', @value = N'Login que ejecutó el proceso.',
    @level0type = N'SCHEMA', @level0name = N'ctl', @level1type = N'TABLE', @level1name = N'BITACORA_CARGA',
    @level2type = N'COLUMN', @level2name = N'USUARIO';
GO
